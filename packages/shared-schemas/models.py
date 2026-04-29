"""
Shared Pydantic schemas — the common input/output contract used by every simulator.
Import these in both the API gateway and all simulator services.
"""
from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

# ──────────────────────────────────────────────
# Receiver/User-Type Modes
# ──────────────────────────────────────────────

class ReceiverMode(str, Enum):
    BEGINNER   = "beginner"
    STUDENT    = "student"
    RESEARCHER = "researcher"
    ENGINEER   = "engineer"
    INSTRUCTOR = "instructor"


# ──────────────────────────────────────────────
# Research Reference Models
# ──────────────────────────────────────────────

class ReferenceEntry(BaseModel):
    title: str
    authors: str | None = None
    year: int | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    url: str | None = None
    relevance: str | None = None


# ──────────────────────────────────────────────
# Formula Card Models
# ──────────────────────────────────────────────

class FormulaCard(BaseModel):
    title: str
    formula: str
    explanation: str
    variables: dict[str, str] = Field(default_factory=dict)
    example: str | None = None


# ──────────────────────────────────────────────
# Hover Annotation Models
# ──────────────────────────────────────────────

class HoverAnnotation(BaseModel):
    target: str
    definition: str
    formula_meaning: str | None = None
    example: str | None = None
    common_mistake: str | None = None
    reference_label: str | None = None


# ──────────────────────────────────────────────
# Step Explanation Models
# ──────────────────────────────────────────────

class StepExplanation(BaseModel):
    step_id: str
    stage: str
    title: str
    description: str
    formula: str | None = None
    input_preview: Any | None = None
    output_preview: Any | None = None
    why_it_matters: str | None = None
    visualization_type: str | None = None


# ──────────────────────────────────────────────
# Receiver Mode Explanation
# ──────────────────────────────────────────────

class ReceiverModeExplanation(BaseModel):
    mode: ReceiverMode
    explanation: str
    technical_detail: str | None = None
    teaching_notes: str | None = None


# ──────────────────────────────────────────────
# Teaching Notes Model
# ──────────────────────────────────────────────

class TeachingNotes(BaseModel):
    summary: str | None = None
    quiz_questions: list[str] = Field(default_factory=list)
    classroom_demo_tips: list[str] = Field(default_factory=list)
    common_misconceptions: list[str] = Field(default_factory=list)


# ──────────────────────────────────────────────
# Demo Initialization Metadata
# ──────────────────────────────────────────────

class DemoMetadata(BaseModel):
    demo_input: dict[str, Any] = Field(default_factory=dict)
    auto_parameters: dict[str, Any] = Field(default_factory=dict)
    expected_output_preview: dict[str, Any] = Field(default_factory=dict)
    beginner_explanation: str | None = None
    advanced_explanation: str | None = None
    formula_cards: list[FormulaCard] = Field(default_factory=list)
    step_explanations: list[StepExplanation] = Field(default_factory=list)
    hover_annotations: list[HoverAnnotation] = Field(default_factory=list)
    references: list[ReferenceEntry] = Field(default_factory=list)
    receiver_mode_explanations: list[ReceiverModeExplanation] = Field(default_factory=list)
    research_context: str | None = None
    teaching_notes: TeachingNotes | None = None


# ──────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────

class AlgorithmID(str, Enum):
    TOKENIZATION       = "tokenization"
    TFIDF              = "tfidf"
    WORD_EMBEDDINGS    = "word_embeddings"
    NAIVE_BAYES        = "naive_bayes"
    SVM                = "svm"
    LSTM               = "lstm"
    RAKE               = "rake"
    TEXTRANK           = "textrank"
    FASTTEXT           = "fasttext"
    TRANSFORMER_ATTN   = "transformer_attention"
    BERT               = "bert"
    GPT                = "gpt"
    T5                 = "t5"


class SimulatorMode(str, Enum):
    LEARNING    = "learning"
    EXPERIMENT  = "experiment"
    ASSESSMENT  = "assessment"
    ADMIN       = "admin"


class TraceLevel(str, Enum):
    NONE    = "none"
    SUMMARY = "summary"
    FULL    = "full"


