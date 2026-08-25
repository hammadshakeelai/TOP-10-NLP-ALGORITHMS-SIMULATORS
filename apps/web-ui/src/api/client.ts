import axios, { type AxiosInstance, type AxiosError } from "axios";
import type { AlgorithmEntry, DemoMetadata, RunRequest, RunResponse, WarningEntry } from "../types/api";
import { toast } from "../lib/toasts";
import catalogMock from "../mocks/catalog.json";

// ── offline / static demo mode ───────────────────────────────────────────────
// Two ways the UI runs without a live backend, both served by the pre-computed
// snapshots in src/mocks/:
//
//   static  — VITE_STATIC_MODE=true at build time. This is a deliberate
//             backend-free deployment (GitHub Pages et al). No request is ever
//             attempted, so there is no failed call and no alarming toast.
//   offline — the backend was expected but turned out to be unreachable. The
//             UI degrades to the same snapshots and warns the user once.
//
// In both cases custom inputs replay the canned demo result for their algorithm.

const STATIC_MODE = import.meta.env.VITE_STATIC_MODE === "true";

let offlineMode = STATIC_MODE;
const offlineListeners = new Set<(value: boolean) => void>();

export function isOfflineMode(): boolean {
  return offlineMode;
}

/** True when this build was compiled as a backend-free static deployment. */
export function isStaticMode(): boolean {
  return STATIC_MODE;
}

export function onOfflineModeChange(cb: (value: boolean) => void): () => void {
  offlineListeners.add(cb);
  return () => {
    offlineListeners.delete(cb);
  };
}

function enterOfflineMode() {
  if (offlineMode) return;
  offlineMode = true;
  toast(
    "API unreachable — switched to offline demo mode with pre-computed results.",
    "info",
    6000
  );
  offlineListeners.forEach((cb) => cb(true));
}

const demoLoaders = import.meta.glob<{ default: DemoMetadata }>("../mocks/demos/*.json");
const runLoaders = import.meta.glob<{ default: RunResponse }>("../mocks/runs/*.json");

async function loadMock<T>(loaders: Record<string, () => Promise<{ default: unknown }>>, id: string): Promise<T> {
  const key = Object.keys(loaders).find((k) => k.endsWith(`/${id}.json`));
  if (!key) throw new Error(`No offline snapshot available for '${id}'.`);
  const mod = await loaders[key]();
  return mod.default as T;
}

function cannedRun(request: RunRequest): Promise<RunResponse> {
  return loadMock<RunResponse>(runLoaders, request.algorithm_id).then((run) => {
    const offlineWarning: WarningEntry = STATIC_MODE
      ? {
          code: "STATIC_MODE",
          message:
            "Static demo build — showing the pre-computed reference result for this algorithm.",
          suggestion:
            "Run the platform locally with the FastAPI backend to simulate your own inputs.",
        }
      : {
          code: "OFFLINE_MODE",
          message: "API offline — showing the pre-computed demo result for this algorithm.",
          suggestion: "Start the FastAPI backend to simulate your own inputs.",
        };
    const clone: RunResponse = JSON.parse(JSON.stringify(run));
    clone.run_id = generateRunId();
    clone.warnings = [...(clone.warnings ?? []), offlineWarning];
    return clone;
  });
}

function generateRunId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `offline-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

// ── http client ──────────────────────────────────────────────────────────────

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const http: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 60_000,
  headers: { "Content-Type": "application/json" },
});

// ── response interceptor — normalise errors, detect network loss ────────────
http.interceptors.response.use(
  (res) => res,
  (err: AxiosError<{ detail?: string }>) => {
    if (!err.response) {
      // Request never reached a server — network down or backend not started.
      enterOfflineMode();
      return Promise.reject(new Error("API unreachable — offline demo mode active."));
    }
    const message =
      err.response.data?.detail ?? err.message ?? "An unexpected error occurred.";
    return Promise.reject(new Error(message));
  }
);

// ── API methods (with offline fallbacks) ─────────────────────────────────────

export async function fetchCatalog(): Promise<AlgorithmEntry[]> {
  if (offlineMode) return catalogMock as AlgorithmEntry[];
  try {
    const { data } = await http.get<AlgorithmEntry[]>("/algorithms/");
    return data;
  } catch (err) {
    if (offlineMode) return catalogMock as AlgorithmEntry[];
    throw err;
  }
}

export async function fetchAlgorithm(id: string): Promise<AlgorithmEntry> {
  if (offlineMode) {
    const entry = (catalogMock as AlgorithmEntry[]).find((a) => a.id === id);
    if (!entry) throw new Error(`Algorithm '${id}' not found.`);
    return entry;
  }
  const { data } = await http.get<AlgorithmEntry>(`/algorithms/${id}`);
  return data;
}

export async function fetchDemoMetadata(id: string): Promise<DemoMetadata> {
  if (offlineMode) return loadMock<DemoMetadata>(demoLoaders, id);
  try {
    const { data } = await http.get<DemoMetadata>(`/algorithms/${id}/demo`);
    return data;
  } catch (err) {
    if (offlineMode) return loadMock<DemoMetadata>(demoLoaders, id);
    throw err;
  }
}

export async function createRun(request: RunRequest): Promise<RunResponse> {
  if (offlineMode) return cannedRun(request);
  try {
    const { data } = await http.post<RunResponse>("/runs/", request);
    return data;
  } catch (err) {
    if (offlineMode) return cannedRun(request);
    throw err;
  }
}

export async function fetchRun(runId: string): Promise<RunResponse> {
  if (offlineMode)
    throw new Error(
      STATIC_MODE
        ? "Run history is not available in the static demo build."
        : "Run history lookup requires the API backend."
    );
  const { data } = await http.get<RunResponse>(`/runs/${runId}`);
  return data;
}

export async function checkHealth(): Promise<{ status: string }> {
  if (offlineMode) return { status: STATIC_MODE ? "static" : "offline" };
  const { data } = await http.get<{ status: string }>("/health");
  return data;
}
