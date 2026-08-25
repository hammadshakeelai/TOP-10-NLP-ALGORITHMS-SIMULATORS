# CLAUDE.md

Guidance for Claude Code when continuing, testing, and publishing this repository.

## Project State

This is no longer an empty repository. It contains a production-oriented NLP Algorithm Simulator Platform skeleton with:

- FastAPI API gateway
- implemented classical simulator modules
- implemented transformer/neural simulator modules
- shared Pydantic schemas
- React/Vite frontend
- graph visualization with `@xyflow/react`
- JSON/CSV export stub
- unit, golden, and integration tests
- sample datasets
- Docker Compose infrastructure

Read `docs/IMPLEMENTATION_STATUS.md` before making changes.

## Local Setup

Use `docs/RUNBOOK.md` as the source of truth for local Windows startup and troubleshooting.

Backend dependencies:

```powershell
pip install -r services/classical-nlp-service/requirements.txt
```

Run API gateway:

```powershell
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

Local URLs:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/algorithms/`
- `http://127.0.0.1:8000/docs`
- `http://localhost:5173`

`http://127.0.0.1:8000/` returns 404 by design.

## Architecture

API gateway:

- `apps/api-gateway/main.py`
- routes: health, algorithms, runs, exports

Shared schemas:

- Canonical source: `packages/shared-schemas/models.py`
- Importable Python alias: `packages/shared_schemas`

Classical simulators:

- `services/classical-nlp-service/simulators`
- registry: `services/classical-nlp-service/registry.py`

Transformer simulators:

- `services/transformer-service/simulators`
- registry: `services/transformer-service/registry.py`

Frontend:

- catalog page: `apps/web-ui/src/pages/AlgorithmCatalog.tsx`
- simulator page: `apps/web-ui/src/pages/SimulatorPage.tsx`
- visualization dispatcher: `apps/web-ui/src/components/VisualizationPanel.tsx`
- graph canvas: `apps/web-ui/src/components/GraphCanvas.tsx`

## Verification Status

Verification commands:

```powershell
pip install -r services/classical-nlp-service/requirements.txt pytest
python -m pytest tests -q
cd apps/web-ui
npm install
npm run build
```

Status as of 2026-08-25:

- Frontend production build: **passes**.
- Static (backend-free) build: **passes**, deployed and verified live.
- Backend tests: **not currently runnable on this machine.** No interpreter on
  PATH has pytest — the Python 3.13 environment that once reported 49 passed is
  gone. Rebuild an environment and re-run before claiming any pass count. Do
  not repeat the 49 figure as verified.
- npm reports two moderate audit findings in transitive dependencies.

The catalog loads 13 algorithm entries.

Node 24 is required. `npm ci` fails on Node 20 with
`Missing: yaml@2.9.0 from lock file`, because `yaml@2` is an optional peer of
`postcss-load-config` that npm 10 and npm 11 disagree about.

## GitHub Publishing Guide

The project is already published and deployed. Read this before any git work.

**The repository keeps exactly one branch: `main`.** A previous
`codex/nlp-simulator-platform` branch was fast-forwarded into `main` and
deleted on both sides. Do not recreate it — GitHub Pages deploys from `main`
alone, so a second long-lived branch means whichever pushed last wins the
deployment.

**Never stage whole directories.** An earlier `git add apps` ran before any
`.gitignore` existed and committed 12,304 `node_modules` files. `.gitignore`
now covers `node_modules/`, `dist/` and `__pycache__/`, but stage explicit
paths anyway:

```powershell
git status --short
git add <specific files>
git commit -m "<message>"
git push origin main
```

Pushing to `main` with changes under `apps/web-ui/**` triggers
`.github/workflows/deploy-pages.yml`, which rebuilds and republishes the live
site. Check it afterwards:

```powershell
gh run list --workflow=deploy-pages.yml --branch=main --limit 3
```

## Deployment Notes

**Live now:** https://hammadshakeelai.github.io/TOP-10-NLP-ALGORITHMS-SIMULATORS/

That is the backend-free static build (`VITE_STATIC_MODE=true`), serving the
pre-computed snapshots in `apps/web-ui/src/mocks/`. Custom input replays the
reference run rather than simulating it. See `docs/STATIC_DEPLOY.md`.

GitHub Pages can host only the static frontend; it cannot run the FastAPI backend, PostgreSQL, Redis, or transformer services.

For a real running deployment, use one of these:

- Docker Compose on a VM
- Render
- Railway
- Fly.io
- Azure Container Apps
- AWS ECS
- a Kubernetes cluster

Minimal Docker deployment command on a server:

```powershell
docker compose -f infra/docker-compose.yml up --build -d
```

If deploying the frontend separately, set the frontend API base URL to the hosted API gateway URL. The current frontend client defaults should be reviewed before production deployment.

## Next Recommended Work

- Rebuild a Python environment so the backend test suite can be run again.
- Add a backend CI workflow for pytest (needs the above first).
- Tier-2 static mode: port tokenization, RAKE, TF-IDF, TextRank and Naive Bayes
  to TypeScript so the static site simulates real user input instead of
  replaying snapshots.
- Replace placeholder service commands in `Dockerfile.classical` and
  `Dockerfile.transformer` with real entrypoints if these become separately
  networked services.
- Add persistent storage for runs and exports.
- Decide whether to rename `packages/shared-schemas` to `packages/shared_schemas`
  permanently.

Already done: GitHub Actions for the frontend build, frontend manual chunks,
`.gitignore`, static deployment.
