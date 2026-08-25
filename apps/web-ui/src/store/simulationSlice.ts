/**
 * Redux slice for simulation state.
 *
 * Stores:
 *   - catalog (all algorithm entries)
 *   - current run request (inputs + parameters the user has set)
 *   - current run response (result, trace, viz specs, demo metadata)
 *   - receiver mode for layered explanations
 *   - run history (last 10 runs, for replay)
 *   - loading / error state
 */
import { createAsyncThunk, createSlice, type PayloadAction } from "@reduxjs/toolkit";
import { createRun, fetchCatalog, fetchDemoMetadata } from "../api/client";
import type {
  AlgorithmEntry,
  AlgorithmID,
  DemoMetadata,
  ReceiverMode,
  RunRequest,
  RunResponse,
  TraceLevel,
} from "../types/api";

// ── thunks ───────────────────────────────────────────────────────────────────

export const loadCatalog = createAsyncThunk("simulation/loadCatalog", fetchCatalog);

export const submitRun = createAsyncThunk(
  "simulation/submitRun",
  async (request: RunRequest) => createRun(request)
);

export const loadAndRunDemo = createAsyncThunk(
  "simulation/loadAndRunDemo",
  async (algorithmId: AlgorithmID, { dispatch }) => {
    const demo = await fetchDemoMetadata(algorithmId);
    const demoInput = demo.demo_input as Record<string, unknown>;

    const req: RunRequest = {
      algorithm_id: algorithmId,
      mode: "learning",
      trace_level: "full",
      parameters: demo.auto_parameters as Record<string, unknown>,
      ...(demoInput.text ? { text: demoInput.text as string } : {}),
      ...(demoInput.documents
        ? {
            documents: demoInput.documents as Array<{
              id: string;
              text: string;
              label?: string;
            }>,
          }
        : {}),
    };

    dispatch(updateRequest(req));
    return createRun(req);
  }
);

// ── state ─────────────────────────────────────────────────────────────────────

interface SimulationState {
  catalog: AlgorithmEntry[];
  catalogStatus: "idle" | "loading" | "ready" | "error";

  selectedAlgorithm: AlgorithmID | null;
  mode: "learning" | "experiment";
  traceLevel: TraceLevel;
  receiverMode: ReceiverMode;

  // The in-flight / last-submitted request
  currentRequest: RunRequest | null;

  // Results
  currentRun: RunResponse | null;
  runStatus: "idle" | "running" | "success" | "error";
  runError: string | null;

  // Cached demo metadata for the currently selected algorithm
  demoMetadata: DemoMetadata | null;

  // History (max 10 entries)
  runHistory: RunResponse[];

  // Replay — points at a historical run to display
  replayIndex: number | null;
}

const initialState: SimulationState = {
  catalog: [],
  catalogStatus: "idle",
  selectedAlgorithm: null,
  mode: "learning",
  traceLevel: "summary",
  receiverMode: "student",
  currentRequest: null,
  currentRun: null,
  runStatus: "idle",
  runError: null,
  demoMetadata: null,
  runHistory: [],
  replayIndex: null,
};

// ── slice ─────────────────────────────────────────────────────────────────────

const simulationSlice = createSlice({
  name: "simulation",
  initialState,
  reducers: {
    selectAlgorithm(state, action: PayloadAction<AlgorithmID>) {
      state.selectedAlgorithm = action.payload;
      state.currentRun = null;
      state.runError = null;
      state.replayIndex = null;
      state.demoMetadata = null;
    },
    setMode(state, action: PayloadAction<"learning" | "experiment">) {
      state.mode = action.payload;
    },
    setTraceLevel(state, action: PayloadAction<TraceLevel>) {
      state.traceLevel = action.payload;
    },
    setReceiverMode(state, action: PayloadAction<ReceiverMode>) {
      state.receiverMode = action.payload;
    },
    updateRequest(state, action: PayloadAction<Partial<RunRequest>>) {
      state.currentRequest = { ...(state.currentRequest ?? {} as RunRequest), ...action.payload };
    },
    clearRun(state) {
      state.currentRun = null;
      state.runStatus = "idle";
      state.runError = null;
    },
    replayRun(state, action: PayloadAction<number>) {
      const idx = action.payload;
      if (idx >= 0 && idx < state.runHistory.length) {
        state.replayIndex = idx;
        state.currentRun = state.runHistory[idx];
        state.runStatus = "success";
      }
    },
    clearReplay(state) {
      state.replayIndex = null;
    },
  },
  extraReducers(builder) {
    builder
      // catalog
      .addCase(loadCatalog.pending, (state) => { state.catalogStatus = "loading"; })
      .addCase(loadCatalog.fulfilled, (state, action) => {
        state.catalog = action.payload;
        state.catalogStatus = "ready";
      })
      .addCase(loadCatalog.rejected, (state) => { state.catalogStatus = "error"; })

      // manual run
      .addCase(submitRun.pending, (state) => {
        state.runStatus = "running";
        state.runError = null;
        state.currentRun = null;
        state.replayIndex = null;
      })
      .addCase(submitRun.fulfilled, (state, action) => {
        state.runStatus = "success";
        state.currentRun = action.payload;
        const stamped = { ...action.payload, timestamp: new Date().toISOString() };
        state.runHistory = [stamped, ...state.runHistory].slice(0, 10);
      })
      .addCase(submitRun.rejected, (state, action) => {
        state.runStatus = "error";
        state.runError = action.error.message ?? "Unknown error.";
      })

      // demo load + run
      .addCase(loadAndRunDemo.pending, (state) => {
        state.runStatus = "running";
        state.runError = null;
        state.currentRun = null;
        state.replayIndex = null;
      })
      .addCase(loadAndRunDemo.fulfilled, (state, action) => {
        state.runStatus = "success";
        state.currentRun = action.payload;
        const stamped = { ...action.payload, timestamp: new Date().toISOString() };
        state.runHistory = [stamped, ...state.runHistory].slice(0, 10);
      })
      .addCase(loadAndRunDemo.rejected, (state, action) => {
        state.runStatus = "error";
        state.runError = action.error.message ?? "Unknown error loading demo.";
      });
  },
});

export const {
  selectAlgorithm,
  setMode,
  setTraceLevel,
  setReceiverMode,
  updateRequest,
  clearRun,
  replayRun,
  clearReplay,
} = simulationSlice.actions;

export default simulationSlice.reducer;
