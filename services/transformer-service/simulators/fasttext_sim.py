"""
FastText Simulator — FT-001 through FT-004.

Uses the official fasttext Python library for supervised classification.
For subword n-gram visualization, decomposes tokens without requiring a full model.

Requires: pip install fasttext-wheel  (or `fasttext` on Linux/Mac)
"""
from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass, field
from typing import Any

from .base import BaseSimulator

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages"))
from shared_schemas import RunRequest, TraceLevel, VisualizationSpec, WarningEntry

from .demo_metadata import TRANSFORMER_DEMO_METADATA


def build_char_ngrams(token: str, min_n: int = 3, max_n: int = 6) -> list[str]:
    """Extract character-level n-grams (fastText style, with < > markers)."""
    padded = f"<{token.lower()}>"
    ngrams: list[str] = []
    for n in range(min_n, max_n + 1):
        for i in range(len(padded) - n + 1):
            ngrams.append(padded[i:i+n])
    return ngrams


@dataclass
class FastTextResult:
    task: str   # classification | subword
    predicted_labels: list[dict[str, Any]]  # [{label, confidence}]
    subword_breakdown: list[dict[str, Any]]  # [{token, ngrams}]
    metrics: dict[str, Any]
    training_params: dict[str, Any]


class FastTextSimulator(BaseSimulator):
    VERSION = "1.0.0"
    ALGORITHM_ID = "fasttext"
    DEMO_METADATA = TRANSFORMER_DEMO_METADATA.get("fasttext")

    def validate(self, request: RunRequest) -> list[WarningEntry]:
        warnings = []
        docs = [d for d in (request.documents or []) if d.label]
        if not docs and not request.text:
            raise ValueError("Provide labelled documents for classification or text for subword analysis.")
        if docs and len(docs) < 4:
            warnings.append(WarningEntry(
                code="SMALL_CORPUS",
                message="Very few labelled examples. FastText results will not generalise.",
                suggestion="Provide at least 50 labelled examples for reliable classification.",
            ))
        return warnings

    def preprocess(self, request: RunRequest) -> dict[str, Any]:
        docs = [d for d in (request.documents or []) if d.label]
        return {
            "docs": docs,
            "text": request.text or "",
            "params": request.parameters,
        }

    def run(self, preprocessed: dict[str, Any], request: RunRequest) -> FastTextResult:
        docs = preprocessed["docs"]
        text: str = preprocessed["text"]
        params = preprocessed["params"]

        min_n: int = params.get("min_char_ngram", 3)
        max_n: int = params.get("max_char_ngram", 6)
        lr: float = float(params.get("learning_rate", 0.5))
        epochs: int = int(params.get("epochs", 25))
        dim: int = int(params.get("dim", 100))
        word_ngrams: int = int(params.get("wordNgrams", 2))

        # Always show subword breakdown for the query text
        tokens = re.findall(r'[a-zA-Z]+', text)
        subword_breakdown = [
            {
                "token": tok,
                "ngrams": build_char_ngrams(tok, min_n, max_n),
                "ngram_count": len(build_char_ngrams(tok, min_n, max_n)),
            }
            for tok in tokens[:20]
        ]

        if not docs:
            return FastTextResult(
                task="subword",
                predicted_labels=[],
                subword_breakdown=subword_breakdown,
                metrics={},
                training_params={"min_n": min_n, "max_n": max_n},
            )

        # Classification mode
        try:
            import fasttext  # type: ignore
            from sklearn.model_selection import train_test_split

            all_texts = [d.text for d in docs]
            all_labels = [d.label for d in docs]
            unique = list(set(all_labels))

            if len(docs) >= 4 and len(unique) > 1:
                X_train, X_test, y_train, y_test = train_test_split(
                    all_texts, all_labels, test_size=0.2, random_state=42,
                    stratify=all_labels if all(all_labels.count(l) > 1 for l in unique) else None
                )
            else:
                X_train, X_test, y_train, y_test = all_texts, all_texts, all_labels, all_labels

            # Write training file
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                for txt, lbl in zip(X_train, y_train):
                    clean = re.sub(r'\s+', ' ', txt.replace('\n', ' '))
                    f.write(f"__label__{lbl} {clean}\n")
                train_path = f.name

            model = fasttext.train_supervised(
                train_path,
                lr=lr, epoch=epochs, dim=dim,
                wordNgrams=word_ngrams,
                minCount=1, verbose=0,
            )

            # Predict query text
            if text:
                labels, scores = model.predict(text, k=5)
                predicted_labels = [
                    {"label": lbl.replace("__label__", ""), "confidence": round(float(s), 4)}
                    for lbl, s in zip(labels, scores)
                ]
            else:
                predicted_labels = []

            # Evaluate
            test_texts_clean = [re.sub(r'\s+', ' ', t.replace('\n', ' ')) for t in X_test]
            correct = 0
            for t, true_lbl in zip(test_texts_clean, y_test):
                pred_labels, _ = model.predict(t, k=1)
                if pred_labels[0].replace("__label__", "") == true_lbl:
                    correct += 1
            accuracy = correct / len(y_test) if y_test else 0.0
            metrics = {"accuracy": round(accuracy, 4), "test_size": len(y_test)}

            os.unlink(train_path)

        except ImportError:
            predicted_labels = [{"label": "N/A", "confidence": 0, "error": "fasttext library not installed"}]
            metrics = {}

        return FastTextResult(
            task="classification",
            predicted_labels=predicted_labels,
            subword_breakdown=subword_breakdown,
            metrics=metrics,
            training_params={
                "lr": lr, "epochs": epochs, "dim": dim,
                "wordNgrams": word_ngrams, "min_n": min_n, "max_n": max_n,
            },
        )

    def trace(self, preprocessed: Any, result: FastTextResult, request: RunRequest) -> dict[str, Any]:
        if request.trace_level == TraceLevel.NONE:
            return {}
        base: dict[str, Any] = {
            "task": result.task,
            "predicted_labels": result.predicted_labels,
            "training_params": result.training_params,
            "metrics": result.metrics,
        }
        if request.trace_level == TraceLevel.SUMMARY:
            return base
        return {**base, "subword_breakdown": result.subword_breakdown}

    def visualize(self, trace: dict[str, Any], result: FastTextResult, request: RunRequest) -> list[VisualizationSpec]:
        specs: list[VisualizationSpec] = []

        if result.predicted_labels:
            specs.append(VisualizationSpec(
                type="bar",
                title="Classification Confidence",
                data=result.predicted_labels,
                config={"x": "label", "y": "confidence", "color": "#6366f1"},
            ))

        if result.subword_breakdown:
            specs.append(VisualizationSpec(
                type="table",
                title="Character N-gram Breakdown",
                data=result.subword_breakdown,
            ))

        return specs

    def serialize_result(self, result: FastTextResult) -> dict[str, Any]:
        return {
            "task": result.task,
            "predicted_labels": result.predicted_labels,
            "metrics": result.metrics,
            "training_params": result.training_params,
        }
