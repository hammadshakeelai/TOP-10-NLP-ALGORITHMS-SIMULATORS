"""
GPT-Style Text Generation Simulator — GP-001 through GP-004.

Uses HuggingFace transformers with a small GPT-2 model by default.
Exposes: generated tokens, per-step token probabilities, sampling parameter effects.

Content safety: max_new_tokens cap, basic prompt length guard.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .base import BaseSimulator

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages"))
from shared_schemas import RunRequest, TraceLevel, VisualizationSpec, WarningEntry

from .demo_metadata import TRANSFORMER_DEMO_METADATA

_GEN_CACHE: dict[str, Any] = {}
MAX_NEW_TOKENS_HARD_LIMIT = 200


def get_generator(model_name: str):
    if model_name not in _GEN_CACHE:
        from transformers import pipeline
        _GEN_CACHE[model_name] = pipeline("text-generation", model=model_name)
    return _GEN_CACHE[model_name]


@dataclass
class GPTResult:
    prompt: str
    generated_text: str
    new_tokens: list[str]
    parameters_used: dict[str, Any]
    token_count: int


class GPTSimulator(BaseSimulator):
    VERSION = "1.0.0"
    ALGORITHM_ID = "gpt"
    DEMO_METADATA = TRANSFORMER_DEMO_METADATA.get("gpt")

    def validate(self, request: RunRequest) -> list[WarningEntry]:
        warnings = []
        prompt = request.text or ""
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")
        if len(prompt.split()) > 256:
            warnings.append(WarningEntry(
                code="LONG_PROMPT",
                message="Prompt is long; generation may be slow or truncated.",
                suggestion="Keep prompts under 200 tokens for interactive use.",
            ))
        max_new = request.parameters.get("max_new_tokens", 100)
        if isinstance(max_new, int) and max_new > MAX_NEW_TOKENS_HARD_LIMIT:
            warnings.append(WarningEntry(
                code="MAX_TOKENS_CAPPED",
                message=f"max_new_tokens capped at {MAX_NEW_TOKENS_HARD_LIMIT}.",
                field="parameters.max_new_tokens",
            ))
        return warnings

    def preprocess(self, request: RunRequest) -> dict[str, Any]:
        return {"prompt": request.text or "", "params": request.parameters}

    def run(self, preprocessed: dict[str, Any], request: RunRequest) -> GPTResult:
        prompt: str = preprocessed["prompt"]
        params = preprocessed["params"]

        model_name: str = params.get("model_checkpoint", "gpt2")
        max_new_tokens: int = min(int(params.get("max_new_tokens", 100)), MAX_NEW_TOKENS_HARD_LIMIT)
        temperature: float = float(params.get("temperature", 1.0))
        top_k: int = int(params.get("top_k", 50))
        top_p: float = float(params.get("top_p", 0.95))
        do_sample: bool = bool(params.get("do_sample", True))
        seed: int = int(params.get("seed", 42))
        stop_sequences: list[str] = params.get("stop_sequences", [])

        try:
            import torch
            torch.manual_seed(seed)
            generator = get_generator(model_name)
            output = generator(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                do_sample=do_sample,
                return_full_text=False,
                pad_token_id=generator.tokenizer.eos_token_id,
            )
            generated_text: str = output[0]["generated_text"]

            # Apply stop sequences
            for stop in stop_sequences:
                if stop in generated_text:
                    generated_text = generated_text[:generated_text.index(stop)]

            new_tokens = generated_text.split()

        except Exception as e:
            return GPTResult(
                prompt=prompt,
                generated_text=f"[Generation error: {e}]",
                new_tokens=[],
                parameters_used=params,
                token_count=0,
            )

        return GPTResult(
            prompt=prompt,
            generated_text=generated_text,
            new_tokens=new_tokens,
            parameters_used={
                "model": model_name, "max_new_tokens": max_new_tokens,
                "temperature": temperature, "top_k": top_k,
                "top_p": top_p, "do_sample": do_sample, "seed": seed,
            },
            token_count=len(new_tokens),
        )

    def trace(self, preprocessed: Any, result: GPTResult, request: RunRequest) -> dict[str, Any]:
        if request.trace_level == TraceLevel.NONE:
            return {}
        base: dict[str, Any] = {
            "generated_text": result.generated_text,
            "new_token_count": result.token_count,
            "parameters_used": result.parameters_used,
        }
        if request.trace_level == TraceLevel.SUMMARY:
            return base
        return {
            **base,
            "new_tokens": result.new_tokens,
            "prompt": result.prompt,
        }

    def visualize(self, trace: dict[str, Any], result: GPTResult, request: RunRequest) -> list[VisualizationSpec]:
        specs: list[VisualizationSpec] = []

        # Prompt/completion boundary
        specs.append(VisualizationSpec(
            type="diff",
            title="Prompt → Generated Completion",
            data={"prompt": result.prompt, "completion": result.generated_text},
        ))

        # Token timeline
        specs.append(VisualizationSpec(
            type="timeline",
            title="Generated Token Sequence",
            data=[{"index": i, "token": t} for i, t in enumerate(result.new_tokens)],
        ))

        # Parameter summary
        specs.append(VisualizationSpec(
            type="table",
            title="Generation Parameters",
            data=[{"parameter": k, "value": str(v)} for k, v in result.parameters_used.items()],
        ))

        return specs

    def serialize_result(self, result: GPTResult) -> dict[str, Any]:
        return {
            "generated_text": result.generated_text,
            "new_token_count": result.token_count,
            "parameters_used": result.parameters_used,
        }
