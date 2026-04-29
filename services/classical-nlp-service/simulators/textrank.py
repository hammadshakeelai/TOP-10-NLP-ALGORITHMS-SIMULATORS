"""
TextRank Simulator — TR-001 through TR-004.

Implements both keyword extraction and extractive summarization.
Uses networkx for graph construction and PageRank.

Keyword mode:  word co-occurrence graph → PageRank → top-N words
Summary mode:  sentence similarity graph → PageRank → top-N sentences

Reference: Mihalcea & Tarau, EMNLP 2004.
"""
from __future__ import annotations

import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .base import BaseSimulator

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages"))
from shared_schemas import RunRequest, TraceLevel, VisualizationSpec, WarningEntry

from .demo_metadata import CLASSICAL_DEMO_METADATA

try:
    import networkx as nx
    HAS_NX = True
except ImportError:
    HAS_NX = False


STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "should",
    "may", "might", "can", "could", "of", "in", "to", "for", "on", "with",
    "at", "by", "from", "and", "or", "but", "not", "this", "that", "it",
    "its", "i", "we", "you", "he", "she", "they", "their", "them", "our",
}

SENTENCE_RE = re.compile(r'(?<=[.!?])\s+')
WORD_RE = re.compile(r'\b[a-z]+\b')


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_RE.split(text.strip()) if s.strip()]


def tokenize(text: str) -> list[str]:
    return [w for w in WORD_RE.findall(text.lower()) if w not in STOPWORDS and len(w) > 2]


def cosine_sim(v1: list[float], v2: list[float]) -> float:
    a, b = np.array(v1), np.array(v2)
    n = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / n) if n > 0 else 0.0


def sentence_overlap_similarity(s1: str, s2: str) -> float:
    """Normalized word overlap — used when no embeddings available."""
    t1 = set(tokenize(s1))
    t2 = set(tokenize(s2))
    if not t1 or not t2:
        return 0.0
    overlap = len(t1 & t2)
    norm = math.log(len(t1) + 1) + math.log(len(t2) + 1)
    return overlap / norm if norm > 0 else 0.0


def power_iteration_pagerank(
    adjacency: dict[str, dict[str, float]],
    nodes: list[str],
    damping: float = 0.85,
    max_iter: int = 100,
    tol: float = 1e-4,
) -> tuple[dict[str, float], list[dict[str, Any]]]:
    """
    Pure-Python PageRank so that iteration steps are available for visualization.
    Returns (final_scores, convergence_log).
    """
    n = len(nodes)
    scores = {node: 1.0 / n for node in nodes}
    convergence_log: list[dict[str, Any]] = []

    for iteration in range(max_iter):
        new_scores: dict[str, float] = {}
        for node in nodes:
            rank_sum = 0.0
            for other in nodes:
                weight = adjacency.get(other, {}).get(node, 0.0)
                out_weight = sum(adjacency.get(other, {}).values())
                if out_weight > 0:
                    rank_sum += weight / out_weight * scores[other]
            new_scores[node] = (1 - damping) / n + damping * rank_sum

        delta = max(abs(new_scores[n_] - scores[n_]) for n_ in nodes)
        convergence_log.append({"iteration": iteration + 1, "max_delta": round(delta, 6)})
        scores = new_scores

        if delta < tol:
            break

    return scores, convergence_log


@dataclass
class TextRankResult:
    mode: str
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]
    scores: dict[str, float]
    ranked_output: list[dict[str, Any]]
    convergence_log: list[dict[str, Any]]
    summary: str | None = None
    top_n: int = 5


