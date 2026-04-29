import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "classical-nlp-service"))

from shared_schemas import AlgorithmID, DocumentInput, RunRequest, TraceLevel
from simulators.naive_bayes import NaiveBayesSimulator
from simulators.rake import RAKESimulator
from simulators.svm import SVMSimulator
from simulators.textrank import TextRankSimulator
from simulators.tfidf import TFIDFSimulator
from simulators.tokenization import TokenizationSimulator
from tests.unit.test_naive_bayes import DOCS


def test_tokenization_golden_output():
    response = TokenizationSimulator().execute(RunRequest(
        algorithm_id=AlgorithmID.TOKENIZATION,
        text="Hello NLP!",
        parameters={"tokenizer_type": "regex", "regex_pattern": r"\b\w+\b"},
        trace_level=TraceLevel.FULL,
    ))
    assert [t["normalized"] for t in response.trace["token_table"]] == ["hello", "nlp"]
    assert response.result["input_fingerprint" if False else "token_count"] == 2


def test_tfidf_golden_top_term():
    response = TFIDFSimulator().execute(RunRequest(
        algorithm_id=AlgorithmID.TFIDF,
        documents=[
            DocumentInput(id="d1", text="cat cat sat"),
            DocumentInput(id="d2", text="dog sat"),
        ],
        parameters={"normalize": False, "remove_stopwords": False, "top_n": 1},
        trace_level=TraceLevel.FULL,
    ))
    assert response.result["top_terms_per_doc"][0]["terms"] == [{"term": "cat", "score": 2.81093}]


def test_rake_golden_keyword():
    response = RAKESimulator().execute(RunRequest(
        algorithm_id=AlgorithmID.RAKE,
        text="machine learning improves search and machine learning ranks documents",
        parameters={"top_n": 1, "max_phrase_words": 5},
        trace_level=TraceLevel.FULL,
    ))
    assert response.result["ranked_keywords"][0]["phrase"] == "machine learning improves search"


def test_textrank_golden_schema_and_keyword():
    response = TextRankSimulator().execute(RunRequest(
        algorithm_id=AlgorithmID.TEXTRANK,
        text="Graphs rank words. Words connect graphs. Graphs help search.",
        parameters={"mode": "keyword", "top_n": 2},
        trace_level=TraceLevel.FULL,
    ))
    assert response.result["mode"] == "keyword"
    assert response.result["ranked_output"][0]["word"] in {"graphs", "words"}


def test_naive_bayes_golden_schema():
    response = NaiveBayesSimulator().execute(RunRequest(
        algorithm_id=AlgorithmID.NAIVE_BAYES,
        text="great wonderful movie",
        documents=DOCS,
        parameters={"random_state": 7, "test_size": 0.4},
    ))
    assert response.result["predicted_class"] == "positive"


def test_svm_golden_schema():
    response = SVMSimulator().execute(RunRequest(
        algorithm_id=AlgorithmID.SVM,
        text="awful terrible movie",
        documents=DOCS,
        parameters={"test_size": 0.4},
    ))
    assert response.result["predicted_class"] in {"positive", "negative"}
    assert set(response.result["decision_scores"]) == {"positive", "negative"}
