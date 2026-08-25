"""
SVM Text Classification Simulator — SV-001 through SV-004.

Uses scikit-learn LinearSVC. Exposes decision margins, support vectors (via
dual coef approximation for LinearSVC), and top/bottom features per class.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.preprocessing import LabelEncoder
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from .base import BaseSimulator

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages"))
from shared_schemas import RunRequest, TraceLevel, VisualizationSpec, WarningEntry

from .demo_metadata import CLASSICAL_DEMO_METADATA


@dataclass
class SVMResult:
    predicted_class: str
    decision_scores: dict[str, float]
    predicted_probabilities: dict[str, float]
    top_positive_features: dict[str, list[dict[str, Any]]]
    top_negative_features: dict[str, list[dict[str, Any]]]
    confusion_matrix: list[list[int]]
    class_labels: list[str]
    classification_report: dict[str, Any]
    C_value: float


class SVMSimulator(BaseSimulator):
    VERSION = "1.0.0"
    ALGORITHM_ID = "svm"
    DEMO_METADATA = CLASSICAL_DEMO_METADATA.get("svm")

    def validate(self, request: RunRequest) -> list[WarningEntry]:
        warnings: list[WarningEntry] = []
        docs = [d for d in (request.documents or []) if d.label]
        if len(docs) < 4:
            warnings.append(WarningEntry(
                code="SMALL_CORPUS",
                message="Fewer than 4 labelled documents. Metrics will not be representative.",
                suggestion="Provide at least 20 labelled documents.",
            ))
        C = request.parameters.get("C", 1.0)
        if not isinstance(C, (int, float)) or C <= 0:
            warnings.append(WarningEntry(
                code="INVALID_C",
                message="C must be > 0; defaulting to 1.0.",
                field="parameters.C",
            ))
        return warnings

    def preprocess(self, request: RunRequest) -> dict[str, Any]:
        docs = [d for d in (request.documents or []) if d.label]
        texts = [d.text for d in docs]
        labels = [d.label for d in docs]
        test_size = request.parameters.get("test_size", 0.2)
        unique = list(set(labels))
        stratify = labels if len(unique) > 1 and all(labels.count(l) > 1 for l in unique) else None

        if len(texts) >= 4:
            # A stratified hold-out needs at least one test sample per class;
            # widen test_size for tiny corpora so train_test_split stays valid.
            min_test = len(unique) if stratify is not None else 1
            effective_test = max(test_size, min_test / len(texts))
            X_train, X_test, y_train, y_test = train_test_split(
                texts, labels, test_size=effective_test, random_state=42, stratify=stratify
            )
        else:
            X_train, X_test, y_train, y_test = texts, texts, labels, labels

        return {
            "X_train": X_train, "X_test": X_test,
            "y_train": y_train, "y_test": y_test,
            "query_text": request.text or (X_test[0] if X_test else ""),
            "params": request.parameters,
        }

    def run(self, preprocessed: dict[str, Any], request: RunRequest) -> SVMResult:
        C = float(preprocessed["params"].get("C", 1.0))
        C = C if C > 0 else 1.0
        ngram_range = tuple(preprocessed["params"].get("ngram_range", [1, 1]))
        max_features = preprocessed["params"].get("max_features", 5000)
        class_weight = preprocessed["params"].get("class_weight", None)

        vectorizer = TfidfVectorizer(ngram_range=ngram_range, max_features=max_features)
        X_train_vec = vectorizer.fit_transform(preprocessed["X_train"])
        X_test_vec = vectorizer.transform(preprocessed["X_test"])
        query_vec = vectorizer.transform([preprocessed["query_text"]])

        base_clf = LinearSVC(C=C, class_weight=class_weight, max_iter=2000)
        # Calibrated probabilities need >= 2 training examples per class for
        # the internal cross-validation; tiny corpora use the raw SVC instead.
        min_class_count = min(Counter(preprocessed["y_train"]).values())
        use_calibration = min_class_count >= 2

        if use_calibration:
            clf = CalibratedClassifierCV(base_clf, cv=min(3, min_class_count))
            clf.fit(X_train_vec, preprocessed["y_train"])
            predicted_class = clf.predict(query_vec)[0]
            probs = clf.predict_proba(query_vec)[0].tolist()
            predicted_probabilities = dict(zip(clf.classes_, [round(p, 4) for p in probs]))
            # Decision scores from base LinearSVC
            inner_clf: LinearSVC = clf.calibrated_classifiers_[0].estimator  # type: ignore
            classes = list(clf.classes_)
        else:
            base_clf.fit(X_train_vec, preprocessed["y_train"])
            predicted_class = base_clf.predict(query_vec)[0]
            predicted_probabilities = {}
            inner_clf = base_clf
            classes = list(base_clf.classes_)

        decision_scores_raw = inner_clf.decision_function(query_vec)[0]
        if len(classes) == 2 and np.asarray(decision_scores_raw).ndim == 0:
            score = float(decision_scores_raw)
            decision_scores = {
                classes[0]: round(-score, 4),
                classes[1]: round(score, 4),
            }
        else:
            decision_scores_raw = np.atleast_1d(decision_scores_raw)
            decision_scores = {cls: round(float(s), 4) for cls, s in zip(classes, decision_scores_raw)}

        # Top features per class (LinearSVC coef_)
        feature_names = vectorizer.get_feature_names_out()
        top_pos: dict[str, list[dict[str, Any]]] = {}
        top_neg: dict[str, list[dict[str, Any]]] = {}
        coef = inner_clf.coef_
        if coef.shape[0] == 1:
            coef = np.vstack([-coef, coef])
        for i, cls in enumerate(inner_clf.classes_):
            sorted_idx = np.argsort(coef[i])
            top_neg[str(cls)] = [
                {"feature": feature_names[j], "coef": round(coef[i][j], 4)}
                for j in sorted_idx[:10]
            ]
            top_pos[str(cls)] = [
                {"feature": feature_names[j], "coef": round(coef[i][j], 4)}
                for j in sorted_idx[:-11:-1]
            ]

        y_pred = inner_clf.predict(X_test_vec)
        cm = confusion_matrix(preprocessed["y_test"], y_pred, labels=classes).tolist()
        report = classification_report(preprocessed["y_test"], y_pred, output_dict=True, zero_division=0)

        return SVMResult(
            predicted_class=predicted_class,
            decision_scores=decision_scores,
            predicted_probabilities=predicted_probabilities,
            top_positive_features=top_pos,
            top_negative_features=top_neg,
            confusion_matrix=cm,
            class_labels=classes,
            classification_report=report,
            C_value=C,
        )

    def trace(self, preprocessed: Any, result: SVMResult, request: RunRequest) -> dict[str, Any]:
        if request.trace_level == TraceLevel.NONE:
            return {}
        base = {
            "predicted_class": result.predicted_class,
            "decision_scores": result.decision_scores,
            "C_value": result.C_value,
            "kernel": "linear (LinearSVC)",
        }
        if request.trace_level == TraceLevel.SUMMARY:
            return base
        return {
            **base,
            "predicted_probabilities": result.predicted_probabilities,
            "top_positive_features": result.top_positive_features,
            "top_negative_features": result.top_negative_features,
            "confusion_matrix": result.confusion_matrix,
            "class_labels": result.class_labels,
            "classification_report": result.classification_report,
        }

    def visualize(self, trace: dict[str, Any], result: SVMResult, request: RunRequest) -> list[VisualizationSpec]:
        specs: list[VisualizationSpec] = []
        specs.append(VisualizationSpec(
            type="bar",
            title="Decision Scores",
            data=[{"class": k, "score": v} for k, v in result.decision_scores.items()],
            config={"x": "class", "y": "score", "diverging": True, "zero_line": True},
        ))
        for cls in result.class_labels:
            pos = result.top_positive_features.get(str(cls), [])
            neg = result.top_negative_features.get(str(cls), [])
            specs.append(VisualizationSpec(
                type="bar",
                title=f"Feature Coefficients — {cls}",
                data=neg + pos,
                config={"x": "feature", "y": "coef", "diverging": True},
            ))
        specs.append(VisualizationSpec(
            type="heatmap",
            title="Confusion Matrix",
            data={"labels": result.class_labels, "matrix": result.confusion_matrix},
            config={"colorscale": "Blues", "annotate": True},
        ))
        return specs

    def serialize_result(self, result: SVMResult) -> dict[str, Any]:
        return {
            "predicted_class": result.predicted_class,
            "decision_scores": result.decision_scores,
            "predicted_probabilities": result.predicted_probabilities,
            "accuracy": result.classification_report.get("accuracy", 0),
            "confusion_matrix": result.confusion_matrix,
            "class_labels": result.class_labels,
        }
