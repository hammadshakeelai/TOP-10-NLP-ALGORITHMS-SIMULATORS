from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

from routers.runs import _run_store

ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(ROOT / "packages"))

router = APIRouter()


def _load_exporter():
    exporter_path = ROOT / "services" / "export-service" / "exporter.py"
    spec = importlib.util.spec_from_file_location("export_service_exporter", exporter_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load exporter from {exporter_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@router.post("/{run_id}")
async def create_export(run_id: str):
    run = _run_store.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return _load_exporter().export_run(run)
