"""
Word Embeddings Simulator (Word2Vec / GloVe) — WE-001 through WE-004.

Learning mode: toy co-occurrence matrix + SVD projection (no external weights needed)
Experiment mode: gensim KeyedVectors on a pretrained model (glove-wiki-gigaword-50, etc.)

Outputs:
  - vector values for target word
  - cosine similarity nearest neighbors
  - analogy result (A:B :: C:?)
  - 2D PCA/TSNE projection for scatter plot
"""
from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .base import BaseSimulator

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages"))
from shared_schemas import RunRequest, TraceLevel, VisualizationSpec, WarningEntry

from .demo_metadata import TRANSFORMER_DEMO_METADATA


# ──────────────────────────────────────────────
# Toy SVD-based embeddings (learning mode)
# ──────────────────────────────────────────────

STOPWORDS = {"a", "an", "the", "is", "are", "was", "were", "in", "on", "at",
             "to", "for", "of", "with", "by", "and", "or", "but", "not", "it", "its"}

WORD_RE = re.compile(r'\b[a-zA-Z]+\b')


def build_cooccurrence_matrix(
    tokens: list[str], vocab: list[str], window: int = 2
) -> np.ndarray:
    idx = {w: i for i, w in enumerate(vocab)}
    n = len(vocab)
    matrix = np.zeros((n, n), dtype=float)
    for i, word in enumerate(tokens):
        if word not in idx:
            continue
        context = tokens[max(0, i - window): i] + tokens[i + 1: i + window + 1]
        for ctx in context:
            if ctx in idx:
                matrix[idx[word], idx[ctx]] += 1.0
    return matrix


