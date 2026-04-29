# Runbook - NLP Algorithm Simulator Platform

This guide explains how to run the project locally on Windows PowerShell, verify that it is working, troubleshoot common errors, and publish the work to GitHub.

## 1. Requirements

Install these before running the app:

- Python 3.11 or newer
- pip
- Node.js 18 or newer
- npm
- Git

The current tested environment used Anaconda Python and standard npm.

## 2. Run Locally

Use two PowerShell windows.

### Window 1 - Backend API

```powershell
cd C:\Users\HP\Documents\GitHub\ai-ml\TOP-10-NLP-ALGORITHMS-SIMULATORS
pip install -r services\classical-nlp-service\requirements.txt
uvicorn main:app --app-dir apps\api-gateway --reload --port 8000
```

Keep this window open. The backend is running when you see:

```text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

Open these backend URLs in the browser:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/algorithms/`
- `http://127.0.0.1:8000/docs`

Important: `http://127.0.0.1:8000/` returns `404 Not Found` because there is no API homepage route. That is normal.

### Window 2 - Frontend UI

```powershell
cd C:\Users\HP\Documents\GitHub\ai-ml\TOP-10-NLP-ALGORITHMS-SIMULATORS\apps\web-ui
npm install
npm run dev
```

Open the UI:

- `http://localhost:5173`

## 3. One-Box Command Reference

```powershell
# BACKEND - PowerShell window 1
cd C:\Users\HP\Documents\GitHub\ai-ml\TOP-10-NLP-ALGORITHMS-SIMULATORS
pip install -r services\classical-nlp-service\requirements.txt
uvicorn main:app --app-dir apps\api-gateway --reload --port 8000

# Test backend:
# http://127.0.0.1:8000/health
# http://127.0.0.1:8000/algorithms/
# http://127.0.0.1:8000/docs

# FRONTEND - PowerShell window 2
cd C:\Users\HP\Documents\GitHub\ai-ml\TOP-10-NLP-ALGORITHMS-SIMULATORS\apps\web-ui
npm install
npm run dev

# Open app:
# http://localhost:5173
```

## 4. Verify Everything

From the repository root:

```powershell
python -m pytest tests -q
```

Expected result:

```text
36 passed
```

From the frontend folder:

```powershell
cd C:\Users\HP\Documents\GitHub\ai-ml\TOP-10-NLP-ALGORITHMS-SIMULATORS\apps\web-ui
npm run build
```

Expected result:

```text
vite build
built
```

Vite may print a non-fatal chunk-size warning. The build is still successful.

## 5. Troubleshooting

### Frontend says: Failed to load catalog. Is the API running?

Check the backend first:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/algorithms/
```

If `/health` works but `/algorithms/` fails, restart the backend:

```powershell
CTRL+C
uvicorn main:app --app-dir apps\api-gateway --reload --port 8000
```

Then refresh:

```text
http://localhost:5173
```

### `GET /` returns 404

This is normal. Use these routes instead:

- `/health`
- `/algorithms/`
- `/docs`

### Port 8000 is already in use

Stop the existing backend with `CTRL+C`, or run on another port:

```powershell
uvicorn main:app --app-dir apps\api-gateway --reload --port 8005
```

If you change the backend port, set the frontend API URL:

```powershell
$env:VITE_API_URL="http://127.0.0.1:8005"
npm run dev
```

### Port 5173 is already in use

Vite may automatically choose another port. Use the URL printed by `npm run dev`.

### Transformer libraries are missing

The default catalog and classical algorithms run with `services/classical-nlp-service/requirements.txt`.

Some transformer simulators may need additional dependencies:

```powershell
pip install -r services\transformer-service\requirements.txt
```

Those dependencies are heavier because they include model-related libraries.

## 6. What Was Implemented

Backend:

- FastAPI gateway
- `/health`
- `/algorithms/`
- `/runs/`
- `/exports/{run_id}`
- shared Pydantic schemas
- classical simulator registry
- transformer simulator registry
- JSON and CSV export stub

Classical simulators:

- Tokenization
- TF-IDF
- Naive Bayes
- SVM
- RAKE
- TextRank

Transformer and neural simulators:

- Word embeddings
- LSTM
- Transformer attention
- BERT
- GPT
- T5
- FastText

Frontend:

- React/Vite app shell
- algorithm catalog page
- generic simulator page
- parameter panel
- warning banner
- visualization panel
- trace viewer
- graph visualization with `@xyflow/react`

Testing:

- Unit tests
- Golden output tests
- API integration test

Data and infrastructure:

- example sentiment dataset
- example news topics dataset
- sample corpus
- Docker Compose
- Dockerfiles

## 7. GitHub Publish Guide

From the repo root:

```powershell
git status --short
git switch -c codex/nlp-simulator-platform
python -m pytest tests -q
cd apps\web-ui
npm install
npm run build
cd ..\..
git add AGENTS.md CLAUDE.md README.md apps datasets docs infra packages services tests
git commit -m "Build NLP algorithm simulator platform"
git push -u origin codex/nlp-simulator-platform
gh pr create --draft --title "Build NLP algorithm simulator platform" --body "Implements the NLP simulator platform skeleton, shared schemas, classical and transformer registries, React UI, exports, tests, datasets, infrastructure, and documentation."
```

If GitHub CLI is not authenticated:

```powershell
gh auth login
```

GitHub Pages can host only the static frontend build. The FastAPI backend must run on a server or cloud platform such as Render, Railway, Fly.io, Azure Container Apps, AWS ECS, or a VM with Docker Compose.
