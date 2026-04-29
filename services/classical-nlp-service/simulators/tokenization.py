"""
Tokenization Simulator — implements TK-001 through TK-004 from the SRS.

Modes:
  whitespace  — split on whitespace only
  regex       — configurable regex pattern
  bpe_demo    — toy BPE merge demonstration (educational, not production BPE)
  wordpiece   — toy WordPiece segmentation (educational)

All modes return character offsets so the frontend can highlight original spans.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from .base import BaseSimulator

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../packages"))
from shared_schemas import RunRequest, TraceLevel, VisualizationSpec, WarningEntry

from .demo_metadata import CLASSICAL_DEMO_METADATA


# ──────────────────────────────────────────────
# Data structures
# ──────────────────────────────────────────────

@dataclass
class Token:
    index: int
    text: str
    normalized: str
    start: int          # character offset in original text
    end: int
    sentence_id: int
    is_subword: bool = False
    subword_of: str | None = None
    pos: str | None = None   # placeholder; real POS requires spaCy


@dataclass
class TokenizationResult:
    tokens: list[Token]
    cleaned_text: str
    vocabulary: list[str]
    frequency: dict[str, int]
    subword_merges: list[dict[str, Any]] = field(default_factory=list)  # BPE trace
    sentence_boundaries: list[int] = field(default_factory=list)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')
DEFAULT_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "must", "can", "could", "of", "in", "to",
    "for", "on", "with", "at", "by", "from", "and", "or", "but", "not",
    "this", "that", "it", "its", "i", "we", "you", "he", "she", "they",
}


def split_sentences(text: str) -> list[str]:
    parts = SENTENCE_SPLIT_RE.split(text.strip())
    return [p.strip() for p in parts if p.strip()]


def simple_stem(word: str) -> str:
    """Porter-style minimal stemmer for demo purposes."""
    suffixes = ["ing", "tion", "ness", "ment", "ly", "ed", "er", "est", "s"]
    for suffix in suffixes:
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def normalize_token(text: str, lowercase: bool, stemming: bool, lemmatization: bool) -> str:
    result = text.lower() if lowercase else text
    if stemming:
        result = simple_stem(result)
    # lemmatization stub — real impl uses spaCy; for now mirrors stemming
    if lemmatization and not stemming:
        result = simple_stem(result)
    return result


# ──────────────────────────────────────────────
# Tokenizers
# ──────────────────────────────────────────────

def whitespace_tokenize(
    text: str, params: dict[str, Any]
) -> list[tuple[str, int, int]]:
    """Returns (token_text, start_char, end_char)."""
    tokens = []
    for m in re.finditer(r'\S+', text):
        tokens.append((m.group(), m.start(), m.end()))
    return tokens


def regex_tokenize(
    text: str, params: dict[str, Any]
) -> list[tuple[str, int, int]]:
    pattern = params.get("regex_pattern", r'\b\w+\b')
    try:
        compiled = re.compile(pattern)
    except re.error:
        compiled = re.compile(r'\b\w+\b')
    return [(m.group(), m.start(), m.end()) for m in compiled.finditer(text)]


def bpe_demo_tokenize(
    text: str, params: dict[str, Any]
) -> tuple[list[tuple[str, int, int]], list[dict[str, Any]]]:
    """
    Toy BPE: starts with character-level tokens, applies a fixed number of merges
    on the most frequent adjacent pair. Returns tokens + merge trace for visualization.
    """
    num_merges: int = params.get("bpe_num_merges", 10)

    # character-level vocabulary
    words = re.findall(r'\S+', text)
    vocab: dict[str, int] = Counter(
        " ".join(list(word) + ["</w>"]) for word in words
    )

    def get_pairs(vocab: dict[str, int]) -> Counter:
        pairs: Counter = Counter()
        for word, freq in vocab.items():
            symbols = word.split()
            for i in range(len(symbols) - 1):
                pairs[(symbols[i], symbols[i + 1])] += freq
        return pairs

    merges: list[dict[str, Any]] = []
    for step in range(num_merges):
        pairs = get_pairs(vocab)
        if not pairs:
            break
        best = pairs.most_common(1)[0][0]
        merges.append({"step": step + 1, "merge": f"{best[0]} {best[1]}", "frequency": pairs[best]})
        new_vocab: dict[str, int] = {}
        bigram = re.escape(" ".join(best))
        replacement = "".join(best)
        for word, freq in vocab.items():
            new_word = re.sub(bigram, replacement, word)
            new_vocab[new_word] = freq
        vocab = new_vocab

    # Convert final vocab back to token spans (approximate)
    raw_tokens = list(re.finditer(r'\S+', text))
    tokens: list[tuple[str, int, int]] = []
    for m in raw_tokens:
        word = m.group()
        word_repr = " ".join(list(word) + ["</w>"])
        # find matching final vocab entry
        for vw in vocab:
            if vw.replace(" ", "").replace("</w>", "") == word:
                word_repr = vw
                break
        parts = word_repr.replace("</w>", "").split()
        pos = m.start()
        for part in parts:
            tokens.append((part, pos, pos + len(part)))
            pos += len(part)

    return tokens, merges


def wordpiece_demo_tokenize(
    text: str, params: dict[str, Any]
) -> list[tuple[str, int, int, bool]]:
    """
    Toy WordPiece: uses a small hardcoded vocab to demonstrate ## continuation tokens.
    Production code uses HuggingFace tokenizers.
    """
    # Minimal demo vocab to illustrate subword splitting
    demo_vocab = {
        "nlp", "natural", "language", "processing", "transform", "##er", "##ers",
        "embed", "##ding", "##dings", "token", "##ize", "##ization", "##s",
        "learn", "##ing", "model", "##s", "text", "class", "##ify", "##ifier",
    }
    tokens: list[tuple[str, int, int, bool]] = []
    for m in re.finditer(r'\S+', text):
        word = m.group().lower().rstrip(".,!?;:")
        start = m.start()
        if word in demo_vocab:
            tokens.append((word, start, start + len(word), False))
        else:
            # greedy longest-match subword split
            remaining = word
            offset = start
            first = True
            while remaining:
                found = False
                for end in range(len(remaining), 0, -1):
                    candidate = remaining[:end]
                    key = candidate if first else f"##{candidate}"
                    if key in demo_vocab or candidate in demo_vocab:
                        tok = candidate if first else f"##{candidate}"
                        tokens.append((tok, offset, offset + end, not first))
                        offset += end
                        remaining = remaining[end:]
                        first = False
                        found = True
                        break
                if not found:
                    tokens.append((remaining if first else f"##{remaining}", offset, offset + len(remaining), not first))
                    break
    return tokens


# ──────────────────────────────────────────────
# Simulator
# ──────────────────────────────────────────────

class TokenizationSimulator(BaseSimulator):
    VERSION = "1.0.0"
    ALGORITHM_ID = "tokenization"
    DEMO_METADATA = CLASSICAL_DEMO_METADATA.get("tokenization")

    # ── validate ────────────────────────────────

    def validate(self, request: RunRequest) -> list[WarningEntry]:
        warnings = []
        text = request.text or ""
        if len(text) > 50_000:
            warnings.append(WarningEntry(
                code="INPUT_TOO_LONG",
                message="Input exceeds 50,000 characters and will be truncated.",
                suggestion="Use the first 50,000 characters or split into chunks.",
            ))
        mode = request.parameters.get("tokenizer_type", "whitespace")
        if mode not in ("whitespace", "regex", "bpe_demo", "wordpiece"):
            warnings.append(WarningEntry(
                code="UNKNOWN_TOKENIZER",
                message=f"Unknown tokenizer_type '{mode}'. Defaulting to 'whitespace'.",
                field="parameters.tokenizer_type",
            ))
        return warnings

    # ── preprocess ──────────────────────────────

    def preprocess(self, request: RunRequest) -> dict[str, Any]:
        text = (request.text or "")[:50_000]
        params = request.parameters
        return {
            "text": text,
            "params": params,
            "sentences": split_sentences(text),
        }

    # ── run ─────────────────────────────────────

    def run(self, preprocessed: dict[str, Any], request: RunRequest) -> TokenizationResult:
        text: str = preprocessed["text"]
        params: dict[str, Any] = preprocessed["params"]
        sentences: list[str] = preprocessed["sentences"]

        tokenizer_type: str = params.get("tokenizer_type", "whitespace")
        lowercase: bool = params.get("lowercase", True)
        remove_stopwords: bool = params.get("remove_stopwords", False)
        stemming: bool = params.get("stemming", False)
        lemmatization: bool = params.get("lemmatization", False)
        remove_punct: bool = params.get("remove_punctuation", False)

        raw_tokens: list[tuple[str, int, int]] = []
        subword_flags: list[bool] = []
        subword_ofs: list[str | None] = []
        merges: list[dict[str, Any]] = []

        if tokenizer_type == "whitespace":
            raw_tokens = whitespace_tokenize(text, params)
            subword_flags = [False] * len(raw_tokens)
            subword_ofs = [None] * len(raw_tokens)
        elif tokenizer_type == "regex":
            raw_tokens = regex_tokenize(text, params)
            subword_flags = [False] * len(raw_tokens)
            subword_ofs = [None] * len(raw_tokens)
        elif tokenizer_type == "bpe_demo":
            raw_tokens, merges = bpe_demo_tokenize(text, params)
            subword_flags = [False] * len(raw_tokens)
            subword_ofs = [None] * len(raw_tokens)
        elif tokenizer_type == "wordpiece":
            wp_tokens = wordpiece_demo_tokenize(text, params)
            for tok, start, end, is_sub in wp_tokens:
                raw_tokens.append((tok, start, end))
                subword_flags.append(is_sub)
                subword_ofs.append(None)  # could store parent word
        else:
            raw_tokens = whitespace_tokenize(text, params)
            subword_flags = [False] * len(raw_tokens)
            subword_ofs = [None] * len(raw_tokens)

        # Build sentence ID map
        sent_boundaries = []
        offset = 0
        for sent in sentences:
            sent_boundaries.append(offset)
            offset += len(sent) + 1

        def get_sentence_id(start: int) -> int:
            sid = 0
            for i, boundary in enumerate(sent_boundaries):
                if start >= boundary:
                    sid = i
                else:
                    break
            return sid

        # Apply normalization + filters
        tokens: list[Token] = []
        idx = 0
        for (tok_text, start, end), is_sub, sub_of in zip(raw_tokens, subword_flags, subword_ofs):
            if remove_punct and re.fullmatch(r'[^\w\s]+', tok_text):
                continue
            normalized = normalize_token(tok_text, lowercase, stemming, lemmatization)
            if remove_stopwords and normalized.lower() in DEFAULT_STOPWORDS:
                continue
            tokens.append(Token(
                index=idx,
                text=tok_text,
                normalized=normalized,
                start=start,
                end=end,
                sentence_id=get_sentence_id(start),
                is_subword=is_sub,
                subword_of=sub_of,
            ))
            idx += 1

        # Cleaned text: join normalized tokens
        cleaned = " ".join(t.normalized for t in tokens)
        vocab = sorted(set(t.normalized for t in tokens))
        freq = Counter(t.normalized for t in tokens)

        return TokenizationResult(
            tokens=tokens,
            cleaned_text=cleaned,
            vocabulary=vocab,
            frequency=dict(freq),
            subword_merges=merges,
            sentence_boundaries=sent_boundaries,
        )

    # ── trace ───────────────────────────────────

    def trace(
        self, preprocessed: dict[str, Any], result: TokenizationResult, request: RunRequest
    ) -> dict[str, Any]:
        if request.trace_level == TraceLevel.NONE:
            return {}

        base = {
            "token_count": len(result.tokens),
            "vocabulary_size": len(result.vocabulary),
            "sentence_count": len(result.sentence_boundaries),
            "cleaned_text": result.cleaned_text,
        }

        if request.trace_level == TraceLevel.SUMMARY:
            return base

        # FULL trace
        return {
            **base,
            "token_table": [
                {
                    "index": t.index,
                    "text": t.text,
                    "normalized": t.normalized,
                    "start": t.start,
                    "end": t.end,
                    "sentence_id": t.sentence_id,
                    "is_subword": t.is_subword,
                }
                for t in result.tokens
            ],
            "frequency_table": [
                {"term": k, "count": v}
                for k, v in sorted(result.frequency.items(), key=lambda x: -x[1])
            ],
            "subword_merges": result.subword_merges,
            "vocabulary": result.vocabulary,
        }

    # ── visualize ───────────────────────────────

    def visualize(
        self, trace: dict[str, Any], result: TokenizationResult, request: RunRequest
    ) -> list[VisualizationSpec]:
        specs: list[VisualizationSpec] = []

        # 1. Token boundary table (used by frontend highlighter)
        specs.append(VisualizationSpec(
            type="table",
            title="Token Boundary Map",
            data=[
                {"index": t.index, "text": t.text, "start": t.start, "end": t.end, "sentence_id": t.sentence_id}
                for t in result.tokens
            ],
        ))

        # 2. Frequency histogram
        top_freq = sorted(result.frequency.items(), key=lambda x: -x[1])[:30]
        specs.append(VisualizationSpec(
            type="bar",
            title="Top Token Frequencies",
            data=[{"term": k, "count": v} for k, v in top_freq],
            config={"x": "term", "y": "count", "color": "#6366f1"},
        ))

        # 3. BPE merge tree (only when tokenizer_type == bpe_demo)
        if result.subword_merges:
            specs.append(VisualizationSpec(
                type="tree",
                title="BPE Merge Steps",
                data=result.subword_merges,
            ))

        # 4. Before/after diff
        original_preview = (request.text or "")[:500]
        cleaned_preview = result.cleaned_text[:500]
        specs.append(VisualizationSpec(
            type="diff",
            title="Original vs. Cleaned Text",
            data={"original": original_preview, "cleaned": cleaned_preview},
        ))

        return specs

    # ── serialize ───────────────────────────────

    def serialize_result(self, result: TokenizationResult) -> dict[str, Any]:
        return {
            "token_count": len(result.tokens),
            "vocabulary_size": len(result.vocabulary),
            "cleaned_text": result.cleaned_text,
            "vocabulary": result.vocabulary[:200],      # cap for wire size
            "top_terms": [
                {"term": k, "count": v}
                for k, v in sorted(result.frequency.items(), key=lambda x: -x[1])[:20]
            ],
        }
