import axios, { type AxiosInstance, type AxiosError } from "axios";
import type { AlgorithmEntry, DemoMetadata, RunRequest, RunResponse } from "../types/api";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const http: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 60_000,
  headers: { "Content-Type": "application/json" },
});

// ── response interceptor — normalise errors ──────────────────────────────────
http.interceptors.response.use(
  (res) => res,
  (err: AxiosError<{ detail?: string }>) => {
    const message =
      err.response?.data?.detail ?? err.message ?? "An unexpected error occurred.";
    return Promise.reject(new Error(message));
  }
);

// ── API methods ───────────────────────────────────────────────────────────────

export async function fetchCatalog(): Promise<AlgorithmEntry[]> {
  const { data } = await http.get<AlgorithmEntry[]>("/algorithms/");
  return data;
}

export async function fetchAlgorithm(id: string): Promise<AlgorithmEntry> {
  const { data } = await http.get<AlgorithmEntry>(`/algorithms/${id}`);
  return data;
}

export async function fetchDemoMetadata(id: string): Promise<DemoMetadata> {
  const { data } = await http.get<DemoMetadata>(`/algorithms/${id}/demo`);
  return data;
}

export async function createRun(request: RunRequest): Promise<RunResponse> {
  const { data } = await http.post<RunResponse>("/runs/", request);
  return data;
}

export async function fetchRun(runId: string): Promise<RunResponse> {
  const { data } = await http.get<RunResponse>(`/runs/${runId}`);
  return data;
}

export async function checkHealth(): Promise<{ status: string }> {
  const { data } = await http.get<{ status: string }>("/health");
  return data;
}
