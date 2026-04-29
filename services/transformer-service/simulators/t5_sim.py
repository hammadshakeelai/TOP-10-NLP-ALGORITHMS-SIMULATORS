"""
T5 / Seq2Seq Transformer Simulator — T5-001 through T5-004.

Uses HuggingFace t5-small by default.
Task framing: T5 uses a text-to-text format — prefix the input with the task.

Supported task prefixes:
  summarize:   <text>
  translate English to French:  <text>
  question: <q> context: <ctx>   (QA)
  paraphrase: <text>
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import BaseSimulator

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages"))
from shared_schemas import RunRequest, TraceLevel, VisualizationSpec, WarningEntry

from .demo_metadata import TRANSFORMER_DEMO_METADATA

_T5_CACHE: dict[str, Any] = {}


def get_t5(model_name: str):
    if model_name not in _T5_CACHE:
        from transformers import T5ForConditionalGeneration, T5Tokenizer
        tokenizer = T5Tokenizer.from_pretrained(model_name)
        model = T5ForConditionalGeneration.from_pretrained(model_name)
        _T5_CACHE[model_name] = (tokenizer, model)
    return _T5_CACHE[model_name]


@dataclass
class T5Result:
    task_prefix: str
    source_text: str
    source_tokens: list[str]
    target_text: str
    target_tokens: list[str]
    beam_candidates: list[dict[str, Any]]
    parameters_used: dict[str, Any]


class T5Simulator(BaseSimulator):
    VERSION = "1.0.0"
    ALGORITHM_ID = "t5"
    DEMO_METADATA = TRANSFORMER_DEMO_METADATA.get("t5")

    SUPPORTED_PREFIXES = [
        "summarize:",
        "translate English to French:",
        "translate English to German:",
        "question:",
        "paraphrase:",
    ]

    def validate(self, request: RunRequest) -> list[WarningEntry]:
        warnings = []
        text = request.text or ""
        task_prefix = request.parameters.get("task_prefix", "summarize:")
        if not any(text.lower().startswith(p.lower()) for p in self.SUPPORTED_PREFIXES):
            warnings.append(WarningEntry(
                code="MISSING_TASK_PREFIX",
                message=f"Input does not start with a recognized task prefix: {self.SUPPORTED_PREFIXES}",
                suggestion=f"Prepend '{task_prefix}' to your input text.",
                field="text",
            ))
        if len(text.split()) > 512:
            warnings.append(WarningEntry(
                code="SOURCE_TOO_LONG",
                message="Source text exceeds 512 tokens; T5 will truncate.",
            ))
        return warnings

    def preprocess(self, request: RunRequest) -> dict[str, Any]:
        text = request.text or ""
        task_prefix = request.parameters.get("task_prefix", "summarize:")
        # Auto-prepend prefix if missing
        full_input = text if any(text.lower().startswith(p.lower()) for p in self.SUPPORTED_PREFIXES) else f"{task_prefix} {text}"
        return {"full_input": full_input, "params": request.parameters}

    def run(self, preprocessed: dict[str, Any], request: RunRequest) -> T5Result:
        full_input: str = preprocessed["full_input"]
        params = preprocessed["params"]

        model_name: str = params.get("model_checkpoint", "t5-small")
        num_beams: int = int(params.get("num_beams", 4))
        max_output_len: int = int(params.get("max_output_length", 128))
        length_penalty: float = float(params.get("length_penalty", 1.0))
        num_candidates: int = min(int(params.get("num_return_sequences", 3)), num_beams)

        # Extract task prefix
        task_prefix = ""
        for p in self.SUPPORTED_PREFIXES:
            if full_input.lower().startswith(p.lower()):
                task_prefix = p
                break

        try:
            tokenizer, model = get_t5(model_name)
            inputs = tokenizer(full_input, return_tensors="pt", truncation=True, max_length=512)
            source_tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])

            outputs = model.generate(
                **inputs,
                num_beams=num_beams,
                max_length=max_output_len,
                length_penalty=length_penalty,
                num_return_sequences=num_candidates,
                early_stopping=True,
            )

            candidates: list[dict[str, Any]] = []
            for i, out in enumerate(outputs):
                decoded = tokenizer.decode(out, skip_special_tokens=True)
                toks = tokenizer.convert_ids_to_tokens(out)
                candidates.append({
                    "rank": i + 1,
                    "text": decoded,
                    "token_count": len([t for t in toks if not t.startswith("<")]),
                })

            best = candidates[0]["text"] if candidates else ""
            target_tokens = tokenizer.tokenize(best)

        except Exception as e:
            return T5Result(
                task_prefix=task_prefix, source_text=full_input,
                source_tokens=full_input.split(), target_text=f"[Error: {e}]",
                target_tokens=[], beam_candidates=[], parameters_used=params,
            )

        return T5Result(
            task_prefix=task_prefix,
            source_text=full_input,
            source_tokens=[str(t) for t in source_tokens],
            target_text=best,
            target_tokens=target_tokens,
            beam_candidates=candidates,
            parameters_used={
                "model": model_name, "num_beams": num_beams,
                "max_output_length": max_output_len, "length_penalty": length_penalty,
            },
        )

    def trace(self, preprocessed: Any, result: T5Result, request: RunRequest) -> dict[str, Any]:
        if request.trace_level == TraceLevel.NONE:
            return {}
        base: dict[str, Any] = {
            "task_prefix": result.task_prefix,
            "source_token_count": len(result.source_tokens),
            "target_text": result.target_text,
            "target_token_count": len(result.target_tokens),
            "beam_candidates": result.beam_candidates,
        }
        if request.trace_level == TraceLevel.SUMMARY:
            return base
        return {
            **base,
            "source_tokens": result.source_tokens,
            "target_tokens": result.target_tokens,
            "parameters_used": result.parameters_used,
        }

    def visualize(self, trace: dict[str, Any], result: T5Result, request: RunRequest) -> list[VisualizationSpec]:
        specs: list[VisualizationSpec] = []

        # Source / target token display
        specs.append(VisualizationSpec(
            type="diff",
            title="Source → Target (Text-to-Text)",
            data={"source": result.source_text, "target": result.target_text},
        ))

        # Beam candidates table
        specs.append(VisualizationSpec(
            type="table",
            title="Beam Search Candidates",
            data=result.beam_candidates,
        ))

        # Token counts comparison
        specs.append(VisualizationSpec(
            type="bar",
            title="Source vs Target Token Count",
            data=[
                {"label": "Source", "count": len(result.source_tokens)},
                {"label": "Target", "count": len(result.target_tokens)},
            ],
            config={"x": "label", "y": "count", "color": "#8b5cf6"},
        ))

        return specs

    def serialize_result(self, result: T5Result) -> dict[str, Any]:
        return {
            "task_prefix": result.task_prefix,
            "target_text": result.target_text,
            "source_token_count": len(result.source_tokens),
            "target_token_count": len(result.target_tokens),
            "beam_candidates": result.beam_candidates,
        }
