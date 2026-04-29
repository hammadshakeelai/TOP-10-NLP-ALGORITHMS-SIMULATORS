import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services" / "classical-nlp-service"))

from shared_schemas import AlgorithmID, RunRequest, TraceLevel
from simulators.svm import SVMSimulator
from tests.unit.test_naive_bayes import DOCS


def test_svm_predicts_margins_and_features():
    response = SVMSimulator().execute(RunRequest(
        algorithm_id=AlgorithmID.SVM,
        text="awful boring movie",
        documents=DOCS,
        parameters={"C": 1.0, "test_size": 0.4},
        trace_level=TraceLevel.FULL,
    ))
    assert response.result["predicted_class"] in {"positive", "negative"}
    assert set(response.result["decision_scores"]) == {"positive", "negative"}
    assert response.trace["top_positive_features"]
    assert response.trace["top_negative_features"]
    assert response.result["confusion_matrix"]


def test_svm_invalid_c_warning_is_nonfatal():
    response = SVMSimulator().execute(RunRequest(
        algorithm_id=AlgorithmID.SVM,
        text="great movie",
        documents=DOCS,
        parameters={"C": 0},
    ))
    assert response.status == "warning"
    assert any(w.code == "INVALID_C" for w in response.warnings)
