"""Re-export the classical BaseSimulator without using the ambiguous simulators package name."""
from __future__ import annotations

import importlib.util
from pathlib import Path

_BASE_PATH = Path(__file__).resolve().parents[2] / "classical-nlp-service" / "simulators" / "base.py"
_SPEC = importlib.util.spec_from_file_location("_classical_base_simulator", _BASE_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Unable to load BaseSimulator from {_BASE_PATH}")

_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)
BaseSimulator = _MODULE.BaseSimulator

__all__ = ["BaseSimulator"]
