"""
Generate static mock data for the frontend's offline/demo mode.

Runs the real simulator registries in-process (no server needed) and snapshots:
  - GET /algorithms/            → src/mocks/catalog.json
  - GET /algorithms/{id}/demo   → src/mocks/demos/{id}.json
  - POST /runs/ (demo input)    → src/mocks/runs/{id}.json

Usage:
    python apps/web-ui/scripts/generate-mocks.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "packages"))

OUT_DIR = ROOT / "apps" / "web-ui" / "src" / "mocks"

SERVICES = ["classical-nlp-service", "transformer-service"]


def purge_service_modules() -> None:
    for name in list(sys.modules):
        if name == "registry" or name == "simulators" or name.startswith("simulators."):
            del sys.modules[name]


def load_registry(service_name: str):
    service_dir = ROOT / "services" / service_name
    registry_path = service_dir / "registry.py"
    module_name = f"{service_name.replace('-', '_')}_registry"
    purge_service_modules()
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


def to_jsonable(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump(mode="json", exclude_none=True)
    if hasattr(obj, "dict"):
        return json.loads(obj.json(exclude_none=True))
    return obj


def main() -> int:
    from shared_schemas import RunRequest

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "demos").mkdir(exist_ok=True)
    (OUT_DIR / "runs").mkdir(exist_ok=True)

    all_entries = []
    failures = []

    for service in SERVICES:
        registry = load_registry(service)
        entries = [to_jsonable(e) for e in registry.get_catalog()]
        all_entries.extend(entries)

        for entry in entries:
            alg_id = entry["id"]
            try:
                sim = registry.get_simulator(alg_id)
                demo = to_jsonable(sim.get_demo_metadata())

                demo_input = demo.get("demo_input") or {}
                request = RunRequest(
                    algorithm_id=alg_id,
                    mode="learning",
                    trace_level="full",
                    parameters=demo.get("auto_parameters") or {},
                    **({"text": demo_input["text"]} if demo_input.get("text") else {}),
                    **(
                        {"documents": demo_input["documents"]}
                        if demo_input.get("documents")
                        else {}
                    ),
                )
                run = to_jsonable(sim.execute(request))

                (OUT_DIR / "demos" / f"{alg_id}.json").write_text(
                    json.dumps(demo, indent=2, ensure_ascii=False), encoding="utf-8"
                )
                (OUT_DIR / "runs" / f"{alg_id}.json").write_text(
                    json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8"
                )
                print(f"  ok  {alg_id}")
            except Exception as exc:  # noqa: BLE001 — snapshotting must be tolerant
                failures.append((alg_id, repr(exc)))
                print(f"SKIP  {alg_id}: {exc!r}")

    (OUT_DIR / "catalog.json").write_text(
        json.dumps(all_entries, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"\ncatalog: {len(all_entries)} entries -> {OUT_DIR / 'catalog.json'}")
    if failures:
        print(f"{len(failures)} algorithm(s) skipped:")
        for alg_id, err in failures:
            print(f"  - {alg_id}: {err}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
