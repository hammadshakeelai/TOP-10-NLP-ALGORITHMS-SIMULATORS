"""
TF-IDF Simulator — implements TF-001 through TF-004 from the SRS.

Two execution paths:
  learning mode  → from-scratch Python implementation so every formula step is traceable
  experiment mode → scikit-learn TfidfVectorizer (faster, handles large corpora)

Intermediate artifacts exposed:
  - tf_table   : per-document term frequency for every term
  - idf_table  : inverse document frequency for every term
  - tfidf_matrix : full document × term matrix
  - cosine_similarity_matrix : document × document similarity
  - query_scores : ranked documents for a query (optional)
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .base import BaseSimulator

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages"))
from shared_schemas import RunRequest, TraceLevel, VisualizationSpec, WarningEntry

from .demo_metadata import CLASSICAL_DEMO_METADATA


# ──────────────────────────────────────────────
# Data structures
# ──────────────────────────────────────────────

@dataclass
class TFIDFResult:
    vocabulary: list[str]
    tf_table: list[dict[str, Any]]      # [{doc_id, term, tf}, ...]
    idf_table: list[dict[str, Any]]     # [{term, idf, doc_count}, ...]
    tfidf_matrix: list[dict[str, Any]]  # [{doc_id, term, score}, ...]
    top_terms_per_doc: list[dict[str, Any]]
    cosine_similarity_matrix: list[list[float]]
    document_ids: list[str]
    query_results: list[dict[str, Any]] = field(default_factory=list)


# ──────────────────────────────────────────────
# From-scratch implementation (learning mode)
# ──────────────────────────────────────────────

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "in", "on", "at",
    "to", "for", "of", "with", "by", "from", "and", "or", "but",
    "not", "this", "that", "it", "its",
}

TOKEN_RE = re.compile(r'\b[a-zA-Z]\w+\b')


def tokenize_for_tfidf(text: str, params: dict[str, Any]) -> list[str]:
    lowercase = params.get("lowercase", True)
    remove_stop = params.get("remove_stopwords", True)
    tokens = TOKEN_RE.findall(text)
    if lowercase:
        tokens = [t.lower() for t in tokens]
    if remove_stop:
        tokens = [t for t in tokens if t not in STOPWORDS]
    return tokens


def compute_tf(tokens: list[str], scheme: str = "raw") -> dict[str, float]:
    """
    scheme:
      raw        — raw count
      freq       — relative frequency (count / total)
      log        — 1 + log(count)
      bool       — binary presence
    """
    counts = Counter(tokens)
    total = len(tokens) or 1
    if scheme == "raw":
        return {t: float(c) for t, c in counts.items()}
    if scheme == "freq":
        return {t: c / total for t, c in counts.items()}
    if scheme == "log":
        return {t: 1 + math.log(c) for t, c in counts.items()}
    if scheme == "bool":
        return {t: 1.0 for t in counts}
    return {t: float(c) for t, c in counts.items()}


def compute_idf(
    all_token_sets: list[set[str]],
    vocabulary: list[str],
    smooth: bool = True,
) -> dict[str, float]:
    """
    smooth=True  : log((1 + N) / (1 + df)) + 1   (scikit-learn default)
    smooth=False : log(N / df) + 1
    """
    N = len(all_token_sets)
    idf: dict[str, float] = {}
    for term in vocabulary:
        df = sum(1 for ts in all_token_sets if term in ts)
        if smooth:
            idf[term] = math.log((1 + N) / (1 + df)) + 1
        else:
            df = df or 1
            idf[term] = math.log(N / df) + 1
    return idf


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    a = np.array(vec_a, dtype=float)
    b = np.array(vec_b, dtype=float)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def l2_normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0:
        return vec
    return [v / norm for v in vec]


def scratch_tfidf(
    documents: list[dict[str, str]],
    params: dict[str, Any],
) -> TFIDFResult:
    ngram_range: tuple[int, int] = tuple(params.get("ngram_range", [1, 1]))  # type: ignore
    smooth_idf: bool = params.get("smooth_idf", True)
    normalize: bool = params.get("normalize", True)
    tf_scheme: str = params.get("tf_scheme", "raw")
    top_n: int = params.get("top_n", 10)

    # Tokenize
    doc_tokens: list[list[str]] = []
    doc_ids: list[str] = []
    for doc in documents:
        tokens = tokenize_for_tfidf(doc["text"], params)
        # Build ngrams
        if ngram_range[1] > 1:
            ngrams = []
            for n in range(ngram_range[0], ngram_range[1] + 1):
                ngrams += [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]
            tokens = ngrams if ngrams else tokens
        doc_tokens.append(tokens)
        doc_ids.append(doc.get("id", f"doc_{len(doc_ids)}"))

    # Vocabulary
    all_token_sets = [set(t) for t in doc_tokens]
    vocab = sorted(set(t for ts in doc_tokens for t in ts))

    # TF tables
    tf_maps: list[dict[str, float]] = []
    tf_table: list[dict[str, Any]] = []
    for tokens, doc_id in zip(doc_tokens, doc_ids):
        tf = compute_tf(tokens, tf_scheme)
        tf_maps.append(tf)
        for term, score in tf.items():
            tf_table.append({"doc_id": doc_id, "term": term, "tf": round(score, 6)})

    # IDF table
    idf_map = compute_idf(all_token_sets, vocab, smooth=smooth_idf)
    idf_table = [
        {"term": t, "idf": round(idf_map[t], 6), "doc_count": sum(1 for ts in all_token_sets if t in ts)}
        for t in vocab
    ]

    # TF-IDF matrix (document × term)
    tfidf_matrix_raw: list[list[float]] = []
    tfidf_matrix: list[dict[str, Any]] = []
    for tf, doc_id in zip(tf_maps, doc_ids):
        vec = [tf.get(term, 0.0) * idf_map.get(term, 0.0) for term in vocab]
        if normalize:
            vec = l2_normalize(vec)
        tfidf_matrix_raw.append(vec)
        for term, score in zip(vocab, vec):
            if score > 0:
                tfidf_matrix.append({"doc_id": doc_id, "term": term, "score": round(score, 6)})

    # Top-N terms per document
    top_terms_per_doc: list[dict[str, Any]] = []
    for doc_id, vec in zip(doc_ids, tfidf_matrix_raw):
        ranked = sorted(zip(vocab, vec), key=lambda x: -x[1])[:top_n]
        top_terms_per_doc.append({
            "doc_id": doc_id,
            "terms": [{"term": t, "score": round(s, 6)} for t, s in ranked if s > 0],
        })

    # Cosine similarity matrix
    n = len(doc_ids)
    sim_matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            sim_matrix[i][j] = round(cosine_similarity(tfidf_matrix_raw[i], tfidf_matrix_raw[j]), 4)

    return TFIDFResult(
        vocabulary=vocab,
        tf_table=tf_table,
        idf_table=idf_table,
        tfidf_matrix=tfidf_matrix,
        top_terms_per_doc=top_terms_per_doc,
        cosine_similarity_matrix=sim_matrix,
        document_ids=doc_ids,
    )


def query_documents(
    result: TFIDFResult,
    query: str,
    params: dict[str, Any],
    doc_vecs: list[list[float]],
    vocab: list[str],
) -> list[dict[str, Any]]:
    query_tokens = tokenize_for_tfidf(query, params)
    query_tf = compute_tf(query_tokens, params.get("tf_scheme", "raw"))
    # use existing IDF (no smoothing re-computed for query)
    idf_map = {row["term"]: row["idf"] for row in result.idf_table}
    q_vec = [query_tf.get(term, 0.0) * idf_map.get(term, 0.0) for term in vocab]
    q_vec = l2_normalize(q_vec)
    scored = [
        {"doc_id": did, "score": round(cosine_similarity(q_vec, dv), 4)}
        for did, dv in zip(result.document_ids, doc_vecs)
    ]
    return sorted(scored, key=lambda x: -x["score"])


# ──────────────────────────────────────────────
# Simulator
# ──────────────────────────────────────────────

class TFIDFSimulator(BaseSimulator):
    VERSION = "1.0.0"
    ALGORITHM_ID = "tfidf"
    DEMO_METADATA = CLASSICAL_DEMO_METADATA.get("tfidf")

    # ── validate ────────────────────────────────

    def validate(self, request: RunRequest) -> list[WarningEntry]:
        warnings: list[WarningEntry] = []
        docs = request.documents or []
        if request.text and not docs:
            # wrap single text as one document
            pass
        if len(docs) > 500:
            warnings.append(WarningEntry(
                code="CORPUS_TOO_LARGE",
                message="Corpus exceeds 500 documents; only the first 500 will be processed.",
                suggestion="Use the experiment mode for large corpora.",
            ))
        for doc in docs:
            if not doc.text.strip():
                warnings.append(WarningEntry(
                    code="EMPTY_DOCUMENT",
                    message=f"Document '{doc.id}' is empty and will produce a zero vector.",
                    field=f"documents[{doc.id}].text",
                ))
        top_n = request.parameters.get("top_n", 10)
        if not isinstance(top_n, int) or top_n < 1:
            warnings.append(WarningEntry(
                code="INVALID_TOP_N",
                message="top_n must be a positive integer; defaulting to 10.",
                field="parameters.top_n",
            ))
        return warnings

    # ── preprocess ──────────────────────────────

    def preprocess(self, request: RunRequest) -> dict[str, Any]:
        docs = request.documents or []
        if request.text and not docs:
            docs = [type("D", (), {"id": "doc_0", "text": request.text})()]  # type: ignore
        # Cap at 500
        docs = docs[:500]
        return {
            "documents": [{"id": d.id, "text": d.text} for d in docs],
            "params": request.parameters,
            "query": request.parameters.get("query"),
        }

    # ── run ─────────────────────────────────────

    def run(self, preprocessed: dict[str, Any], request: RunRequest) -> TFIDFResult:
        result = scratch_tfidf(preprocessed["documents"], preprocessed["params"])

        # Optional query scoring
        if preprocessed.get("query"):
            # Rebuild doc vecs from tfidf_matrix
            doc_vecs: dict[str, dict[str, float]] = {}
            for row in result.tfidf_matrix:
                doc_vecs.setdefault(row["doc_id"], {})[row["term"]] = row["score"]
            vocab = result.vocabulary
            vecs = [
                [doc_vecs.get(did, {}).get(t, 0.0) for t in vocab]
                for did in result.document_ids
            ]
            result.query_results = query_documents(
                result, preprocessed["query"], preprocessed["params"], vecs, vocab
            )
        return result

    # ── trace ───────────────────────────────────

    def trace(
        self, preprocessed: dict[str, Any], result: TFIDFResult, request: RunRequest
    ) -> dict[str, Any]:
        if request.trace_level == TraceLevel.NONE:
            return {}

        base: dict[str, Any] = {
            "document_count": len(result.document_ids),
            "vocabulary_size": len(result.vocabulary),
            "parameters": preprocessed["params"],
        }

        if request.trace_level == TraceLevel.SUMMARY:
            base["top_terms_per_doc"] = result.top_terms_per_doc
            return base

        # FULL
        return {
            **base,
            "tf_table": result.tf_table,
            "idf_table": result.idf_table,
            "tfidf_matrix": result.tfidf_matrix,
            "top_terms_per_doc": result.top_terms_per_doc,
            "cosine_similarity_matrix": result.cosine_similarity_matrix,
            "query_results": result.query_results,
            "formula": {
                "tf": "raw count (configurable via tf_scheme)",
                "idf": "log((1+N)/(1+df)) + 1  [smooth=True]  |  log(N/df) + 1  [smooth=False]",
                "tfidf": "tf * idf",
                "cosine": "dot(a,b) / (||a|| * ||b||)",
            },
        }

    # ── visualize ───────────────────────────────

    def visualize(
        self, trace: dict[str, Any], result: TFIDFResult, request: RunRequest
    ) -> list[VisualizationSpec]:
        specs: list[VisualizationSpec] = []

        # 1. TF-IDF heatmap (document × top-N terms)
        top_n = request.parameters.get("top_n", 10)
        top_terms = sorted(
            {row["term"]: row["score"] for row in result.tfidf_matrix}.items(),
            key=lambda x: -x[1]
        )[:top_n]
        top_term_names = [t for t, _ in top_terms]
        heatmap_data = []
        for doc_id in result.document_ids:
            scores = {row["term"]: row["score"] for row in result.tfidf_matrix if row["doc_id"] == doc_id}
            heatmap_data.append({
                "doc_id": doc_id,
                "values": [round(scores.get(t, 0.0), 4) for t in top_term_names],
            })
        specs.append(VisualizationSpec(
            type="heatmap",
            title="TF-IDF Matrix Heatmap",
            data={"terms": top_term_names, "rows": heatmap_data},
            config={"colorscale": "Blues"},
        ))

        # 2. Top-term bar chart (first document)
        if result.top_terms_per_doc:
            first = result.top_terms_per_doc[0]
            specs.append(VisualizationSpec(
                type="bar",
                title=f"Top Terms — {first['doc_id']}",
                data=first["terms"],
                config={"x": "term", "y": "score", "color": "#10b981"},
            ))

        # 3. Cosine similarity matrix
        specs.append(VisualizationSpec(
            type="heatmap",
            title="Document Cosine Similarity Matrix",
            data={
                "labels": result.document_ids,
                "matrix": result.cosine_similarity_matrix,
            },
            config={"colorscale": "Viridis", "symmetric": True},
        ))

        # 4. IDF distribution
        specs.append(VisualizationSpec(
            type="bar",
            title="IDF Values (top 30 terms)",
            data=sorted(result.idf_table, key=lambda x: -x["idf"])[:30],
            config={"x": "term", "y": "idf", "color": "#f59e0b"},
        ))

        if result.query_results:
            specs.append(VisualizationSpec(
                type="bar",
                title="Query–Document Cosine Similarity",
                data=result.query_results,
                config={"x": "doc_id", "y": "score", "color": "#6366f1"},
            ))

        return specs

    # ── serialize ───────────────────────────────

    def serialize_result(self, result: TFIDFResult) -> dict[str, Any]:
        return {
            "document_count": len(result.document_ids),
            "vocabulary_size": len(result.vocabulary),
            "top_terms_per_doc": result.top_terms_per_doc,
            "cosine_similarity_matrix": result.cosine_similarity_matrix,
            "query_results": result.query_results,
        }
