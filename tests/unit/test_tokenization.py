"""Unit tests for the Tokenization simulator — validates TK-001 through TK-004."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "classical-nlp-service"))

import pytest
from shared_schemas import AlgorithmID, RunRequest, SimulatorMode, TraceLevel
from simulators.tokenization import TokenizationSimulator

SIM = TokenizationSimulator()


def make_request(**kwargs) -> RunRequest:
    defaults = dict(
        algorithm_id=AlgorithmID.TOKENIZATION,
        text="The quick brown fox jumps over the lazy dog.",
        mode=SimulatorMode.LEARNING,
        trace_level=TraceLevel.FULL,
        parameters={},
    )
    defaults.update(kwargs)
    return RunRequest(**defaults)


# ── TK-001: character offsets ────────────────────────────────────────────────

def test_whitespace_offsets():
    text = "Hello world foo"
    req = make_request(text=text, parameters={"tokenizer_type": "whitespace"})
    response = SIM.execute(req)
    tokens = response.trace["token_table"]
    for tok in tokens:
        assert text[tok["start"]: tok["end"]] == tok["text"], (
            f"Offset mismatch: expected '{text[tok['start']:tok['end']]}', got '{tok['text']}'"
        )


def test_regex_offsets():
    text = "NLP is fun! (Really.)"
    req = make_request(text=text, parameters={"tokenizer_type": "regex", "regex_pattern": r"\b\w+\b"})
    response = SIM.execute(req)
    tokens = response.trace["token_table"]
    for tok in tokens:
        assert text[tok["start"]: tok["end"]].lower() == tok["normalized"], (
            f"Token '{tok['normalized']}' start/end mismatch"
        )


# ── TK-002: tokenizer modes ──────────────────────────────────────────────────

@pytest.mark.parametrize("mode", ["whitespace", "regex", "bpe_demo", "wordpiece"])
def test_tokenizer_modes(mode):
    req = make_request(parameters={"tokenizer_type": mode})
    response = SIM.execute(req)
    assert response.status in ("success", "warning")
    assert response.result["token_count"] >= 0


def test_bpe_merges_in_trace():
    req = make_request(
        text="low lower lowest lower",
        parameters={"tokenizer_type": "bpe_demo", "bpe_num_merges": 5},
    )
    response = SIM.execute(req)
    assert "subword_merges" in response.trace
    merges = response.trace["subword_merges"]
    assert isinstance(merges, list)


# ── TK-003: vocabulary size changes ─────────────────────────────────────────

def test_stopword_removal_reduces_vocab():
    text = "The quick brown fox is the laziest animal"
    req_no_stop = make_request(text=text, parameters={"tokenizer_type": "whitespace", "remove_stopwords": False})
    req_stop    = make_request(text=text, parameters={"tokenizer_type": "whitespace", "remove_stopwords": True})
    resp_no = SIM.execute(req_no_stop)
    resp_sw = SIM.execute(req_stop)
    assert resp_sw.result["vocabulary_size"] < resp_no.result["vocabulary_size"]


def test_stemming_reduces_vocab():
    text = "running runs runner fastest fast fastening"
    req_no = make_request(text=text, parameters={"tokenizer_type": "whitespace", "stemming": False})
    req_st = make_request(text=text, parameters={"tokenizer_type": "whitespace", "stemming": True})
    resp_no = SIM.execute(req_no)
    resp_st = SIM.execute(req_st)
    assert resp_st.result["vocabulary_size"] <= resp_no.result["vocabulary_size"]


# ── TK-004: alignment ────────────────────────────────────────────────────────

def test_token_boundary_visualization_present():
    req = make_request()
    response = SIM.execute(req)
    viz_types = [v.type for v in response.visualization_specs]
    assert "table" in viz_types, "Token boundary table must be in visualization_specs"


# ── edge cases ───────────────────────────────────────────────────────────────

def test_empty_text_returns_zero_tokens():
    req = make_request(text="   ")
    response = SIM.execute(req)
    assert response.result["token_count"] == 0


def test_emoji_handling():
    req = make_request(text="Hello 🌍 world 🚀 NLP")
    response = SIM.execute(req)
    assert response.status in ("success", "warning")


def test_long_text_truncated_gracefully():
    long_text = "word " * 20_000
    req = make_request(text=long_text)
    response = SIM.execute(req)
    assert len(response.warnings) > 0  # should warn about truncation
    assert response.result["token_count"] > 0


def test_trace_level_none_returns_empty():
    req = make_request(trace_level=TraceLevel.NONE)
    response = SIM.execute(req)
    assert response.trace == {}
