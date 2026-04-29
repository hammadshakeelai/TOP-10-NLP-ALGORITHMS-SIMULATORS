# NLP Algorithm Simulator Platform - Implementation Status

Last updated: April 29, 2026

## Summary

This repository has been expanded from a placeholder into a working full-stack NLP Algorithm Simulator Platform skeleton with implemented simulator modules, shared API contracts, a FastAPI gateway, a React/Vite frontend, test coverage scaffolding, sample datasets, Docker infrastructure, and export stubs.

The platform follows the SRS in `NLP_Algorithm_Simulators_SRS.docx`: every simulator implements a common pipeline of `validate`, `preprocess`, `run`, `trace`, `visualize`, and `serialize_result`, returning a shared `RunResponse` with `algorithm_version`, `input_fingerprint`, `runtime_ms`, warnings, trace data, and visualization specs.

## New in Sprint 3

- **GET /algorithms/{id}/demo endpoint** - Returns demo metadata for each algorithm including example input, parameters, formulas, references, and step-by-step explanations
- **13 demo metadata files** - Added example demos for all algorithms in `apps/web-ui/src/data/demos/`
- **5 new frontend components**:
  - `ReceiverModeSwitcher.tsx` - Toggle between text input and file upload modes
  - `StepTimeline.tsx` - Expandable timeline showing algorithm execution steps
  - `FormulaPanel.tsx` - Displays mathematical formulas used by algorithms
  - `ReferencesPanel.tsx` - Shows academic references and links
  - `ExplanationPanel.tsx` - Detailed step-by-step algorithm explanations

## Backend Implemented

Shared contracts:

- `packages/shared-schemas/models.py` contains the Pydantic contracts.
- `packages/shared_schemas/` was added as a Python-importable compatibility package because Python cannot import a hyphenated package name directly.

Classical service:

- `services/classical-nlp-service/simulators/tokenization.py`
- `services/classical-nlp-service/simulators/tfidf.py`
- `services/classical-nlp-service/simulators/naive_bayes.py`
- `services/classical-nlp-service/simulators/svm.py`
- `services/classical-nlp-service/simulators/rake.py`
- `services/classical-nlp-service/simulators/textrank.py`
- `services/classical-nlp-service/registry.py`
- `services/classical-nlp-service/__init__.py`

Transformer service:

- `services/transformer-service/simulators/word_embeddings.py`
- `services/transformer-service/simulators/lstm_sim.py`
- `services/transformer-service/simulators/transformer_attention.py`
- `services/transformer-service/simulators/bert_sim.py`
- `services/transformer-service/simulators/gpt_sim.py`
- `services/transformer-service/simulators/t5_sim.py`
- `services/transformer-service/simulators/fasttext_sim.py`
- `services/transformer-service/simulators/__init__.py`
- `services/transformer-service/registry.py`
- `services/transformer-service/__init__.py`

API gateway:

- `apps/api-gateway/main.py`
- `apps/api-gateway/routers/algorithms.py`
- `apps/api-gateway/routers/runs.py`
- `apps/api-gateway/routers/health.py`
- `apps/api-gateway/routers/exports.py`

Export service:

- `services/export-service/exporter.py` generates JSON and CSV export payloads from a `RunResponse`.

## Frontend Implemented

React/Vite UI:

- `apps/web-ui/src/App.tsx`
- `apps/web-ui/src/main.tsx`
- `apps/web-ui/src/index.css`
- `apps/web-ui/index.html`
- `apps/web-ui/vite.config.ts`
- `apps/web-ui/tsconfig.json`
- `apps/web-ui/tailwind.config.js`
- `apps/web-ui/postcss.config.js`

State/API/types:

- `apps/web-ui/src/types/api.ts`
- `apps/web-ui/src/api/client.ts`
- `apps/web-ui/src/store/simulationSlice.ts`
- `apps/web-ui/src/store/store.ts`
- `apps/web-ui/src/store/hooks.ts`

Pages/components:

- `apps/web-ui/src/pages/AlgorithmCatalog.tsx`
- `apps/web-ui/src/pages/SimulatorPage.tsx`
- `apps/web-ui/src/components/ParameterPanel.tsx`
- `apps/web-ui/src/components/VisualizationPanel.tsx`
- `apps/web-ui/src/components/GraphCanvas.tsx`
- `apps/web-ui/src/components/TraceViewer.tsx`
- `apps/web-ui/src/components/WarningBanner.tsx`
- `apps/web-ui/src/components/ReceiverModeSwitcher.tsx`
- `apps/web-ui/src/components/StepTimeline.tsx`
- `apps/web-ui/src/components/FormulaPanel.tsx`
- `apps/web-ui/src/components/ReferencesPanel.tsx`
- `apps/web-ui/src/components/ExplanationPanel.tsx`

## Tests Added

- `tests/unit/test_tokenization.py`
- `tests/unit/test_tfidf.py`
- `tests/unit/test_rake.py`
- `tests/unit/test_textrank.py`
- `tests/unit/test_naive_bayes.py`
- `tests/unit/test_svm.py`
- `tests/golden/test_golden_outputs.py`
- `tests/integration/test_api.py`

**Test Count: 49 passing tests**

The tests focus on deterministic classical algorithms and API schema behavior. Transformer model smoke tests are intentionally not included yet because they can require model downloads and heavier runtime dependencies.

## Infrastructure Added

- `infra/docker-compose.yml`
- `infra/Dockerfile.api`
- `infra/Dockerfile.classical`
- `infra/Dockerfile.transformer`

Compose includes:

- API gateway on port `8000`
- Classical service placeholder on port `8001`
- Transformer service placeholder on port `8002`
- PostgreSQL
- Redis

## Sample Data Added

- `datasets/examples/sentiment_labelled.csv`
- `datasets/examples/news_topics.csv`
- `datasets/examples/sample_corpus.txt`

## Verification Notes

Commands run:

```powershell
npm install
pip install -r services/classical-nlp-service/requirements.txt
python -m pytest tests -q
npm run build
```

Results:

- `npm install` completed successfully. npm reported two moderate audit findings in transitive dependencies.
- `python -m pytest tests -q` passed: **49 tests passed**.
- `npm run build` passed.

Vite emitted a non-fatal chunk-size warning because the bundled frontend JavaScript exceeds 500 kB after minification. Future work can add route-level code splitting or manual chunks.

Local API catalog verification loaded 13 algorithm entries:

- tokenization
- tfidf
- naive_bayes
- svm
- rake
- textrank
- word_embeddings
- lstm
- transformer_attention
- bert
- gpt
- t5
- fasttext

The transformer service `BaseSimulator` re-export was corrected to avoid a circular import through the ambiguous top-level `simulators.base` package name. This fixed the `/algorithms/` 500 error that caused the frontend catalog loading message.

## Known Follow-Up Work

- Add route-level code splitting or manual chunks to reduce frontend bundle size.
- Replace placeholder HTTP-server commands in `Dockerfile.classical` and `Dockerfile.transformer` with real service apps if those services become independently networked.
- Decide whether to rename `packages/shared-schemas` to `packages/shared_schemas` permanently. A compatibility alias exists now, but a single canonical package name would be cleaner.
- Add GitHub Actions for backend tests and frontend build.
- Add persistent run/export storage instead of in-memory `_run_store`.
