# AGENTS.md

Guidance for Codex and other coding agents working in this repository.

## Project Overview

This repository implements an NLP Algorithm Simulator Platform. It provides interactive simulators for preprocessing, vectorization, classification, keyword extraction, sequence models, and transformer-style NLP workflows.

The product goal is educational and experimental: users paste text or provide small datasets, choose an algorithm, tune parameters, run the simulator, inspect trace artifacts, view visualizations, and export reproducible results.

The SRS is stored at:

- `NLP_Algorithm_Simulators_SRS.docx`

If detailed requirements are needed, extract the DOCX with Python `zipfile` and read `word/document.xml`.

## Current Stack

Backend:

- Python 3.11
- FastAPI
- Pydantic v2
- NumPy
- scikit-learn
- NetworkX
- Optional transformer stack: torch, transformers, gensim, fastText, sentencepiece

Frontend:

- React 18
- TypeScript
- Vite
- Redux Toolkit
- Recharts
- Tailwind CSS
- @xyflow/react

Infrastructure:

- Docker Compose
- PostgreSQL
- Redis

## Repository Structure

- `apps/api-gateway` - FastAPI gateway for catalog, runs, exports, and health.
- `apps/web-ui` - React/Vite simulator UI.
- `packages/shared-schemas` - original shared Pydantic contract source.
- `packages/shared_schemas` - importable Python compatibility package.
- `services/classical-nlp-service` - classical NLP simulators and registry.
- `services/transformer-service` - transformer and neural simulators and registry.
- `services/export-service` - JSON/CSV export helpers.
- `datasets/examples` - sample CSV and text datasets.
- `infra` - Docker Compose and Dockerfiles.
- `tests` - unit, golden, and integration tests.
- `docs/IMPLEMENTATION_STATUS.md` - detailed implementation record and remaining work.

## Implemented Simulators

Classical:

- Tokenization
- TF-IDF
- Naive Bayes
- SVM
- RAKE
- TextRank

Transformer/neural:

- Word embeddings
- LSTM
- Transformer attention
- BERT
- GPT-style generation
- T5/sequence-to-sequence
- FastText

## Shared Simulator Contract

Every simulator must extend `BaseSimulator` and implement:

- `validate`
- `preprocess`
- `run`
- `trace`
- `visualize`
- `serialize_result`

Every run should return a `RunResponse` with:

- `algorithm_version`
- `input_fingerprint`
- `metrics.runtime_ms`
- `warnings`
- `trace`
- `visualization_specs`
- `result`

Respect `trace_level`:

- `none` returns `trace = {}`
- `summary` returns key metrics and concise output
- `full` returns intermediate tables, matrices, scores, and formulas where available

Warnings are non-fatal. Raise `ValueError` only for hard errors that should become HTTP 422 responses.

## Local Setup

Full Windows run instructions are in `docs/RUNBOOK.md`.

Backend:

```powershell
cd C:\Users\HP\Documents\GitHub\ai-ml\TOP-10-NLP-ALGORITHMS-SIMULATORS
pip install -r services/classical-nlp-service/requirements.txt
uvicorn main:app --app-dir apps/api-gateway --reload --port 8000
```

Frontend:

```powershell
cd apps/web-ui
npm install
npm run dev
```

Tests:

```powershell
python -m pytest tests -q
```

Frontend build:

```powershell
cd apps/web-ui
npm run build
```

Docker:

```powershell
docker compose -f infra/docker-compose.yml up --build
```

Known local URLs:

- API health: `http://127.0.0.1:8000/health`
- API catalog: `http://127.0.0.1:8000/algorithms/`
- Swagger docs: `http://127.0.0.1:8000/docs`
- Frontend: `http://localhost:5173`

`GET /` on the API returns 404 by design.

## API Routes

- `GET /health`
- `GET /algorithms/`
- `GET /algorithms/{algorithm_id}`
- `POST /runs/`
- `GET /runs/{run_id}`
- `POST /exports/{run_id}`

## Agent Notes

- Keep edits scoped. This repo has many generated or in-progress files that may be untracked.
- Prefer existing simulator patterns over new abstractions.
- Use `packages/shared_schemas` for Python imports.
- The transformer service base class must be loaded without importing the ambiguous top-level `simulators.base`; otherwise the API catalog can hit a circular import.
- Do not add heavyweight model downloads to default tests.
- When adding a simulator, add it to the relevant service registry and frontend catalog will discover it through `/algorithms/`.
- Update `docs/IMPLEMENTATION_STATUS.md`, `README.md`, and this file when major architecture or startup commands change.
