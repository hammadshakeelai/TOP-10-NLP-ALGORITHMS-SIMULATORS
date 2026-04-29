from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_LEGACY_MODELS = Path(__file__).resolve().parent.parent / "shared-schemas" / "models.py"
_SPEC = importlib.util.spec_from_file_location("_shared_schemas_legacy_models", _LEGACY_MODELS)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Unable to load shared schemas from {_LEGACY_MODELS}")

_MODULE = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _MODULE
_SPEC.loader.exec_module(_MODULE)

AlgorithmEntry = _MODULE.AlgorithmEntry
AlgorithmID = _MODULE.AlgorithmID
DemoMetadata = _MODULE.DemoMetadata
DocumentInput = _MODULE.DocumentInput
ExportLink = _MODULE.ExportLink
FormulaCard = _MODULE.FormulaCard
HoverAnnotation = _MODULE.HoverAnnotation
MetricsOutput = _MODULE.MetricsOutput
ParameterSchema = _MODULE.ParameterSchema
ReceiverMode = _MODULE.ReceiverMode
ReceiverModeExplanation = _MODULE.ReceiverModeExplanation
ReferenceEntry = _MODULE.ReferenceEntry
RunRequest = _MODULE.RunRequest
RunResponse = _MODULE.RunResponse
RunStatus = _MODULE.RunStatus
SimulatorMode = _MODULE.SimulatorMode
StepExplanation = _MODULE.StepExplanation
TeachingNotes = _MODULE.TeachingNotes
TraceLevel = _MODULE.TraceLevel
VisualizationSpec = _MODULE.VisualizationSpec
WarningEntry = _MODULE.WarningEntry

__all__ = [
    "AlgorithmEntry",
    "AlgorithmID",
    "DemoMetadata",
    "DocumentInput",
    "ExportLink",
    "FormulaCard",
    "HoverAnnotation",
    "MetricsOutput",
    "ParameterSchema",
    "ReceiverMode",
    "ReceiverModeExplanation",
    "ReferenceEntry",
    "RunRequest",
    "RunResponse",
    "RunStatus",
    "SimulatorMode",
    "StepExplanation",
    "TeachingNotes",
    "TraceLevel",
    "VisualizationSpec",
    "WarningEntry",
]
