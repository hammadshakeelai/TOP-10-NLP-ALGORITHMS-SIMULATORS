"""
NLP Simulator API Gateway
FastAPI application — entry point for all simulator requests.

Routes:
  GET  /algorithms           → catalog
  GET  /algorithms/{id}      → single algorithm metadata
  POST /runs                 → execute a simulator
  GET  /runs/{run_id}        → retrieve a stored run (stub)
  POST /exports/{run_id}     → generate export artifact (stub)
  GET  /health               → health check
"""
from __future__ import annotations

import sys, os, time, uuid, json
from contextlib import asynccontextmanager
from pathlib import Path

# Make packages importable
ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "packages"))
sys.path.insert(0, str(ROOT / "services" / "classical-nlp-service"))
sys.path.insert(0, str(ROOT / "services" / "transformer-service"))

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from shared_schemas import AlgorithmID, RunRequest, RunResponse, RunStatus

from routers import algorithms, exports, health, runs


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("NLP Simulator API starting...")
    yield
    print("NLP Simulator API shutting down.")


app = FastAPI(
    title="NLP Algorithm Simulator API",
    description="Interactive simulation and visualization of NLP algorithms.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_timing(request: Request, call_next):
    t = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time-Ms"] = str(round((time.perf_counter() - t) * 1000, 1))
    return response


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc)},
    )


app.include_router(health.router)
app.include_router(algorithms.router, prefix="/algorithms", tags=["Catalog"])
app.include_router(runs.router, prefix="/runs", tags=["Simulator Runs"])
app.include_router(exports.router, prefix="/exports", tags=["Exports"])
