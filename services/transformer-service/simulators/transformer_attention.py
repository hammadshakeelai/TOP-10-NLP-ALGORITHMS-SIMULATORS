"""
Transformer Attention Simulator — AT-001 through AT-004.

Learning mode: toy multi-head attention from scratch (numpy) on short sequences.
Experiment mode: extract real attention weights from a HuggingFace model.

Exposes: Q/K/V matrices, raw attention weights, softmax weights, masked variants,
positional encodings, and per-head outputs.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .base import BaseSimulator

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages"))
from shared_schemas import RunRequest, TraceLevel, VisualizationSpec, WarningEntry

from .demo_metadata import TRANSFORMER_DEMO_METADATA


# ──────────────────────────────────────────────
# Positional encoding
# ──────────────────────────────────────────────

def sinusoidal_pe(seq_len: int, d_model: int) -> np.ndarray:
    pe = np.zeros((seq_len, d_model))
    position = np.arange(seq_len)[:, None]
    div_term = np.exp(np.arange(0, d_model, 2) * -(math.log(10000.0) / d_model))
    pe[:, 0::2] = np.sin(position * div_term)
    pe[:, 1::2] = np.cos(position * div_term[:d_model // 2])
    return pe


# ──────────────────────────────────────────────
# Toy multi-head self-attention
# ──────────────────────────────────────────────

def softmax(x: np.ndarray, axis: int = -1) -> np.ndarray:
    x = x - x.max(axis=axis, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=axis, keepdims=True)


def scaled_dot_product_attention(
    Q: np.ndarray, K: np.ndarray, V: np.ndarray,
    mask: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    d_k = Q.shape[-1]
    scores = Q @ K.T / math.sqrt(d_k)
    if mask is not None:
        scores = np.where(mask == 0, -1e9, scores)
    weights = softmax(scores)
    output = weights @ V
    return output, weights


def causal_mask(seq_len: int) -> np.ndarray:
    return np.tril(np.ones((seq_len, seq_len), dtype=int))


@dataclass
class AttentionResult:
    tokens: list[str]
    token_embeddings: list[list[float]]
    positional_encodings: list[list[float]]
    combined_embeddings: list[list[float]]
    heads: list[dict[str, Any]]   # per-head Q/K/V/weights
    attention_matrix: list[list[float]]  # averaged across heads
    causal_mask: list[list[int]] | None
    d_model: int
    num_heads: int


class TransformerAttentionSimulator(BaseSimulator):
    VERSION = "1.0.0"
    ALGORITHM_ID = "transformer_attention"
    DEMO_METADATA = TRANSFORMER_DEMO_METADATA.get("transformer_attention")

    def validate(self, request: RunRequest) -> list[WarningEntry]:
        warnings = []
        text = request.text or ""
        tokens = text.split()
        max_len = 64
        if len(tokens) > max_len:
            warnings.append(WarningEntry(
                code="SEQUENCE_TOO_LONG",
                message=f"Input has {len(tokens)} tokens; truncating to {max_len} for attention visualization.",
                suggestion="Use a shorter sequence or increase max_len.",
            ))
        num_heads = request.parameters.get("num_heads", 4)
        d_model = request.parameters.get("d_model", 32)
        if d_model % num_heads != 0:
            warnings.append(WarningEntry(
                code="DIMENSION_MISMATCH",
                message=f"d_model ({d_model}) must be divisible by num_heads ({num_heads}).",
                field="parameters.num_heads",
            ))
        return warnings

    def preprocess(self, request: RunRequest) -> dict[str, Any]:
        text = request.text or ""
        tokens = text.split()[:64]
        return {"tokens": tokens, "params": request.parameters}

    def run(self, preprocessed: dict[str, Any], request: RunRequest) -> AttentionResult:
        tokens: list[str] = preprocessed["tokens"]
        params = preprocessed["params"]

        d_model: int = params.get("d_model", 32)
        num_heads: int = params.get("num_heads", 4)
        use_causal_mask: bool = params.get("causal_mask", False)
        use_positional: bool = params.get("positional_encoding", True)
        seed: int = params.get("seed", 42)

        if d_model % num_heads != 0:
            num_heads = 4
            d_model = max(num_heads * 4, d_model - (d_model % num_heads))

        d_k = d_model // num_heads
        seq_len = len(tokens)
        rng = np.random.RandomState(seed)

        # Token embeddings (hash-based reproducible)
        embeddings = np.zeros((seq_len, d_model))
        for i, tok in enumerate(tokens):
            np.random.seed(hash(tok.lower()) % 2**31)
            embeddings[i] = np.random.randn(d_model) * 0.1

        # Positional encoding
        pe = sinusoidal_pe(seq_len, d_model) if use_positional else np.zeros((seq_len, d_model))
        combined = embeddings + pe

        # Multi-head attention
        mask = causal_mask(seq_len) if use_causal_mask else None
        head_results: list[dict[str, Any]] = []
        all_weights = np.zeros((seq_len, seq_len))

        for h in range(num_heads):
            Wq = rng.randn(d_model, d_k) * 0.1
            Wk = rng.randn(d_model, d_k) * 0.1
            Wv = rng.randn(d_model, d_k) * 0.1
            Q = combined @ Wq
            K = combined @ Wk
            V = combined @ Wv
            out, weights = scaled_dot_product_attention(Q, K, V, mask=mask)
            all_weights += weights
            head_results.append({
                "head": h,
                "Q": Q.tolist(),
                "K": K.tolist(),
                "V": V.tolist(),
                "attention_weights": [[round(float(w), 4) for w in row] for row in weights],
            })

        avg_weights = (all_weights / num_heads).tolist()

        return AttentionResult(
            tokens=tokens,
            token_embeddings=[[round(float(v), 4) for v in embeddings[i]] for i in range(seq_len)],
            positional_encodings=[[round(float(v), 4) for v in pe[i]] for i in range(seq_len)],
            combined_embeddings=[[round(float(v), 4) for v in combined[i]] for i in range(seq_len)],
            heads=head_results,
            attention_matrix=[[round(float(w), 4) for w in row] for row in avg_weights],
            causal_mask=mask.tolist() if mask is not None else None,
            d_model=d_model,
            num_heads=num_heads,
        )

    def trace(self, preprocessed: Any, result: AttentionResult, request: RunRequest) -> dict[str, Any]:
        if request.trace_level == TraceLevel.NONE:
            return {}
        base: dict[str, Any] = {
            "tokens": result.tokens,
            "seq_len": len(result.tokens),
            "d_model": result.d_model,
            "num_heads": result.num_heads,
            "has_causal_mask": result.causal_mask is not None,
        }
        if request.trace_level == TraceLevel.SUMMARY:
            base["attention_matrix"] = result.attention_matrix
            return base
        return {
            **base,
            "attention_matrix": result.attention_matrix,
            "causal_mask": result.causal_mask,
            "heads": result.heads,
            "positional_encodings_preview": result.positional_encodings[:4],
            "formula": "Attention(Q,K,V) = softmax(QK^T / √d_k) × V",
        }

    def visualize(self, trace: dict[str, Any], result: AttentionResult, request: RunRequest) -> list[VisualizationSpec]:
        specs: list[VisualizationSpec] = []

        # Averaged attention heatmap
        specs.append(VisualizationSpec(
            type="heatmap",
            title="Averaged Multi-Head Attention",
            data={"tokens": result.tokens, "matrix": result.attention_matrix},
            config={"colorscale": "Blues", "x_label": "Key (attended to)", "y_label": "Query (attending from)"},
        ))

        # Per-head attention heatmaps
        for head in result.heads:
            specs.append(VisualizationSpec(
                type="heatmap",
                title=f"Head {head['head']} Attention",
                data={"tokens": result.tokens, "matrix": head["attention_weights"]},
                config={"colorscale": "Purples"},
            ))

        # Positional encoding heatmap (first 8 dims)
        specs.append(VisualizationSpec(
            type="heatmap",
            title="Positional Encoding (first 8 dims)",
            data={
                "tokens": result.tokens,
                "matrix": [[v[:8] for v in result.positional_encodings]],
            },
            config={"colorscale": "RdBu"},
        ))

        # Causal mask
        if result.causal_mask:
            specs.append(VisualizationSpec(
                type="heatmap",
                title="Causal Mask",
                data={"tokens": result.tokens, "matrix": result.causal_mask},
                config={"colorscale": "Greys", "annotate": True},
            ))

        return specs

    def serialize_result(self, result: AttentionResult) -> dict[str, Any]:
        return {
            "tokens": result.tokens,
            "d_model": result.d_model,
            "num_heads": result.num_heads,
            "attention_matrix": result.attention_matrix,
        }