def svd_embeddings(matrix: np.ndarray, dim: int = 50) -> np.ndarray:
    U, s, _ = np.linalg.svd(matrix, full_matrices=False)
    return U[:, :dim] * np.sqrt(s[:dim])


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def pca_2d(vectors: np.ndarray) -> np.ndarray:
    """Simple 2-component PCA without sklearn."""
    centered = vectors - vectors.mean(axis=0)
    cov = np.cov(centered.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    idx = np.argsort(eigenvalues)[::-1]
    return centered @ eigenvectors[:, idx[:2]]


@dataclass
class EmbeddingResult:
    model_type: str          # toy_svd | word2vec | glove
    target_word: str
    vector: list[float]
    nearest_neighbors: list[dict[str, Any]]
    analogy_result: dict[str, Any] | None
    projection_2d: list[dict[str, Any]]
    cooccurrence_snippet: list[dict[str, Any]]


class WordEmbeddingsSimulator(BaseSimulator):
    VERSION = "1.0.0"
    ALGORITHM_ID = "word_embeddings"
    DEMO_METADATA = TRANSFORMER_DEMO_METADATA.get("word_embeddings")

    def validate(self, request: RunRequest) -> list[WarningEntry]:
        warnings = []
        target = request.parameters.get("target_word", "")
        if not target:
            warnings.append(WarningEntry(
                code="MISSING_TARGET_WORD",
                message="No target_word specified in parameters.",
                field="parameters.target_word",
                suggestion="Set parameters.target_word to a word you want to inspect.",
            ))
        model = request.parameters.get("model_type", "toy_svd")
        if model not in ("toy_svd", "word2vec", "glove"):
            warnings.append(WarningEntry(
                code="UNKNOWN_MODEL",
                message=f"model_type '{model}' not recognized. Defaulting to 'toy_svd'.",
                field="parameters.model_type",
            ))
        return warnings

    def preprocess(self, request: RunRequest) -> dict[str, Any]:
        corpus_text = request.text or " ".join(d.text for d in (request.documents or []))
        raw_tokens = WORD_RE.findall(corpus_text.lower())
        tokens = [w for w in raw_tokens if w not in STOPWORDS and len(w) > 2]
        freq = Counter(tokens)
        min_count = request.parameters.get("min_count", 2)
        vocab = sorted([w for w, c in freq.items() if c >= min_count])
        return {
            "tokens": tokens,
            "vocab": vocab,
            "params": request.parameters,
            "corpus_text": corpus_text,
        }

    def run(self, preprocessed: dict[str, Any], request: RunRequest) -> EmbeddingResult:
        tokens: list[str] = preprocessed["tokens"]
        vocab: list[str] = preprocessed["vocab"]
        params = preprocessed["params"]

        dim = min(params.get("vector_dim", 50), len(vocab) - 1 if len(vocab) > 1 else 1)
        window = params.get("context_window", 2)
        target = params.get("target_word", "").lower()
        top_k = params.get("top_k_neighbors", 10)
        model_type = params.get("model_type", "toy_svd")

        if model_type in ("word2vec", "glove"):
            return self._pretrained_mode(target, top_k, params, model_type)

        # Toy SVD mode
        if not vocab:
            return EmbeddingResult(
                model_type="toy_svd", target_word=target, vector=[],
                nearest_neighbors=[], analogy_result=None, projection_2d=[],
                cooccurrence_snippet=[]
            )

        cooc = build_cooccurrence_matrix(tokens, vocab, window=window)
        embeddings = svd_embeddings(cooc, dim=dim)  # shape (|vocab|, dim)
        idx_map = {w: i for i, w in enumerate(vocab)}

        # Target vector
        target_vec = embeddings[idx_map[target]] if target in idx_map else np.zeros(dim)

        # Nearest neighbors
        sims = [
            {"word": w, "similarity": round(cosine_similarity(target_vec, embeddings[idx_map[w]]), 4)}
            for w in vocab if w != target
        ]
        sims.sort(key=lambda x: -x["similarity"])
        neighbors = sims[:top_k]

        # Analogy (A:B :: C:?)
        analogy_result = None
        analogy = params.get("analogy")  # e.g. {"a": "king", "b": "man", "c": "woman"}
        if analogy and all(analogy.get(k, "").lower() in idx_map for k in ("a", "b", "c")):
            a = embeddings[idx_map[analogy["a"].lower()]]
            b = embeddings[idx_map[analogy["b"].lower()]]
            c = embeddings[idx_map[analogy["c"].lower()]]
            query = a - b + c
            cands = [
                {"word": w, "score": round(cosine_similarity(query, embeddings[idx_map[w]]), 4)}
                for w in vocab if w not in (analogy["a"].lower(), analogy["b"].lower(), analogy["c"].lower())
            ]
            cands.sort(key=lambda x: -x["score"])
            analogy_result = {
                "query": f"{analogy['a']}:{analogy['b']} :: {analogy['c']}:?",
                "answer": cands[0]["word"] if cands else "?",
                "candidates": cands[:5],
            }

        # 2D projection
        # Project exactly the words that made it into display_vecs — the word
        # list and the vector rows must stay index-aligned even when the
        # target word is missing from the vocabulary.
        display_words = list({target} | {n["word"] for n in neighbors[:20]})
        projected_words = [w for w in display_words if w in idx_map]
        display_vecs = np.array([embeddings[idx_map[w]] for w in projected_words])
        if len(projected_words) >= 2:
            proj = pca_2d(display_vecs)
            projection_2d = [
                {"word": w, "x": round(float(proj[i, 0]), 4), "y": round(float(proj[i, 1]), 4)}
                for i, w in enumerate(projected_words)
            ]
        else:
            projection_2d = []

        # Co-occurrence snippet (top 10 pairs involving target)
        if target in idx_map:
            ti = idx_map[target]
            cooc_pairs = [
                {"word": vocab[j], "cooccurrence": int(cooc[ti, j])}
                for j in range(len(vocab)) if j != ti and cooc[ti, j] > 0
            ]
            cooc_pairs.sort(key=lambda x: -x["cooccurrence"])
            cooc_snippet = cooc_pairs[:10]
        else:
            cooc_snippet = []

        return EmbeddingResult(
            model_type="toy_svd",
            target_word=target,
            vector=[round(float(v), 4) for v in target_vec],
            nearest_neighbors=neighbors,
            analogy_result=analogy_result,
            projection_2d=projection_2d,
            cooccurrence_snippet=cooc_snippet,
        )

    def _pretrained_mode(self, target: str, top_k: int, params: dict[str, Any], model_type: str) -> EmbeddingResult:
        """Load a gensim pretrained model (requires gensim and downloaded vectors)."""
        try:
            import gensim.downloader as api
            model_name = {
                "word2vec": "word2vec-google-news-300",
                "glove": "glove-wiki-gigaword-50",
            }.get(model_type, "glove-wiki-gigaword-50")
            wv = api.load(model_name)

            if target not in wv:
                return EmbeddingResult(
                    model_type=model_type, target_word=target, vector=[],
                    nearest_neighbors=[], analogy_result=None, projection_2d=[],
                    cooccurrence_snippet=[],
                )

            vector = [round(float(v), 4) for v in wv[target]]
            neighbors = [{"word": w, "similarity": round(float(s), 4)} for w, s in wv.most_similar(target, topn=top_k)]
            projection_2d = []

            return EmbeddingResult(
                model_type=model_type,
                target_word=target,
                vector=vector,
                nearest_neighbors=neighbors,
                analogy_result=None,
                projection_2d=projection_2d,
                cooccurrence_snippet=[],
            )
        except Exception as e:
            return EmbeddingResult(
                model_type=f"{model_type}_unavailable",
                target_word=target, vector=[], nearest_neighbors=[],
                analogy_result={"error": str(e)},
                projection_2d=[], cooccurrence_snippet=[],
            )

    def trace(self, preprocessed: Any, result: EmbeddingResult, request: RunRequest) -> dict[str, Any]:
        if request.trace_level == TraceLevel.NONE:
            return {}
        base: dict[str, Any] = {
            "model_type": result.model_type,
            "target_word": result.target_word,
            "vector_dim": len(result.vector),
            "nearest_neighbors": result.nearest_neighbors,
        }
        if request.trace_level == TraceLevel.SUMMARY:
            return base
        return {
            **base,
            "vector": result.vector,
            "analogy_result": result.analogy_result,
            "cooccurrence_snippet": result.cooccurrence_snippet,
            "projection_2d_count": len(result.projection_2d),
        }

    def visualize(self, trace: dict[str, Any], result: EmbeddingResult, request: RunRequest) -> list[VisualizationSpec]:
        specs: list[VisualizationSpec] = []

        # 2D scatter
        if result.projection_2d:
            specs.append(VisualizationSpec(
                type="scatter",
                title="2D Word Embedding Projection (PCA)",
                data=result.projection_2d,
                config={"x": "x", "y": "y", "label": "word", "highlight": result.target_word},
            ))

        # Nearest neighbor similarity bars
        specs.append(VisualizationSpec(
            type="bar",
            title=f"Nearest Neighbors of '{result.target_word}'",
            data=result.nearest_neighbors,
            config={"x": "word", "y": "similarity", "color": "#6366f1"},
        ))

        # Co-occurrence table
        if result.cooccurrence_snippet:
            specs.append(VisualizationSpec(
                type="bar",
                title="Co-occurrence Counts",
                data=result.cooccurrence_snippet,
                config={"x": "word", "y": "cooccurrence", "color": "#f59e0b"},
            ))

        # Analogy equation
        if result.analogy_result and "error" not in result.analogy_result:
            specs.append(VisualizationSpec(
                type="table",
                title="Analogy Result",
                data=result.analogy_result.get("candidates", []),
            ))

        return specs

    def serialize_result(self, result: EmbeddingResult) -> dict[str, Any]:
        return {
            "model_type": result.model_type,
            "target_word": result.target_word,
            "vector_preview": result.vector[:10],
            "nearest_neighbors": result.nearest_neighbors,
            "analogy_result": result.analogy_result,
        }
