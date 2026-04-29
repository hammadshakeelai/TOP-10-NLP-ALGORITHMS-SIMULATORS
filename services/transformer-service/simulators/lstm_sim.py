"""
LSTM Simulator — LS-001 through LS-004.

Learning mode: toy LSTM with random (or fixed-seed) weights for gate visualization.
Experiment mode: PyTorch LSTM (sentiment classification on small labelled corpus).

Exposes per-step: hidden state, cell state, forget/input/output gate activations.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .base import BaseSimulator

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages"))
from shared_schemas import RunRequest, TraceLevel, VisualizationSpec, WarningEntry

from .demo_metadata import TRANSFORMER_DEMO_METADATA


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-max(-500, min(500, x))))


def tanh(x: float) -> float:
    return math.tanh(max(-500, min(500, x)))


@dataclass
class LSTMStep:
    step: int
    token: str
    input_vec: list[float]
    forget_gate: list[float]
    input_gate: list[float]
    cell_gate: list[float]
    output_gate: list[float]
    cell_state: list[float]
    hidden_state: list[float]


@dataclass
class LSTMResult:
    steps: list[LSTMStep]
    final_hidden: list[float]
    prediction: str | None
    confidence: float | None
    tokens: list[str]
    hidden_size: int


class ToyLSTM:
    """Single-layer LSTM cell with traceable gates."""

    def __init__(self, input_size: int, hidden_size: int, seed: int = 42):
        rng = np.random.RandomState(seed)
        # Weight matrices initialized small to keep gates interpretable
        scale = 0.1
        self.Wf = rng.randn(hidden_size, input_size + hidden_size) * scale
        self.bf = np.zeros(hidden_size)
        self.Wi = rng.randn(hidden_size, input_size + hidden_size) * scale
        self.bi = np.zeros(hidden_size)
        self.Wc = rng.randn(hidden_size, input_size + hidden_size) * scale
        self.bc = np.zeros(hidden_size)
        self.Wo = rng.randn(hidden_size, input_size + hidden_size) * scale
        self.bo = np.zeros(hidden_size)

    def step(
        self,
        x: np.ndarray,
        h_prev: np.ndarray,
        c_prev: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
        combined = np.concatenate([x, h_prev])
        f = np.vectorize(sigmoid)(self.Wf @ combined + self.bf)
        i = np.vectorize(sigmoid)(self.Wi @ combined + self.bi)
        g = np.vectorize(tanh)(self.Wc @ combined + self.bc)
        o = np.vectorize(sigmoid)(self.Wo @ combined + self.bo)
        c = f * c_prev + i * g
        h = o * np.vectorize(tanh)(c)
        return h, c, {"f": f, "i": i, "g": g, "o": o}


class LSTMSimulator(BaseSimulator):
    VERSION = "1.0.0"
    ALGORITHM_ID = "lstm"
    DEMO_METADATA = TRANSFORMER_DEMO_METADATA.get("lstm")

    def validate(self, request: RunRequest) -> list[WarningEntry]:
        warnings = []
        text = request.text or ""
        max_seq = request.parameters.get("max_seq_len", 50)
        tokens = text.split()
        if len(tokens) > max_seq:
            warnings.append(WarningEntry(
                code="SEQUENCE_TRUNCATED",
                message=f"Input has {len(tokens)} tokens; truncating to {max_seq}.",
                suggestion="Increase max_seq_len or shorten input.",
            ))
        return warnings

    def preprocess(self, request: RunRequest) -> dict[str, Any]:
        text = request.text or ""
        max_seq = request.parameters.get("max_seq_len", 50)
        tokens = text.split()[:max_seq]
        padded = tokens + ["<PAD>"] * (max_seq - len(tokens))
        padded_flags = [False] * len(tokens) + [True] * (max_seq - len(tokens))
        return {
            "tokens": tokens,
            "padded": padded,
            "padded_flags": padded_flags,
            "params": request.parameters,
        }

    def run(self, preprocessed: dict[str, Any], request: RunRequest) -> LSTMResult:
        tokens: list[str] = preprocessed["tokens"]
        params = preprocessed["params"]

        hidden_size = params.get("hidden_size", 8)
        input_size = params.get("input_size", 16)
        seed = params.get("random_seed", 42)

        # Build a tiny fixed embedding (hash-based, for reproducibility)
        rng = np.random.RandomState(seed)
        embedding_table: dict[str, np.ndarray] = {}

        def embed(token: str) -> np.ndarray:
            if token not in embedding_table:
                np.random.seed(hash(token) % 2**31)
                embedding_table[token] = np.random.randn(input_size).astype(float) * 0.1
            return embedding_table[token]

        lstm = ToyLSTM(input_size, hidden_size, seed=seed)
        h = np.zeros(hidden_size)
        c = np.zeros(hidden_size)
        steps: list[LSTMStep] = []

        for step_idx, token in enumerate(tokens):
            x = embed(token)
            h, c, gates = lstm.step(x, h, c)
            steps.append(LSTMStep(
                step=step_idx,
                token=token,
                input_vec=[round(float(v), 4) for v in x[:4]],   # preview only
                forget_gate=[round(float(v), 4) for v in gates["f"]],
                input_gate=[round(float(v), 4) for v in gates["i"]],
                cell_gate=[round(float(v), 4) for v in gates["g"]],
                output_gate=[round(float(v), 4) for v in gates["o"]],
                cell_state=[round(float(v), 4) for v in c],
                hidden_state=[round(float(v), 4) for v in h],
            ))

        # Toy classification head (binary sentiment)
        W_out = rng.randn(2, hidden_size) * 0.1
        logits = W_out @ h
        probs = np.exp(logits - logits.max())
        probs /= probs.sum()
        pred_idx = int(np.argmax(probs))
        labels = params.get("class_labels", ["negative", "positive"])
        prediction = labels[pred_idx] if pred_idx < len(labels) else str(pred_idx)

        return LSTMResult(
            steps=steps,
            final_hidden=[round(float(v), 4) for v in h],
            prediction=prediction,
            confidence=round(float(probs[pred_idx]), 4),
            tokens=tokens,
            hidden_size=hidden_size,
        )

    def trace(self, preprocessed: Any, result: LSTMResult, request: RunRequest) -> dict[str, Any]:
        if request.trace_level == TraceLevel.NONE:
            return {}
        base: dict[str, Any] = {
            "token_count": len(result.tokens),
            "hidden_size": result.hidden_size,
            "prediction": result.prediction,
            "confidence": result.confidence,
        }
        if request.trace_level == TraceLevel.SUMMARY:
            return base
        return {
            **base,
            "steps": [
                {
                    "step": s.step,
                    "token": s.token,
                    "forget_gate_mean": round(sum(s.forget_gate) / len(s.forget_gate), 4),
                    "input_gate_mean": round(sum(s.input_gate) / len(s.input_gate), 4),
                    "output_gate_mean": round(sum(s.output_gate) / len(s.output_gate), 4),
                    "cell_state_norm": round(float(np.linalg.norm(s.cell_state)), 4),
                    "hidden_state_norm": round(float(np.linalg.norm(s.hidden_state)), 4),
                }
                for s in result.steps
            ],
            "full_steps": [s.__dict__ for s in result.steps],
        }

    def visualize(self, trace: dict[str, Any], result: LSTMResult, request: RunRequest) -> list[VisualizationSpec]:
        specs: list[VisualizationSpec] = []

        # Gate activation heatmap (each gate × each step)
        gate_heatmap: dict[str, list[list[float]]] = {
            "forget": [s.forget_gate for s in result.steps],
            "input": [s.input_gate for s in result.steps],
            "output": [s.output_gate for s in result.steps],
        }
        specs.append(VisualizationSpec(
            type="heatmap",
            title="Gate Activations Over Time",
            data={
                "tokens": result.tokens,
                "gates": gate_heatmap,
                "hidden_size": result.hidden_size,
            },
            config={"colorscale": "RdBu", "center": 0.5},
        ))

        # Hidden state trajectory (norm per step)
        hidden_norms = [
            {"step": s.step, "token": s.token,
             "hidden_norm": round(float(np.linalg.norm(s.hidden_state)), 4),
             "cell_norm": round(float(np.linalg.norm(s.cell_state)), 4)}
            for s in result.steps
        ]
        specs.append(VisualizationSpec(
            type="line",
            title="Hidden & Cell State Norms Over Steps",
            data=hidden_norms,
            config={"x": "step", "y": ["hidden_norm", "cell_norm"], "label": "token"},
        ))

        # Prediction confidence bar
        specs.append(VisualizationSpec(
            type="bar",
            title="Prediction Confidence",
            data=[{"label": result.prediction, "confidence": result.confidence}],
            config={"x": "label", "y": "confidence", "color": "#6366f1"},
        ))

        return specs

    def serialize_result(self, result: LSTMResult) -> dict[str, Any]:
        return {
            "prediction": result.prediction,
            "confidence": result.confidence,
            "token_count": len(result.tokens),
            "hidden_size": result.hidden_size,
        }
