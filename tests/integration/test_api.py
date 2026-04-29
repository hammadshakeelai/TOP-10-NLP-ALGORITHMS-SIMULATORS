import sys
import asyncio
from pathlib import Path

import httpx

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "apps" / "api-gateway"))
sys.path.insert(0, str(ROOT / "packages"))

from main import app


CLASSIFIER_DOCS = [
    {"id": "p1", "text": "great movie loved acting", "label": "positive"},
    {"id": "p2", "text": "excellent story wonderful cast", "label": "positive"},
    {"id": "p3", "text": "happy joyful delightful film", "label": "positive"},
    {"id": "p4", "text": "amazing nice enjoyable scenes", "label": "positive"},
    {"id": "p5", "text": "good pleasant charming movie", "label": "positive"},
    {"id": "n1", "text": "bad movie hated acting", "label": "negative"},
    {"id": "n2", "text": "awful boring terrible cast", "label": "negative"},
    {"id": "n3", "text": "sad dull poor film", "label": "negative"},
    {"id": "n4", "text": "horrible nasty painful scenes", "label": "negative"},
    {"id": "n5", "text": "bad unpleasant weak movie", "label": "negative"},
]


def payload_for(algorithm_id: str):
    if algorithm_id == "tokenization":
        return {"algorithm_id": algorithm_id, "text": "Hello NLP world.", "parameters": {"tokenizer_type": "regex"}}
    if algorithm_id == "tfidf":
        return {"algorithm_id": algorithm_id, "documents": [{"id": "d1", "text": "cat cat sat"}, {"id": "d2", "text": "dog sat"}]}
    if algorithm_id == "rake":
        return {"algorithm_id": algorithm_id, "text": "machine learning improves search and ranks documents"}
    if algorithm_id == "textrank":
        return {"algorithm_id": algorithm_id, "text": "Graphs rank words. Words connect graphs. Graphs help search."}
    if algorithm_id == "naive_bayes":
        return {"algorithm_id": algorithm_id, "text": "great movie", "documents": CLASSIFIER_DOCS, "parameters": {"test_size": 0.4}}
    if algorithm_id == "svm":
        return {"algorithm_id": algorithm_id, "text": "awful movie", "documents": CLASSIFIER_DOCS, "parameters": {"test_size": 0.4}}
    raise AssertionError(algorithm_id)


async def post_run(algorithm_id: str):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.post("/runs/", json=payload_for(algorithm_id))


def test_post_runs_for_each_classical_algorithm():
    for algorithm_id in ["tokenization", "tfidf", "naive_bayes", "svm", "rake", "textrank"]:
        response = asyncio.run(post_run(algorithm_id))
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["algorithm_id"] == algorithm_id
        assert body["status"] in {"success", "warning"}
        assert body["algorithm_version"].startswith(f"{algorithm_id}-v")
        assert body["input_fingerprint"].startswith("sha256:")
        assert "runtime_ms" in body["metrics"]
        assert isinstance(body["visualization_specs"], list)


async def get_demo(algorithm_id: str):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get(f"/algorithms/{algorithm_id}/demo")


def test_demo_endpoint_returns_metadata_for_all_classical():
    for algorithm_id in ["tokenization", "tfidf", "naive_bayes", "svm", "rake", "textrank"]:
        response = asyncio.run(get_demo(algorithm_id))
        assert response.status_code == 200, f"{algorithm_id}: {response.text}"
        body = response.json()
        assert "demo_input" in body, f"{algorithm_id}: missing demo_input"
        assert "auto_parameters" in body, f"{algorithm_id}: missing auto_parameters"
        assert "step_explanations" in body, f"{algorithm_id}: missing step_explanations"
        assert "formula_cards" in body, f"{algorithm_id}: missing formula_cards"
        assert "references" in body, f"{algorithm_id}: missing references"
        assert "receiver_mode_explanations" in body, f"{algorithm_id}: missing receiver_mode_explanations"
        assert len(body["step_explanations"]) > 0, f"{algorithm_id}: empty step_explanations"
        assert len(body["formula_cards"]) > 0, f"{algorithm_id}: empty formula_cards"
        assert len(body["receiver_mode_explanations"]) == 5, f"{algorithm_id}: expected 5 receiver modes"


def test_demo_endpoint_returns_404_for_unknown():
    transport = httpx.ASGITransport(app=app)
    async def _get():
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get("/algorithms/unknown_xyz/demo")
    response = asyncio.run(_get())
    assert response.status_code == 404


def test_run_response_includes_demo_fields():
    response = asyncio.run(post_run("tokenization"))
    assert response.status_code == 201, response.text
    body = response.json()
    assert isinstance(body["step_explanations"], list)
    assert isinstance(body["formula_cards"], list)
    assert isinstance(body["references"], list)
    assert isinstance(body["receiver_mode_explanations"], list)
    assert len(body["step_explanations"]) > 0, "tokenization run should include step_explanations"
    assert len(body["formula_cards"]) > 0, "tokenization run should include formula_cards"
