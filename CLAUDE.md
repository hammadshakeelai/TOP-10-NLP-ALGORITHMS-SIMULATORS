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

Verified commands:

```powershell
npm install
pip install -r services/classical-nlp-service/requirements.txt
python -m pytest tests -q
npm run build
```

Current result:

- Backend tests pass: 49 passed.
- Frontend production build passes.
- npm reports two moderate audit findings in transitive dependencies.
- Vite reports a non-fatal chunk-size warning for the production bundle.

Last local catalog verification loaded 13 algorithm entries.

## GitHub Publishing Guide

Use this when asked to deploy or publish the project to GitHub.

1. Check current work:

```powershell
git status --short
```

2. Create a branch:

```powershell
git switch -c codex/nlp-simulator-platform
```

3. Install and verify:

```powershell
pip install -r services/classical-nlp-service/requirements.txt
python -m pytest tests -q
cd apps/web-ui
npm install
npm run build
cd ..\..
```

4. Review changed files:

```powershell
git diff --stat
git diff
```

5. Stage and commit:

```powershell
git add AGENTS.md CLAUDE.md README.md apps datasets docs infra packages services tests
git commit -m "Build NLP algorithm simulator platform"
```

6. Push to GitHub:

```powershell
git push -u origin codex/nlp-simulator-platform
```

7. Open a pull request with GitHub CLI:

```powershell
gh pr create --draft --title "Build NLP algorithm simulator platform" --body "Implements the NLP simulator platform skeleton, shared schemas, classical and transformer registries, React UI, exports, tests, datasets, infrastructure, and documentation."
```

If `gh` is not authenticated:

```powershell
gh auth login
```

## Deployment Notes

GitHub itself can host the repository and run CI. GitHub Pages can host only the static frontend build; it cannot run the FastAPI backend, PostgreSQL, Redis, or transformer services.

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

- Add GitHub Actions for backend tests and frontend build.
- Add frontend code splitting or manual chunks to reduce bundle size.
- Replace placeholder independent service commands in `Dockerfile.classical` and `Dockerfile.transformer` with real service entrypoints if these become separately networked services.
- Add persistent storage for runs and exports.
- Decide whether to rename `packages/shared-schemas` to `packages/shared_schemas` permanently.
