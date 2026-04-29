import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "classical-nlp-service"))

from shared_schemas import AlgorithmID, RunRequest, TraceLevel
from simulators.textrank import TextRankSimulator, power_iteration_pagerank


SIM = TextRankSimulator()


def test_keyword_mode_returns_ranked_words_and_convergence_log():
    response = SIM.execute(RunRequest(
        algorithm_id=AlgorithmID.TEXTRANK,
        text="Graphs rank words. Words connect to graphs. Ranking words helps search.",
        parameters={"mode": "keyword", "top_n": 3, "window_size": 2},
        trace_level=TraceLevel.FULL,
    ))
    assert response.result["mode"] == "keyword"
    assert len(response.result["ranked_output"]) == 3
    assert response.trace["convergence_log"]


def test_summary_mode_returns_summary_sentences():
    response = SIM.execute(RunRequest(
        algorithm_id=AlgorithmID.TEXTRANK,
        text="Cats sleep on mats. Cats chase toys. Space rockets launch from pads. Cats like warm mats.",
        parameters={"mode": "summary", "top_n": 2},
        trace_level=TraceLevel.FULL,
    ))
    assert response.result["mode"] == "summary"
    assert "summary" in response.result
    assert len(response.result["ranked_output"]) == 2


def test_pagerank_converges_before_max_iter_on_simple_graph():
    scores, log = power_iteration_pagerank(
        {"a": {"b": 1.0}, "b": {"a": 1.0}},
        ["a", "b"],
        damping=0.85,
        max_iter=20,
        tol=1e-6,
    )
    assert len(log) < 20
    assert round(scores["a"], 6) == round(scores["b"], 6)
