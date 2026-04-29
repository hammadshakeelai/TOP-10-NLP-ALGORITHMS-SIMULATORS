# TOP-10-NLP-ALGORITHMS-SIMULATORS

Interactive NLP Algorithm Simulator Platform for learning, testing, tracing, visualizing, and exporting NLP algorithm behavior.

## What This Project Does

The platform exposes a common simulator API for NLP algorithms. A user can choose an algorithm, enter text or small datasets, configure parameters, run the simulation, inspect intermediate trace data, view charts/graphs, and export results.

The implementation is based on the SRS in `NLP_Algorithm_Simulators_SRS.docx`.

## Implemented Algorithms

Classical NLP:

- Tokenization - whitespace, regex, toy BPE, toy WordPiece, offsets, token traces
- TF-IDF - from-scratch TF, IDF, TF-IDF, cosine similarity, query ranking
- Naive Bayes - MultinomialNB, priors, likelihoods, probabilities, confusion matrix
- SVM - LinearSVC with calibrated probabilities, margins, top features
- RAKE - from-scratch candidate phrases, word degree/frequency scores, co-occurrence graph
- TextRank - keyword and summary modes with PageRank convergence trace

Transformer and neural simulators:

- Word embeddings - toy SVD embeddings, optional pretrained vectors, PCA projection, analogy
- LSTM - toy recurrent gate trace with hidden/cell states
- Transformer attention - multi-head attention from scratch, positional encodings, causal mask
- BERT - HuggingFace pipeline wrapper for MLM/sentiment/NER/QA
- GPT - HuggingFace generation wrapper with decoding parameters
- T5 - text-to-text wrapper with beam candidates
- FastText - subword breakdown and supervised classification path

## Repository Layout

```text
apps/
  api-gateway/          FastAPI gateway
  web-ui/               React + TypeScript + Vite UI
datasets/examples/      sample datasets
docs/                   implementation documentation
infra/                  Docker Compose and Dockerfiles
packages/
  shared-schemas/       original Pydantic schema source
  shared_schemas/       importable Python package alias
services/
  classical-nlp-service/
  transformer-service/
  export-service/
tests/
  unit/
  golden/
  integration/
```

## Quick Start

For the most detailed Windows run instructions, see `docs/RUNBOOK.md`.

### Backend

```powershell
cd C:\Users\HP\Documents\GitHub\ai-ml\TOP-10-NLP-ALGORITHMS-SIMULATORS
pip install -r services/classical-nlp-service/requirements.txt
uvicorn main:app --app-dir apps/api-gateway --reload --port 8000
```

Open:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/algorithms/`
- `http://127.0.0.1:8000/docs`

`http://127.0.0.1:8000/` returns `404 Not Found`; this is normal because the API does not define a homepage route.

### Frontend

```powershell
cd C:\Users\HP\Documents\GitHub\ai-ml\TOP-10-NLP-ALGORITHMS-SIMULATORS\apps\web-ui
npm install
npm run dev
```

Open:

- `http://localhost:5173`

### Docker Compose

```powershell
docker compose -f infra/docker-compose.yml up --build
```

Services:

- API gateway: `http://localhost:8000`
- Classical service placeholder: `http://localhost:8001`
- Transformer service placeholder: `http://localhost:8002`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

## Running Tests

Install backend dependencies first:

```powershell
pip install -r services/classical-nlp-service/requirements.txt
python -m pytest tests -q
```

Build the frontend:

```powershell
cd apps/web-ui
npm run build
```

Expected verification status:

- `python -m pytest tests -q` -> `36 passed`
- `npm run build` -> successful Vite build

## Troubleshooting

If the frontend says `Failed to load catalog. Is the API running?`, open:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/algorithms/`

If `/health` works but `/algorithms/` fails, restart the backend:

```powershell
CTRL+C
uvicorn main:app --app-dir apps\api-gateway --reload --port 8000
```

Then refresh `http://localhost:5173`.

## API Overview

Catalog:

```http
GET /algorithms/
GET /algorithms/{algorithm_id}
```

Runs:

```http
POST /runs/
GET /runs/{run_id}
```

Exports:

```http
POST /exports/{run_id}
```

Health:

```http
GET /health
```

Example run request:

```json
{
  "algorithm_id": "tfidf",
  "mode": "learning",
  "documents": [
    {"id": "d1", "text": "NLP transforms text into features."},
    {"id": "d2", "text": "TF-IDF ranks important terms in documents."}
  ],
  "parameters": {
    "top_n": 10,
    "smooth_idf": true
  },
  "trace_level": "full"
}
```

## Implementation Notes

- All simulators return shared Pydantic `RunResponse` objects.
- Visualization output is carried through `visualization_specs`.
- Frontend dispatches `bar`, `heatmap`, `scatter`, `line`, `table`, `diff`, and `graph` specs.
- `@xyflow/react` powers graph visualization for RAKE and TextRank.
- Exports currently return JSON and CSV payloads from in-memory run data.
- Persistent storage is not wired yet.

See `docs/IMPLEMENTATION_STATUS.md` for a full implementation log, verification notes, and known follow-up work.
