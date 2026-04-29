import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "classical-nlp-service"))

from shared_schemas import AlgorithmID, RunRequest, TraceLevel
from simulators.rake import RAKESimulator


SIM = RAKESimulator()


def run_rake(text: str, parameters=None):
    return SIM.execute(RunRequest(
        algorithm_id=AlgorithmID.RAKE,
        text=text,
        parameters=parameters or {},
        trace_level=TraceLevel.FULL,
    ))


def test_candidate_phrases_split_on_stopwords():
    response = run_rake("Natural language processing improves search and ranking.")
    phrases = {item["phrase"] for item in response.trace["candidate_phrases"]}
    assert "natural language processing improves search" in phrases
    assert "ranking" in phrases


def test_custom_stopword_changes_candidates():
    text = "graph ranking improves graph search"
    baseline = run_rake(text, {"stopwords": [], "max_phrase_words": 5})
    custom = run_rake(text, {"stopwords": ["improves"], "max_phrase_words": 5})

    baseline_phrases = {item["phrase"] for item in baseline.trace["candidate_phrases"]}
    custom_phrases = {item["phrase"] for item in custom.trace["candidate_phrases"]}
    assert "graph ranking improves graph search" in baseline_phrases
    assert {"graph ranking", "graph search"}.issubset(custom_phrases)


def test_score_formula_degree_over_frequency():
    response = run_rake("red apple red banana", {"stopwords": [], "max_phrase_words": 5})
    scores = response.trace["word_scores"]
    assert scores["red"]["frequency"] == 2
    assert scores["red"]["degree"] == 8
    assert scores["red"]["score"] == 4.0
    assert response.trace["ranked_keywords"][0]["score"] == 16.0