class RunStatus(str, Enum):
    QUEUED     = "queued"
    RUNNING    = "running"
    SUCCESS    = "success"
    WARNING    = "warning"
    FAILED     = "failed"


# ──────────────────────────────────────────────
# Common Input
# ──────────────────────────────────────────────

class DocumentInput(BaseModel):
    id: str
    text: str
    label: str | None = None


class RunRequest(BaseModel):
    experiment_id: str | None = None
    algorithm_id: AlgorithmID
    mode: SimulatorMode = SimulatorMode.LEARNING
    text: str | None = None
    documents: list[DocumentInput] | None = None
    labels: list[str] | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    trace_level: TraceLevel = TraceLevel.SUMMARY
    language: str = "en"

    @model_validator(mode="after")
    def require_text_or_documents(self) -> "RunRequest":
        if self.text is None and not self.documents:
            raise ValueError("Provide either `text` or `documents`.")
        return self

    def input_fingerprint(self) -> str:
        payload = {
            "algorithm_id": self.algorithm_id,
            "text": self.text,
            "documents": [d.model_dump() for d in self.documents] if self.documents else None,
            "parameters": self.parameters,
        }
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return "sha256:" + hashlib.sha256(raw.encode()).hexdigest()[:16]


# ──────────────────────────────────────────────
# Common Output
# ──────────────────────────────────────────────

class WarningEntry(BaseModel):
    code: str
    message: str
    field: str | None = None
    suggestion: str | None = None


class MetricsOutput(BaseModel):
    runtime_ms: float = 0.0
    token_count: int | None = None
    memory_mb: float | None = None
    model_version: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class VisualizationSpec(BaseModel):
    """
    Chart-ready data payload consumed by the frontend.
    `type` is one of: heatmap | bar | scatter | graph | table | timeline | tree
    `data` is the raw spec payload (typed per algorithm in visualization-specs package).
    """
    type: str
    title: str
    data: Any
    config: dict[str, Any] = Field(default_factory=dict)


class ExportLink(BaseModel):
    format: str   # json | csv | report
    url: str
    checksum: str | None = None


class RunResponse(BaseModel):
    run_id: str
    status: RunStatus
    algorithm_id: AlgorithmID
    algorithm_version: str
    input_fingerprint: str
    result: dict[str, Any]
    trace: dict[str, Any] | list[Any] = Field(default_factory=dict)
    visualization_specs: list[VisualizationSpec] = Field(default_factory=list)
    metrics: MetricsOutput = Field(default_factory=MetricsOutput)
    warnings: list[WarningEntry] = Field(default_factory=list)
    export_links: list[ExportLink] = Field(default_factory=list)
    demo_input: dict[str, Any] = Field(default_factory=dict)
    auto_parameters: dict[str, Any] = Field(default_factory=dict)
    step_explanations: list[StepExplanation] = Field(default_factory=list)
    formula_cards: list[FormulaCard] = Field(default_factory=list)
    hover_annotations: list[HoverAnnotation] = Field(default_factory=list)
    references: list[ReferenceEntry] = Field(default_factory=list)
    receiver_mode_explanations: list[ReceiverModeExplanation] = Field(default_factory=list)
    research_context: str | None = None
    teaching_notes: TeachingNotes | None = None


# ──────────────────────────────────────────────
# Algorithm catalog entry
# ──────────────────────────────────────────────

class ParameterSchema(BaseModel):
    name: str
    type: str           # string | int | float | bool | array | object
    default: Any
    description: str
    min: Any | None = None
    max: Any | None = None
    options: list[Any] | None = None


class AlgorithmEntry(BaseModel):
    id: AlgorithmID
    name: str
    family: str         # preprocessing | vectorization | classification | extraction | sequence | transformer
    description: str
    use_cases: list[str]
    input_types: list[str]
    parameter_schema: list[ParameterSchema]
    supported_modes: list[SimulatorMode]
    complexity: str
    requires_gpu: bool = False
    is_async: bool = False
    demo_metadata: DemoMetadata | None = None
