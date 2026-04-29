"""
RAKE Keyword Extraction Simulator — RK-001 through RK-004.

Fully from-scratch implementation of Rapid Automatic Keyword Extraction.
Algorithm: Rose et al. 2010.

Pipeline:
  1. Split text into candidate phrases using stopword + punctuation delimiters
  2. Build word co-occurrence graph within each phrase
  3. Score each word: degree(w) / freq(w)
  4. Score each phrase: sum of word scores
  5. Return ranked phrases with full scoring trace
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any

from .base import BaseSimulator

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages"))
from shared_schemas import RunRequest, TraceLevel, VisualizationSpec, WarningEntry

from .demo_metadata import CLASSICAL_DEMO_METADATA


DEFAULT_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an",
    "and", "any", "are", "aren't", "as", "at", "be", "because", "been",
    "before", "being", "below", "between", "both", "but", "by", "can",
    "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does",
    "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "get", "gets", "got", "had", "hadn't", "has",
    "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
    "her", "here", "here's", "hers", "herself", "him", "himself", "his",
    "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into",
    "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more",
    "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off",
    "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd",
    "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
    "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
    "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until",
    "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've",
    "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "why", "why's",
    "will", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll",
    "you're", "you've", "your", "yours", "yourself", "yourselves",
}


@dataclass
class RAKEResult:
    candidate_phrases: list[dict[str, Any]]
    word_scores: dict[str, dict[str, float]]   # {word: {freq, degree, score}}
    cooccurrence_graph: list[dict[str, Any]]   # edges for visualization
    ranked_keywords: list[dict[str, Any]]
    top_n: int


class RAKESimulator(BaseSimulator):
    VERSION = "1.0.0"
    ALGORITHM_ID = "rake"
    DEMO_METADATA = CLASSICAL_DEMO_METADATA.get("rake")

    def validate(self, request: RunRequest) -> list[WarningEntry]:
        warnings: list[WarningEntry] = []
        text = request.text or ""
        if len(text.strip()) < 20:
            warnings.append(WarningEntry(
                code="TEXT_TOO_SHORT",
                message="Text is very short. RAKE may produce few or no candidate phrases.",
                suggestion="Provide at least one full sentence.",
            ))
        min_chars = request.parameters.get("min_phrase_chars", 0)
        if isinstance(min_chars, int) and min_chars < 0:
            warnings.append(WarningEntry(
                code="INVALID_MIN_CHARS",
                message="min_phrase_chars must be >= 0; defaulting to 0.",
                field="parameters.min_phrase_chars",
            ))
        return warnings

    def preprocess(self, request: RunRequest) -> dict[str, Any]:
        text = request.text or ""
        params = request.parameters
        # Merge user stopwords with defaults
        user_sw = set(w.lower() for w in params.get("stopwords", []))
        stopwords = DEFAULT_STOPWORDS | user_sw
        return {"text": text, "stopwords": stopwords, "params": params}

    def run(self, preprocessed: dict[str, Any], request: RunRequest) -> RAKEResult:
        text: str = preprocessed["text"]
        stopwords: set[str] = preprocessed["stopwords"]
        params: dict[str, Any] = preprocessed["params"]

        min_len: int = params.get("min_phrase_words", 1)
        max_len: int = params.get("max_phrase_words", 5)
        min_chars: int = params.get("min_phrase_chars", 0)
        min_score: float = params.get("min_score", 0.0)
        top_n: int = params.get("top_n", 10)
        handle_punct: bool = params.get("handle_punctuation", True)

        # Split text into sentences, then into candidate phrases
        if handle_punct:
            sentence_delimiters = re.compile(r'[.!?,;:\n\t\(\)\[\]\"\']+')
        else:
            sentence_delimiters = re.compile(r'[\n]+')

        phrases_raw = sentence_delimiters.split(text)

        # Tokenize each phrase, split on stopwords
        def tokenize_phrase(phrase: str) -> list[str]:
            words = re.findall(r'[a-zA-Z]+(?:\'[a-zA-Z]+)?', phrase.lower())
            return words

        candidate_phrases: list[list[str]] = []
        for phrase in phrases_raw:
            words = tokenize_phrase(phrase)
            current: list[str] = []
            for word in words:
                if word in stopwords:
                    if min_len <= len(current) <= max_len:
                        if len(" ".join(current)) >= min_chars:
                            candidate_phrases.append(current[:])
                    current = []
                else:
                    current.append(word)
            if min_len <= len(current) <= max_len:
                if len(" ".join(current)) >= min_chars:
                    candidate_phrases.append(current[:])

        if not candidate_phrases:
            return RAKEResult(
                candidate_phrases=[],
                word_scores={},
                cooccurrence_graph=[],
                ranked_keywords=[],
                top_n=top_n,
            )

        # Word frequency
        all_words = [w for phrase in candidate_phrases for w in phrase]
        word_freq = Counter(all_words)

        # Word degree (total co-occurrences within phrases)
        word_degree: dict[str, int] = defaultdict(int)
        for phrase in candidate_phrases:
            deg = len(phrase) - 1
            for word in phrase:
                word_degree[word] += deg + 1  # includes self

        # Word score = degree / frequency
        word_scores: dict[str, dict[str, float]] = {}
        for word in word_freq:
            freq = word_freq[word]
            deg = word_degree[word]
            score = deg / freq if freq > 0 else 0.0
            word_scores[word] = {
                "frequency": freq,
                "degree": deg,
                "score": round(score, 4),
            }

        # Phrase scores
        phrase_score_list: list[dict[str, Any]] = []
        seen: set[str] = set()
        for phrase in candidate_phrases:
            phrase_str = " ".join(phrase)
            if phrase_str in seen:
                continue
            seen.add(phrase_str)
            score = sum(word_scores[w]["score"] for w in phrase)
            phrase_score_list.append({
                "phrase": phrase_str,
                "words": phrase,
                "score": round(score, 4),
                "word_scores": {w: word_scores[w]["score"] for w in phrase},
            })

        # Filter by min_score and rank
        ranked = [p for p in phrase_score_list if p["score"] >= min_score]
        ranked = sorted(ranked, key=lambda x: -x["score"])
        for i, item in enumerate(ranked):
            item["rank"] = i + 1

        # Co-occurrence graph edges (for visualization)
        edge_counts: dict[tuple[str, str], int] = defaultdict(int)
        for phrase in candidate_phrases:
            for i, w1 in enumerate(phrase):
                for j, w2 in enumerate(phrase):
                    if i != j:
                        edge = tuple(sorted([w1, w2]))
                        edge_counts[edge] += 1  # type: ignore
        cooccurrence_graph = [
            {"source": e[0], "target": e[1], "weight": cnt}
            for e, cnt in sorted(edge_counts.items(), key=lambda x: -x[1])[:50]
        ]

        return RAKEResult(
            candidate_phrases=phrase_score_list,
            word_scores=word_scores,
            cooccurrence_graph=cooccurrence_graph,
            ranked_keywords=ranked[:top_n],
            top_n=top_n,
        )

    def trace(self, preprocessed: Any, result: RAKEResult, request: RunRequest) -> dict[str, Any]:
        if request.trace_level == TraceLevel.NONE:
            return {}
        base = {
            "candidate_phrase_count": len(result.candidate_phrases),
            "unique_words": len(result.word_scores),
            "top_n": result.top_n,
        }
        if request.trace_level == TraceLevel.SUMMARY:
            base["ranked_keywords"] = result.ranked_keywords
            return base
        return {
            **base,
            "ranked_keywords": result.ranked_keywords,
            "word_scores": result.word_scores,
            "candidate_phrases": result.candidate_phrases,
            "formula": "phrase_score = Σ word_score(w)  where  word_score(w) = degree(w) / freq(w)",
        }

    def visualize(self, trace: dict[str, Any], result: RAKEResult, request: RunRequest) -> list[VisualizationSpec]:
        specs: list[VisualizationSpec] = []

        # Ranked phrase bar chart
        specs.append(VisualizationSpec(
            type="bar",
            title="RAKE Keyword Scores",
            data=[{"phrase": r["phrase"], "score": r["score"]} for r in result.ranked_keywords],
            config={"x": "phrase", "y": "score", "color": "#f59e0b", "horizontal": True},
        ))

        # Scoring table
        specs.append(VisualizationSpec(
            type="table",
            title="Phrase Scoring Breakdown",
            data=result.ranked_keywords,
        ))

        # Word co-occurrence mini-graph
        specs.append(VisualizationSpec(
            type="graph",
            title="Word Co-occurrence Graph",
            data={
                "nodes": [{"id": w, "score": v["score"]} for w, v in result.word_scores.items()],
                "edges": result.cooccurrence_graph,
            },
        ))

        return specs

    def serialize_result(self, result: RAKEResult) -> dict[str, Any]:
        return {
            "ranked_keywords": result.ranked_keywords,
            "candidate_phrase_count": len(result.candidate_phrases),
            "unique_words": len(result.word_scores),
        }
