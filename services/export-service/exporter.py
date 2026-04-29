from __future__ import annotations

import csv
import hashlib
import io
import json
from typing import Any

from shared_schemas import RunResponse


def export_json(run: RunResponse) -> dict[str, Any]:
    payload = run.model_dump(mode="json")
    raw = json.dumps(payload, sort_keys=True).encode("utf-8")
    return {
        "format": "json",
        "filename": f"{run.run_id}.json",
        "content_type": "application/json",
        "checksum": hashlib.sha256(raw).hexdigest(),
        "content": payload,
    }


def export_csv(run: RunResponse) -> dict[str, Any]:
    rows = _flatten_rows(run)
    buffer = io.StringIO()
    fieldnames = sorted({key for row in rows for key in row.keys()}) if rows else ["run_id", "algorithm_id", "status"]
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows or [{
        "run_id": run.run_id,
        "algorithm_id": run.algorithm_id,
        "status": run.status,
    }])
    content = buffer.getvalue()
    return {
        "format": "csv",
        "filename": f"{run.run_id}.csv",
        "content_type": "text/csv",
        "checksum": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "content": content,
    }


def export_run(run: RunResponse) -> dict[str, Any]:
    return {
        "run_id": run.run_id,
        "algorithm_id": run.algorithm_id,
        "exports": [export_json(run), export_csv(run)],
    }


def _flatten_rows(run: RunResponse) -> list[dict[str, Any]]:
    base = {
        "run_id": run.run_id,
        "algorithm_id": str(run.algorithm_id),
        "algorithm_version": run.algorithm_version,
        "input_fingerprint": run.input_fingerprint,
        "status": str(run.status),
        "runtime_ms": run.metrics.runtime_ms,
    }
    result = run.result
    candidate_lists = [
        result.get("ranked_keywords"),
        result.get("ranked_output"),
        result.get("top_terms"),
        result.get("query_results"),
    ]
    for candidate in candidate_lists:
        if isinstance(candidate, list) and candidate:
            return [{**base, **_scalarize(row)} for row in candidate if isinstance(row, dict)]
    return [{**base, **_scalarize(result)}]


def _scalarize(row: dict[str, Any]) -> dict[str, Any]:
    scalar: dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, (str, int, float, bool)) or value is None:
            scalar[key] = value
        else:
            scalar[key] = json.dumps(value, sort_keys=True)
    return scalar
