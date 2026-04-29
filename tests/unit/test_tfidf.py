import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "classical-nlp-service"))

from shared_schemas import AlgorithmID, DocumentInput, RunRequest, TraceLevel
from simulators.tfidf import TFIDFSimulator, compute_idf, compute_tf


SIM = TFIDFSimulator()


def test_tf_schemes_are_computed_separately():
    tokens = ["apple", "apple", "banana"]
    assert compute_tf(tokens, "raw") == {"apple": 2.0, "banana": 1.0}
    assert compute_tf(tokens, "bool") == {"apple": 1.0, "banana": 1.0}
    assert compute_tf(tokens, "freq")["apple"] == 2 / 3
    assert compute_tf(tokens, "log")["apple"] == 1 + math.log(2)


def test_idf_smoothing_matches_formula():
    token_sets = [{"apple", "banana"}, {"banana"}]
    idf = compute_idf(token_sets, ["apple", "banana"], smooth=True)
    assert idf["banana"] == 1.0
    assert round(idf["apple"], 6) == round(math.log(3 / 2) + 1, 6)


def test_execute_returns_full_tables_and_top_terms():
    req = RunRequest(
        algorithm_id=AlgorithmID.TFIDF,
        documents=[
            DocumentInput(id="d1", text="cat cat sat"),
            DocumentInput(id="d2", text="dog sat"),
        ],
        parameters={"top_n": 2, "normalize": False, "remove_stopwords": False},
        trace_level=TraceLevel.FULL,
    )
    response = SIM.execute(req)

    assert response.result["document_count"] == 2
    assert response.trace["tf_table"]
    assert response.trace["idf_table"]
    assert response.trace["tfidf_matrix"]
    assert response.trace["top_terms_per_doc"][0]["terms"][0]["term"] == "cat"


def test_query_ranking_prefers_matching_document():
    req = RunRequest(
        algorithm_id=AlgorithmID.TFIDF,
        documents=[
            DocumentInput(id="d1", text="cats purr softly"),
            DocumentInput(id="d2", text="rockets launch quickly"),
        ],
        parameters={"query": "rocket launch", "top_n": 3},
        trace_level=TraceLevel.FULL,
    )
    response = SIM.execute(req)

    assert response.result["query_results"][0]["doc_id"] == "d2"
    assert response.result["query_results"][0]["score"] > response.result["query_results"][1]["score"]


def test_trace_level_none_returns_empty_trace():
    req = RunRequest(
        algorithm_id=AlgorithmID.TFIDF,
        documents=[DocumentInput(id="d1", text="one document")],
        trace_level=TraceLevel.NONE,
    )
    assert SIM.execute(req).trace == {}
