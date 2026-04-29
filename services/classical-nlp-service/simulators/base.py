"""
Base simulator interface. Every algorithm must implement this contract.
Mirrors the interface defined in SRS §12.2.
"""
from __future__ import annotations

import time
import uuid
from abc import ABC, abstractmethod
from typing import Any

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages"))

from shared_schemas import (
    DemoMetadata,
    MetricsOutput,
    RunRequest,
    RunResponse,
    RunStatus,
    VisualizationSpec,
    WarningEntry,
)


class BaseSimulator(ABC):
    VERSION: str = "0.0.0"
    ALGORITHM_ID: str = ""
    DEMO_METADATA: DemoMetadata | None = None

    def execute(self, request: RunRequest) -> RunResponse:
        """Orchestrates the full pipeline: validate → preprocess → run → trace → visualize → serialize."""
        t_start = time.perf_counter()
        warnings: list[WarningEntry] = []

        # 1. validate
        val_warnings = self.validate(request)
        warnings.extend(val_warnings)

        # 2. preprocess
        preprocessed = self.preprocess(request)

        # 3. run algorithm
        raw_result = self.run(preprocessed, request)

        # 4. trace (depth controlled by trace_level)
        trace = self.trace(preprocessed, raw_result, request)

        # 5. visualize
        viz_specs = self.visualize(trace, raw_result, request)

        # 6. serialize
        result_dict = self.serialize_result(raw_result)

        runtime_ms = (time.perf_counter() - t_start) * 1000

        demo = self.DEMO_METADATA

        return RunResponse(
            run_id=str(uuid.uuid4()),
            status=RunStatus.WARNING if warnings else RunStatus.SUCCESS,
            algorithm_id=request.algorithm_id,
            algorithm_version=f"{self.ALGORITHM_ID}-v{self.VERSION}",
            input_fingerprint=request.input_fingerprint(),
            result=result_dict,
            trace=trace,
            visualization_specs=viz_specs,
            metrics=MetricsOutput(runtime_ms=round(runtime_ms, 2)),
            warnings=warnings,
            demo_input=demo.demo_input if demo else {},
            auto_parameters=demo.auto_parameters if demo else {},
            step_explanations=demo.step_explanations if demo else [],
            formula_cards=demo.formula_cards if demo else [],
            hover_annotations=demo.hover_annotations if demo else [],
            references=demo.references if demo else [],
            receiver_mode_explanations=demo.receiver_mode_explanations if demo else [],
            research_context=demo.research_context if demo else None,
            teaching_notes=demo.teaching_notes if demo else None,
        )

    @abstractmethod
    def validate(self, request: RunRequest) -> list[WarningEntry]:
        """Return warnings without halting. Raise ValueError for hard errors."""
        ...

    @abstractmethod
    def preprocess(self, request: RunRequest) -> Any:
        """Transform raw input into the form the algorithm consumes."""
        ...

    @abstractmethod
    def run(self, preprocessed: Any, request: RunRequest) -> Any:
        """Execute the algorithm and return raw result data."""
        ...

    @abstractmethod
    def trace(self, preprocessed: Any, result: Any, request: RunRequest) -> dict[str, Any]:
        """Build the step-by-step explanation artifact. Depth varies by trace_level."""
        ...

    @abstractmethod
    def visualize(self, trace: dict[str, Any], result: Any, request: RunRequest) -> list[VisualizationSpec]:
        """Return chart-ready VisualizationSpec objects for the frontend."""
        ...

    @abstractmethod
    def serialize_result(self, result: Any) -> dict[str, Any]:
        """Flatten the algorithm result into a JSON-serializable dict."""
        ...

    def get_demo_metadata(self) -> DemoMetadata | None:
        """Return demo initialization metadata for this simulator."""
        return self.DEMO_METADATA
