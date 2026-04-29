"""
Naive Bayes Text Classification Simulator — NB-001 through NB-004.

Uses scikit-learn MultinomialNB under the hood for correctness,
but exposes every intermediate probability for the trace viewer.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split

from .base import BaseSimulator

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages"))
from shared_schemas import RunRequest, TraceLevel, VisualizationSpec, WarningEntry

from .demo_metadata import CLASSICAL_DEMO_METADATA


@dataclass
class NBResult:
    predicted_class: str
    predicted_probabilities: dict[str, float]
    class_priors: dict[str, float]
    top_features_per_class: dict[str, list[dict[str, Any]]]
    confusion_matrix: list[list[int]]
    class_labels: list[str]
    classification_report: dict[str, Any]
    smoothing_alpha: float
    test_texts: list[str] = field(default_factory=list)
    test_labels: list[str] = field(default_factory=list)
    predicted_labels: list[str] = field(default_factory=list)


class NaiveBayesSimulator(BaseSimulator):
    VERSION = "1.0.0"
    ALGORITHM_ID = "naive_bayes"
    DEMO_METADATA = CLASSICAL_DEMO_METADATA.get("naive_bayes")

    def validate(self, request: RunRequest) -> list[WarningEntry]:
        warnings: list[WarningEntry] = []
        docs = request.documents or []
        if len(docs) < 4:
            warnings.append(WarningEntry(
                code="SMALL_CORPUS",
                message="Fewer than 4 documents provided. Train/test split may be unreliable.",
                suggestion="Provide at least 20 labelled documents for meaningful evaluation.",
            ))
        missing_labels = [d.id for d in docs if not d.label]
        if missing_labels:
            warnings.append(WarningEntry(
                code="MISSING_LABELS",
                message=f"{len(missing_labels)} document(s) have no label and will be excluded from training.",
                field="documents[*].label",
            ))
        alpha = request.parameters.get("smoothing_alpha", 1.0)
        if not isinstance(alpha, (int, float)) or alpha <= 0:
            warnings.append(WarningEntry(
                code="INVALID_ALPHA",
                message="smoothing_alpha must be > 0; defaulting to 1.0.",
                field="parameters.smoothing_alpha",
            ))
        return warnings

    def preprocess(self, request: RunRequest) -> dict[str, Any]:
        docs = [d for d in (request.documents or []) if d.label]
        texts = [d.text for d in docs]
        labels = [d.label for d in docs]
        test_size = request.parameters.get("test_size", 0.2)
        random_state = request.parameters.get("random_state", 42)

        if len(texts) >= 4:
            X_train, X_test, y_train, y_test = train_test_split(
                texts, labels, test_size=test_size, random_state=random_state, stratify=labels
                if len(set(labels)) > 1 else None
            )
        else:
            X_train, X_test, y_train, y_test = texts, texts, labels, labels

        # If there's a separate test text in the request
        query_text = request.text or (X_test[0] if X_test else "")

        return {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "query_text": query_text,
            "params": request.parameters,
        }

    def run(self, preprocessed: dict[str, Any], request: RunRequest) -> NBResult:
        alpha = float(preprocessed["params"].get("smoothing_alpha", 1.0))
        alpha = alpha if alpha > 0 else 1.0
        ngram_range = tuple(preprocessed["params"].get("ngram_range", [1, 1]))
        max_features = preprocessed["params"].get("max_features", 5000)

        vectorizer = CountVectorizer(ngram_range=ngram_range, max_features=max_features)
        X_train_vec = vectorizer.fit_transform(preprocessed["X_train"])
        X_test_vec = vectorizer.transform(preprocessed["X_test"])
        query_vec = vectorizer.transform([preprocessed["query_text"]])

        clf = MultinomialNB(alpha=alpha)
        clf.fit(X_train_vec, preprocessed["y_train"])

        # Query prediction
        predicted_class = clf.predict(query_vec)[0]
        predicted_probs = dict(zip(clf.classes_, clf.predict_proba(query_vec)[0].tolist()))

        # Class priors
        class_priors = dict(zip(clf.classes_, np.exp(clf.class_log_prior_).tolist()))

        # Top features per class
        feature_names = vectorizer.get_feature_names_out()
        top_features_per_class: dict[str, list[dict[str, Any]]] = {}
        for i, cls in enumerate(clf.classes_):
            log_probs = clf.feature_log_prob_[i]
            top_idx = np.argsort(log_probs)[::-1][:15]
            top_features_per_class[cls] = [
                {"feature": feature_names[j], "log_prob": round(log_probs[j], 4)}
                for j in top_idx
            ]

        # Evaluation
        y_pred = clf.predict(X_test_vec)
        cm = confusion_matrix(preprocessed["y_test"], y_pred, labels=list(clf.classes_)).tolist()
        report = classification_report(
            preprocessed["y_test"], y_pred, output_dict=True, zero_division=0
        )

        return NBResult(
            predicted_class=predicted_class,
            predicted_probabilities={k: round(v, 4) for k, v in predicted_probs.items()},
            class_priors={k: round(v, 4) for k, v in class_priors.items()},
            top_features_per_class=top_features_per_class,
            confusion_matrix=cm,
            class_labels=list(clf.classes_),
            classification_report=report,
            smoothing_alpha=alpha,
            test_texts=preprocessed["X_test"],
            test_labels=preprocessed["y_test"],
            predicted_labels=y_pred.tolist(),
        )

    def trace(self, preprocessed: dict[str, Any], result: NBResult, request: RunRequest) -> dict[str, Any]:
        if request.trace_level == TraceLevel.NONE:
            return {}
        base = {
            "predicted_class": result.predicted_class,
            "predicted_probabilities": result.predicted_probabilities,
            "class_priors": result.class_priors,
            "smoothing_alpha": result.smoothing_alpha,
            "formula": "P(class|text) ∝ P(class) × ∏ P(word|class)^α",
        }
        if request.trace_level == TraceLevel.SUMMARY:
            return base
        return {
            **base,
            "top_features_per_class": result.top_features_per_class,
            "confusion_matrix": result.confusion_matrix,
            "class_labels": result.class_labels,
            "classification_report": result.classification_report,
        }

    def visualize(self, trace: dict[str, Any], result: NBResult, request: RunRequest) -> list[VisualizationSpec]:
        specs: list[VisualizationSpec] = []

        # Probability bar chart
        specs.append(VisualizationSpec(
            type="bar",
            title="Predicted Class Probabilities",
            data=[{"class": k, "probability": v} for k, v in result.predicted_probabilities.items()],
            config={"x": "class", "y": "probability", "color": "#6366f1"},
        ))

        # Top features per class
        for cls, features in result.top_features_per_class.items():
            specs.append(VisualizationSpec(
                type="bar",
                title=f"Top Features — Class: {cls}",
                data=features,
                config={"x": "feature", "y": "log_prob", "color": "#10b981"},
            ))

        # Confusion matrix heatmap
        specs.append(VisualizationSpec(
            type="heatmap",
            title="Confusion Matrix",
            data={"labels": result.class_labels, "matrix": result.confusion_matrix},
            config={"colorscale": "Blues", "annotate": True},
        ))

        return specs

    def serialize_result(self, result: NBResult) -> dict[str, Any]:
        return {
            "predicted_class": result.predicted_class,
            "predicted_probabilities": result.predicted_probabilities,
            "class_priors": result.class_priors,
            "accuracy": result.classification_report.get("accuracy", 0),
            "confusion_matrix": result.confusion_matrix,
            "class_labels": result.class_labels,
        }
