# NLP Algorithm Simulator Platform - Implementation Status

Last updated: April 29, 2026

## Summary

This repository has been expanded from a placeholder into a working full-stack NLP Algorithm Simulator Platform skeleton with implemented simulator modules, shared API contracts, a FastAPI gateway, a React/Vite frontend, test coverage scaffolding, sample datasets, Docker infrastructure, and export stubs.

The platform follows the SRS in `NLP_Algorithm_Simulators_SRS.docx`: every simulator implements a common pipeline of `validate`, `preprocess`, `run`, `trace`, `visualize`, and `serialize_result`, returning a shared `RunResponse` with `algorithm_version`, `input_fingerprint`, `runtime_ms`, warnings, trace data, and visualization specs.

## New in Sprint 5

- **Offline demo mode (no backend required)** — the frontend now works as a fully static site:
  - `apps/web-ui/scripts/generate-mocks.py` runs every simulator registry in-process and snapshots the catalog, per-algorithm demo metadata, and pre-computed demo run results into `apps/web-ui/src/mocks/` (13/13 algorithms). Regenerate with `python apps/web-ui/scripts/generate-mocks.py` after changing simulator code.
  - `src/api/client.ts` falls back to these snapshots on network failure, flags offline mode, and canned runs carry an `OFFLINE_MODE` warning. Header shows an "Offline demo" badge and "Demo data" status; custom inputs replay the algorithm's canned demo result.
  - Transformer snapshots generated with `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1` so no model downloads occur.
- **Fixed 3 real backend demo bugs** found while snapshotting (all would fail on the live API too):
  - `svm.py` — stratified hold-out split crashed on tiny corpora (`test_size=1 < n_classes=2`); test size now widens to ≥1 sample per class, and probability calibration falls back to the raw LinearSVC when a class has <2 training examples.
  - `word_embeddings.py` — 2D projection crashed with `IndexError` when the target word was absent from the vocabulary (word list and vector rows desynced); lists now filtered once and kept index-aligned.
  - `word_embeddings` demo metadata — `auto_parameters` used key names the simulator never read (`embedding_dim`/`window_size`/`algorithm`); replaced with the real contract (`model_type`, `vector_dim`, `context_window`, `target_word`, `analogy`).
  - `bert_sim.py` — `visualize()` raised `KeyError('token')` when the transformers pipeline was unavailable and predictions carried `{"error": ...}`; chart builders now skip error entries.
- **E2E smoke test** — `apps/web-ui/scripts/ui-smoke-test.py` (Playwright + system Chrome, no backend): 14 checks covering catalog render, search, simulator flow, offline demo run, run history, export, theme persistence, and 404. **14/14 passing.**
- Backend tests: **49 passing** after the simulator fixes.

## New in Sprint 4

- **Fixed a fatal frontend build bug** — the inline SVG favicon in `index.html` contained raw `%` characters that crashed Vite's HTML pipeline ("URI malformed"). The favicon now lives at `apps/web-ui/public/favicon.svg`.
- **Route-level code splitting** — pages load via `React.lazy` + `Suspense`; Vite `manualChunks` split `react`, `state` (redux/axios), `charts` (recharts), and `flow` (@xyflow/react). Initial page weight dropped from a single 834 kB bundle (~250 kB gzip) to ~254 kB (~87 kB gzip); chart and graph libraries load only on the simulator page.
- **Robustness shell** — global `ErrorBoundary` with retry/recover UI, catch-all 404 route, page-level Suspense loader, scroll restoration, `noscript` fallback, and a lightweight toast system (`src/lib/toasts.ts`) with `CopyButton` clipboard helper (with `execCommand` fallback).
- **Dark/light theme** — the gray ramp is driven by CSS variables (`--g-*` in `src/index.css`, consumed via Tailwind `<alpha-value>`), toggled by a header button, persisted in `localStorage`, and applied pre-paint by an inline script in `index.html` to avoid FOUC. Accent colors use `dark:` pairs where contrast requires it.
- **Accessibility** — skip-to-content link, `aria-expanded`/`aria-pressed`/`aria-live` on interactive controls, labelled form fields (`htmlFor`/`aria-describedby`), visible `:focus-visible` rings, `prefers-reduced-motion` support, and per-route `document.title` updates.
- **Simulator UX** — run history panel with one-click replay (uses the previously dormant `runHistory`/`replayRun` state), JSON export download, copy-result button, character/word counter, empty state with demo CTA, spinner on the run button, and a `/` keyboard shortcut that focuses catalog search.
- **SEO/meta** — Open Graph/Twitter tags and `color-scheme` metadata in `index.html`.

Verified: `npm run build` passes (no chunk-size warnings), `python -m pytest tests -q` → 49 passed. Rendered output smoke-tested headlessly in Chrome (dark, light, and 404 routes).

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

- Replace placeholder HTTP-server commands in `Dockerfile.classical` and `Dockerfile.transformer` with real service apps if those services become independently networked.
- Decide whether to rename `packages/shared-schemas` to `packages/shared_schemas` permanently. A compatibility alias exists now, but a single canonical package name would be cleaner.
- Add GitHub Actions for backend tests and frontend build.
- Add persistent run/export storage instead of in-memory `_run_store`.
- Remove unused `d3` and `react-diff-viewer-continued` dependencies from `apps/web-ui/package.json` (not imported anywhere; tree-shaken from builds today).
