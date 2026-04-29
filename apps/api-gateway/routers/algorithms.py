"""
GET /algorithms             — full catalog
GET /algorithms/{id}        — single algorithm entry
GET /algorithms/{id}/demo   — demo initialization metadata
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT / "packages"))

from fastapi import APIRouter, HTTPException

from shared_schemas import AlgorithmEntry, AlgorithmID, DemoMetadata

router = APIRouter()

CLASSICAL_IDS = {
    AlgorithmID.TOKENIZATION, AlgorithmID.TFIDF, AlgorithmID.NAIVE_BAYES,
    AlgorithmID.SVM, AlgorithmID.RAKE, AlgorithmID.TEXTRANK,
}
TRANSFORMER_IDS = {
    AlgorithmID.WORD_EMBEDDINGS, AlgorithmID.LSTM, AlgorithmID.TRANSFORMER_ATTN,
    AlgorithmID.BERT, AlgorithmID.GPT, AlgorithmID.T5, AlgorithmID.FASTTEXT,
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


def get_catalog() -> list[AlgorithmEntry]:
    classical = _load_registry("classical-nlp-service").get_catalog()
    transformer = _load_registry("transformer-service").get_catalog()
    return classical + transformer


def _get_demo(algorithm_id: str) -> DemoMetadata | None:
    if algorithm_id in CLASSICAL_IDS:
        registry = _load_registry("classical-nlp-service")
    elif algorithm_id in TRANSFORMER_IDS:
        registry = _load_registry("transformer-service")
    else:
        return None
    sim = registry.get_simulator(algorithm_id)
    return sim.get_demo_metadata()


@router.get("/", response_model=list[AlgorithmEntry])
async def list_algorithms():
    """Return the full algorithm catalog."""
    return get_catalog()


@router.get("/{algorithm_id}/demo", response_model=DemoMetadata)
async def get_algorithm_demo(algorithm_id: str):
    """Return demo initialization metadata for an algorithm (inputs, parameters, explanations)."""
    demo = _get_demo(algorithm_id)
    if demo is None:
        raise HTTPException(status_code=404, detail=f"No demo metadata found for '{algorithm_id}'.")
    return demo


@router.get("/{algorithm_id}", response_model=AlgorithmEntry)
async def get_algorithm(algorithm_id: str):
    """Return metadata for a single algorithm."""
    catalog = get_catalog()
    for entry in catalog:
        if entry.id == algorithm_id:
            return entry
    raise HTTPException(status_code=404, detail=f"Algorithm '{algorithm_id}' not found.")
