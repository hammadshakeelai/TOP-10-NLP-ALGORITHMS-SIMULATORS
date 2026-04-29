import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "classical-nlp-service"))

from shared_schemas import AlgorithmID, DocumentInput, RunRequest, TraceLevel
from simulators.naive_bayes import NaiveBayesSimulator


DOCS = [
    DocumentInput(id="p1", text="great movie loved acting", label="positive"),
    DocumentInput(id="p2", text="excellent story wonderful cast", label="positive"),
    DocumentInput(id="p3", text="happy joyful delightful film", label="positive"),
    DocumentInput(id="p4", text="amazing nice enjoyable scenes", label="positive"),
    DocumentInput(id="p5", text="good pleasant charming movie", label="positive"),
    DocumentInput(id="n1", text="bad movie hated acting", label="negative"),
    DocumentInput(id="n2", text="awful boring terrible cast", label="negative"),
    DocumentInput(id="n3", text="sad dull poor film", label="negative"),
    DocumentInput(id="n4", text="horrible nasty painful scenes", label="negative"),
    DocumentInput(id="n5", text="bad unpleasant weak movie", label="negative"),
]


def test_naive_bayes_predicts_and_exposes_probabilities():
    response = NaiveBayesSimulator().execute(RunRequest(
        algorithm_id=AlgorithmID.NAIVE_BAYES,
        text="great enjoyable movie",
        documents=DOCS,
        parameters={"smoothing_alpha": 1.0, "test_size": 0.4},
        trace_level=TraceLevel.FULL,
    ))
    assert response.result["predicted_class"] in {"positive", "negative"}
    assert set(response.result["predicted_probabilities"]) == {"positive", "negative"}
    assert response.trace["class_priors"]
    assert response.trace["top_features_per_class"]
    assert response.result["confusion_matrix"]


def test_naive_bayes_alpha_warning_is_nonfatal():
    response = NaiveBayesSimulator().execute(RunRequest(
        algorithm_id=AlgorithmID.NAIVE_BAYES,
        text="great movie",
        documents=DOCS,
        parameters={"smoothing_alpha": -1},
    ))
    assert response.status == "warning"
    assert any(w.code == "INVALID_ALPHA" for w in response.warnings)
