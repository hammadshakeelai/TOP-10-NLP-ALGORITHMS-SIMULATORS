"""
BERT Simulator — BE-001 through BE-004.

Uses HuggingFace transformers with a small BERT model (bert-base-uncased).
Requires: pip install transformers torch

Supported tasks (selectable via parameters.task):
  mlm           — masked language modeling (default)
  sentiment     — text classification (distilbert-sst2)
  ner           — named entity recognition (bert-base-NER)
  qa            — extractive question answering
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import BaseSimulator

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages"))
from shared_schemas import RunRequest, TraceLevel, VisualizationSpec, WarningEntry

from .demo_metadata import TRANSFORMER_DEMO_METADATA

_PIPELINE_CACHE: dict[str, Any] = {}


def get_pipeline(task: str, model: str | None = None):
    key = f"{task}:{model}"
    if key not in _PIPELINE_CACHE:
        from transformers import pipeline
        kwargs: dict[str, Any] = {"task": task}
        if model:
            kwargs["model"] = model
        _PIPELINE_CACHE[key] = pipeline(**kwargs)
    return _PIPELINE_CACHE[key]


@dataclass
class BERTResult:
    task: str
    input_text: str
    subword_tokens: list[str]
    predictions: list[dict[str, Any]]
    attention_maps: list[list[list[float]]] | None  # [layer][head][seq x seq]
    contextual_embeddings: list[list[float]] | None


class BERTSimulator(BaseSimulator):
    VERSION = "1.0.0"
    ALGORITHM_ID = "bert"
    DEMO_METADATA = TRANSFORMER_DEMO_METADATA.get("bert")

    TASK_MODELS = {
        "mlm": ("fill-mask", "bert-base-uncased"),
        "sentiment": ("text-classification", "distilbert-base-uncased-finetuned-sst-2-english"),
        "ner": ("ner", "dbmdz/bert-large-cased-finetuned-conll03-english"),
        "qa": ("question-answering", "distilbert-base-cased-distilled-squad"),
    }

    def validate(self, request: RunRequest) -> list[WarningEntry]:
        warnings = []
        task = request.parameters.get("task", "mlm")
        if task not in self.TASK_MODELS:
            warnings.append(WarningEntry(
                code="UNKNOWN_TASK",
                message=f"task '{task}' not supported. Choose from: {list(self.TASK_MODELS.keys())}.",
                field="parameters.task",
            ))
        text = request.text or ""
        if task == "mlm" and "[MASK]" not in text and "<mask>" not in text.lower():
            warnings.append(WarningEntry(
                code="NO_MASK_TOKEN",
                message="MLM task expects at least one [MASK] token in the input text.",
                field="text",
                suggestion="Add [MASK] where you want BERT to predict a word.",
            ))
        if len(text.split()) > 512:
            warnings.append(WarningEntry(
                code="SEQUENCE_TOO_LONG",
                message="Input exceeds 512 tokens; BERT will truncate automatically.",
            ))
        return warnings

    def preprocess(self, request: RunRequest) -> dict[str, Any]:
        return {"text": request.text or "", "params": request.parameters}

    def run(self, preprocessed: dict[str, Any], request: RunRequest) -> BERTResult:
        text: str = preprocessed["text"]
        params = preprocessed["params"]
        task: str = params.get("task", "mlm")
        top_k: int = params.get("top_k", 5)

        try:
            pipeline_task, model_name = self.TASK_MODELS.get(task, self.TASK_MODELS["mlm"])
            custom_model = params.get("model_checkpoint")
            model = custom_model or model_name
            pipe = get_pipeline(pipeline_task, model)

            if task == "mlm":
                raw = pipe(text, top_k=top_k)
                predictions = raw if isinstance(raw[0], dict) else raw[0]
                predictions = [
                    {"token": p["token_str"], "score": round(p["score"], 4), "sequence": p.get("sequence", "")}
                    for p in predictions
                ]
                subword_tokens = self._tokenize(text, model)
            elif task == "sentiment":
                raw = pipe(text, top_k=None)
                predictions = [{"label": p["label"], "score": round(p["score"], 4)} for p in raw]
                subword_tokens = self._tokenize(text, model)
            elif task == "ner":
                raw = pipe(text, aggregation_strategy="simple")
                predictions = [
                    {"entity": p["entity_group"], "word": p["word"],
                     "score": round(p["score"], 4), "start": p["start"], "end": p["end"]}
                    for p in raw
                ]
                subword_tokens = self._tokenize(text, model)
            elif task == "qa":
                context = params.get("context", text)
                question = params.get("question", text)
                raw = pipe(question=question, context=context)
                predictions = [{"answer": raw["answer"], "score": round(raw["score"], 4),
                                "start": raw["start"], "end": raw["end"]}]
                subword_tokens = self._tokenize(context, model)
            else:
                predictions = []
                subword_tokens = []

        except Exception as e:
            return BERTResult(
                task=task, input_text=text,
                subword_tokens=[], predictions=[{"error": str(e)}],
                attention_maps=None, contextual_embeddings=None,
            )

        return BERTResult(
            task=task, input_text=text,
            subword_tokens=subword_tokens,
            predictions=predictions,
            attention_maps=None,   # requires output_attentions=True; add in experiment mode
            contextual_embeddings=None,
        )

    def _tokenize(self, text: str, model_name: str) -> list[str]:
        try:
            from transformers import AutoTokenizer
            tok = AutoTokenizer.from_pretrained(model_name)
            return tok.tokenize(text)
        except Exception:
            return text.split()

    def trace(self, preprocessed: Any, result: BERTResult, request: RunRequest) -> dict[str, Any]:
        if request.trace_level == TraceLevel.NONE:
            return {}
        base: dict[str, Any] = {
            "task": result.task,
            "subword_token_count": len(result.subword_tokens),
            "predictions": result.predictions,
        }
        if request.trace_level == TraceLevel.SUMMARY:
            return base
        return {
            **base,
            "subword_tokens": result.subword_tokens,
        }

    def visualize(self, trace: dict[str, Any], result: BERTResult, request: RunRequest) -> list[VisualizationSpec]:
        specs: list[VisualizationSpec] = []

        if result.task == "mlm":
            specs.append(VisualizationSpec(
                type="bar",
                title="Masked Token Predictions",
                data=[{"token": p["token"], "score": p["score"]} for p in result.predictions],
                config={"x": "token", "y": "score", "color": "#6366f1"},
            ))

        if result.task == "sentiment":
            specs.append(VisualizationSpec(
                type="bar",
                title="Sentiment Probabilities",
                data=[{"label": p["label"], "score": p["score"]} for p in result.predictions],
                config={"x": "label", "y": "score", "color": "#10b981"},
            ))

        if result.task == "ner":
            specs.append(VisualizationSpec(
                type="table",
                title="Named Entities",
                data=result.predictions,
            ))

        # Subword token table
        specs.append(VisualizationSpec(
            type="table",
            title="WordPiece Subword Tokens",
            data=[{"index": i, "token": t} for i, t in enumerate(result.subword_tokens)],
        ))

        return specs

    def serialize_result(self, result: BERTResult) -> dict[str, Any]:
        return {
            "task": result.task,
            "predictions": result.predictions,
            "subword_token_count": len(result.subword_tokens),
        }
