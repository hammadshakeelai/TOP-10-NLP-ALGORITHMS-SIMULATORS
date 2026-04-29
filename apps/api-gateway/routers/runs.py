"""
POST /runs          — execute a simulator, return RunResponse
GET  /runs/{run_id} — retrieve a stored run (in-memory stub; swap for DB)

Routing logic:
  classical algorithms (tokenization, tfidf, naive_bayes, svm, rake, textrank)
    → classical-nlp-service registry
  transformer algorithms (word_embeddings, lstm, transformer_attention, bert, gpt, t5, fasttext)
    → transformer-service registry (dynamically imported)
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT / "packages"))

from fastapi import APIRouter, HTTPException

from shared_schemas import AlgorithmID, RunRequest, RunResponse

router = APIRouter()

# In-memory run store (replace with PostgreSQL + S3 in production)
_run_store: dict[str, RunResponse] = {}

CLASSICAL_IDS = {
    AlgorithmID.TOKENIZATION,
    AlgorithmID.TFIDF,
    AlgorithmID.NAIVE_BAYES,
    AlgorithmID.SVM,
    AlgorithmID.RAKE,
    AlgorithmID.TEXTRANK,
}

TRANSFORMER_IDS = {
    AlgorithmID.WORD_EMBEDDINGS,
    AlgorithmID.LSTM,
    AlgorithmID.TRANSFORMER_ATTN,
    AlgorithmID.BERT,
    AlgorithmID.GPT,
    AlgorithmID.T5,
    AlgorithmID.FASTTEXT,
}


def _purge_service_modules() -> None:
    for name in list(sys.modules):
        if name == "registry" or name == "simulators" or name.startswith("simulators."):
            del sys.modules[name]


def _load_registry(service_name: str):
    service_dir = ROOT / "services" / service_name
    registry_path = service_dir / "registry.py"
    module_name = f"{service_name.replace('-', '_')}_registry"
    _purge_service_modules()
    sys.path.insert(0, str(service_dir))
    try:
        spec = importlib.util.spec_from_file_location(module_name, registry_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Unable to load registry from {registry_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        try:
            sys.path.remove(str(service_dir))
        except ValueError:
            pass


def _route_simulator(algorithm_id: str):
    if algorithm_id in CLASSICAL_IDS:
        return _load_registry("classical-nlp-service").get_simulator(algorithm_id)
    if algorithm_id in TRANSFORMER_IDS:
        return _load_registry("transformer-service").get_simulator(algorithm_id)
    raise ValueError(f"No simulator registered for algorithm_id='{algorithm_id}'.")


@router.post("/", response_model=RunResponse, status_code=201)
async def create_run(request: RunRequest) -> RunResponse:
    """Execute a simulator and return the full run response."""
    simulator = _route_simulator(request.algorithm_id)
    response = simulator.execute(request)
    _run_store[response.run_id] = response
    return response


@router.get("/{run_id}", response_model=RunResponse)
async def get_run(run_id: str) -> RunResponse:
    """Retrieve a previously executed run by ID."""
    run = _run_store.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return run