class TextRankSimulator(BaseSimulator):
    VERSION = "1.0.0"
    ALGORITHM_ID = "textrank"
    DEMO_METADATA = CLASSICAL_DEMO_METADATA.get("textrank")

    def validate(self, request: RunRequest) -> list[WarningEntry]:
        warnings: list[WarningEntry] = []
        text = request.text or ""
        mode = request.parameters.get("mode", "keyword")

        if len(text.strip()) < 30:
            warnings.append(WarningEntry(
                code="TEXT_TOO_SHORT",
                message="Text is too short for meaningful TextRank results.",
                suggestion="Provide at least 3 sentences for summarization or one paragraph for keyword extraction.",
            ))

        sentences = split_sentences(text)
        if mode == "summary" and len(sentences) < 3:
            warnings.append(WarningEntry(
                code="TOO_FEW_SENTENCES",
                message=f"Only {len(sentences)} sentence(s) found. Summarization needs at least 3.",
                field="text",
            ))

        damping = request.parameters.get("damping", 0.85)
        if not isinstance(damping, (int, float)) or not (0 < damping < 1):
            warnings.append(WarningEntry(
                code="INVALID_DAMPING",
                message="damping must be in (0, 1); defaulting to 0.85.",
                field="parameters.damping",
            ))
        return warnings

    def preprocess(self, request: RunRequest) -> dict[str, Any]:
        return {
            "text": request.text or "",
            "params": request.parameters,
            "sentences": split_sentences(request.text or ""),
        }

    def run(self, preprocessed: dict[str, Any], request: RunRequest) -> TextRankResult:
        text: str = preprocessed["text"]
        params: dict[str, Any] = preprocessed["params"]
        sentences: list[str] = preprocessed["sentences"]

        mode: str = params.get("mode", "keyword")
        window_size: int = params.get("window_size", 2)
        damping: float = float(params.get("damping", 0.85))
        damping = damping if 0 < damping < 1 else 0.85
        tol: float = float(params.get("convergence_tol", 1e-4))
        top_n: int = params.get("top_n", 5)

        if mode == "keyword":
            return self._keyword_mode(text, damping, tol, top_n, window_size)
        else:
            return self._summary_mode(sentences, damping, tol, top_n)

    def _keyword_mode(
        self, text: str, damping: float, tol: float, top_n: int, window_size: int
    ) -> TextRankResult:
        words = tokenize(text)
        vocab = sorted(set(words))

        adjacency: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        for i, word in enumerate(words):
            window = words[max(0, i - window_size): i] + words[i + 1: i + window_size + 1]
            for w in window:
                adjacency[word][w] += 1.0
                adjacency[w][word] += 1.0

        scores, convergence_log = power_iteration_pagerank(
            {k: dict(v) for k, v in adjacency.items()}, vocab, damping=damping, tol=tol
        )

        ranked = sorted(scores.items(), key=lambda x: -x[1])[:top_n]
        ranked_output = [{"rank": i + 1, "word": w, "score": round(s, 6)} for i, (w, s) in enumerate(ranked)]

        nodes = [{"id": w, "score": round(scores.get(w, 0), 6)} for w in vocab]
        edges = [
            {"source": src, "target": tgt, "weight": round(wt, 4)}
            for src, targets in adjacency.items()
            for tgt, wt in targets.items()
            if src < tgt
        ]

        return TextRankResult(
            mode="keyword",
            nodes=nodes,
            edges=edges,
            scores={w: round(s, 6) for w, s in scores.items()},
            ranked_output=ranked_output,
            convergence_log=convergence_log,
            top_n=top_n,
        )

    def _summary_mode(
        self, sentences: list[str], damping: float, tol: float, top_n: int
    ) -> TextRankResult:
        n = len(sentences)
        adjacency: dict[str, dict[str, float]] = defaultdict(dict)
        edges: list[dict[str, Any]] = []

        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                sim = sentence_overlap_similarity(sentences[i], sentences[j])
                if sim > 0:
                    adjacency[f"s{i}"][f"s{j}"] = sim
                    if i < j:
                        edges.append({"source": f"s{i}", "target": f"s{j}", "weight": round(sim, 4)})

        node_ids = [f"s{i}" for i in range(n)]
        scores, convergence_log = power_iteration_pagerank(
            {k: dict(v) for k, v in adjacency.items()}, node_ids, damping=damping, tol=tol
        )

        ranked = sorted(scores.items(), key=lambda x: -x[1])[:top_n]
        ranked_output = [
            {
                "rank": i + 1,
                "sentence_id": sid,
                "sentence": sentences[int(sid[1:])],
                "score": round(s, 6),
            }
            for i, (sid, s) in enumerate(ranked)
        ]

        # Summary = top sentences in original order
        top_ids = {sid for sid, _ in ranked}
        summary_sents = [s for i, s in enumerate(sentences) if f"s{i}" in top_ids]
        summary = " ".join(summary_sents)

        nodes = [
            {"id": f"s{i}", "label": sentences[i][:60] + "…" if len(sentences[i]) > 60 else sentences[i],
             "score": round(scores.get(f"s{i}", 0), 6)}
            for i in range(n)
        ]

        return TextRankResult(
            mode="summary",
            nodes=nodes,
            edges=edges,
            scores={k: round(v, 6) for k, v in scores.items()},
            ranked_output=ranked_output,
            convergence_log=convergence_log,
            summary=summary,
            top_n=top_n,
        )

    def trace(self, preprocessed: Any, result: TextRankResult, request: RunRequest) -> dict[str, Any]:
        if request.trace_level == TraceLevel.NONE:
            return {}
        base: dict[str, Any] = {
            "mode": result.mode,
            "node_count": len(result.nodes),
            "edge_count": len(result.edges),
            "iterations": len(result.convergence_log),
            "ranked_output": result.ranked_output,
        }
        if result.summary:
            base["summary"] = result.summary
        if request.trace_level == TraceLevel.SUMMARY:
            return base
        return {
            **base,
            "convergence_log": result.convergence_log,
            "all_scores": result.scores,
            "formula": "PR(V) = (1-d)/N + d × Σ (wji / Σ_k wjk) × PR(Vj)",
        }

    def visualize(self, trace: dict[str, Any], result: TextRankResult, request: RunRequest) -> list[VisualizationSpec]:
        specs: list[VisualizationSpec] = []

        # Graph visualization
        specs.append(VisualizationSpec(
            type="graph",
            title=f"TextRank Graph — {result.mode.capitalize()} Mode",
            data={"nodes": result.nodes, "edges": result.edges},
            config={"layout": "force", "node_size_by": "score"},
        ))

        # Ranked output bar/table
        specs.append(VisualizationSpec(
            type="bar",
            title="TextRank Scores",
            data=[{"label": r.get("word") or r.get("sentence_id"), "score": r["score"]}
                  for r in result.ranked_output],
            config={"x": "label", "y": "score", "color": "#8b5cf6", "horizontal": True},
        ))

        # Convergence plot
        if result.convergence_log:
            specs.append(VisualizationSpec(
                type="line",
                title="Score Convergence",
                data=result.convergence_log,
                config={"x": "iteration", "y": "max_delta"},
            ))

        # Sentence rank table (summary mode)
        if result.mode == "summary":
            specs.append(VisualizationSpec(
                type="table",
                title="Sentence Rankings",
                data=result.ranked_output,
            ))

        return specs

    def serialize_result(self, result: TextRankResult) -> dict[str, Any]:
        out: dict[str, Any] = {
            "mode": result.mode,
            "ranked_output": result.ranked_output,
            "node_count": len(result.nodes),
            "edge_count": len(result.edges),
        }
        if result.summary:
            out["summary"] = result.summary
        return out
