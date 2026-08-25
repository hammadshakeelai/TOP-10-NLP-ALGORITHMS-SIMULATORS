/**
 * SimulatorPage — generic wrapper rendered for every algorithm.
 *
 * Layout (SRS §UX-002):
 *   Receiver mode switcher
 *   Input panel → Parameters panel → Run / Load Demo buttons
 *   → Explanation panel → Step timeline → Formula cards
 *   → Visualizations → Trace viewer → References
 */
import { useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useAppDispatch, useAppSelector } from "../store/hooks";
import {
  selectAlgorithm,
  submitRun,
  loadAndRunDemo,
  updateRequest,
  setTraceLevel,
  setReceiverMode,
  clearRun,
  replayRun,
} from "../store/simulationSlice";
import type { AlgorithmID, RunRequest, TraceLevel, ReceiverMode } from "../types/api";
import TraceViewer from "../components/TraceViewer";
import VisualizationPanel from "../components/VisualizationPanel";
import ParameterPanel from "../components/ParameterPanel";
import WarningBanner from "../components/WarningBanner";
import ReceiverModeSwitcher from "../components/ReceiverModeSwitcher";
import StepTimeline from "../components/StepTimeline";
import FormulaPanel from "../components/FormulaPanel";
import ReferencesPanel from "../components/ReferencesPanel";
import ExplanationPanel from "../components/ExplanationPanel";
import CopyButton from "../components/CopyButton";
import { toast } from "../lib/toasts";

function downloadJson(filename: string, data: unknown) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function timeAgo(iso: string | undefined): string {
  if (!iso) return "";
  const seconds = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  if (seconds < 60) return `${Math.floor(seconds)}s ago`;
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  return `${Math.floor(seconds / 3600)}h ago`;
}

export default function SimulatorPage() {
  const { algorithmId } = useParams<{ algorithmId: string }>();
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  const {
    catalog,
    selectedAlgorithm,
    currentRun,
    runStatus,
    runError,
    traceLevel,
    receiverMode,
    currentRequest,
    runHistory,
  } = useAppSelector((s) => s.simulation);

  const entry = catalog.find((a) => a.id === algorithmId);

  useEffect(() => {
    if (algorithmId && algorithmId !== selectedAlgorithm) {
      dispatch(selectAlgorithm(algorithmId as AlgorithmID));
    }
  }, [algorithmId, selectedAlgorithm, dispatch]);

  useEffect(() => {
    document.title = entry ? `${entry.name} · NLP Simulator` : "NLP Simulator";
    return () => {
      document.title = "NLP Algorithm Simulator";
    };
  }, [entry]);

  if (!entry) {
    return (
      <div className="text-center mt-20 text-gray-400">
        <p>Algorithm not found: <code>{algorithmId}</code></p>
        <button onClick={() => navigate("/")} className="mt-4 text-indigo-700 dark:text-indigo-300 underline focus-ring rounded">
          Back to catalog
        </button>
      </div>
    );
  }

  function handleRun() {
    if (!algorithmId) return;
    const req: RunRequest = {
      algorithm_id: algorithmId as AlgorithmID,
      mode: "learning",
      trace_level: traceLevel,
      ...(currentRequest ?? {}),
    };
    dispatch(submitRun(req));
  }

  function handleLoadDemo() {
    if (!algorithmId) return;
    dispatch(loadAndRunDemo(algorithmId as AlgorithmID));
  }

  function handleExport() {
    if (!currentRun || !algorithmId) return;
    downloadJson(`run-${currentRun.run_id}.json`, currentRun);
    toast("Result exported as JSON.", "success", 2500);
  }

  const isRunning = runStatus === "running";
  const text = (currentRequest?.text as string) ?? "";

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div className="flex-1 min-w-[240px]">
          <button onClick={() => navigate("/")} className="text-sm text-gray-500 hover:text-gray-300 mb-1 focus-ring rounded">
            ← Catalog
          </button>
          <h1 className="text-2xl font-bold">{entry.name}</h1>
          <p className="text-gray-400 text-sm mt-1">{entry.description}</p>
        </div>
        <div className="flex items-center gap-2">
          <label htmlFor="trace-level" className="sr-only">Trace level</label>
          <select
            id="trace-level"
            value={traceLevel}
            onChange={(e) => dispatch(setTraceLevel(e.target.value as TraceLevel))}
            className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm focus-ring"
          >
            <option value="none">Trace: None</option>
            <option value="summary">Trace: Summary</option>
            <option value="full">Trace: Full</option>
          </select>
        </div>
      </div>

      {/* Receiver mode switcher */}
      <section className="bg-gray-900 border border-gray-800 rounded-xl p-4" aria-label="Learning depth">
        <div className="text-xs text-gray-500 mb-2 font-medium">Learning depth</div>
        <ReceiverModeSwitcher
          value={receiverMode}
          onChange={(mode: ReceiverMode) => dispatch(setReceiverMode(mode))}
        />
      </section>

      {/* Input */}
      <section className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold">Input</h2>
          {text.length > 0 && (
            <span className="text-xs text-gray-500 tabular-nums">
              {text.length.toLocaleString()} chars · ~{Math.max(1, Math.round(text.trim().split(/\s+/).length))} words
            </span>
          )}
        </div>
        <label htmlFor="simulator-input" className="sr-only">
          Input text for {entry.name}
        </label>
        <textarea
          id="simulator-input"
          rows={6}
          value={text}
          placeholder={
            entry.input_types.includes("documents")
              ? "Enter text here (for labelled docs use the JSON panel below)…"
              : "Paste your text here…"
          }
          className="w-full bg-gray-800 rounded-lg px-4 py-3 text-sm font-mono resize-y border border-gray-700 focus:border-indigo-500 outline-none transition-colors"
          onChange={(e) => dispatch(updateRequest({ text: e.target.value }))}
        />
      </section>

      {/* Parameters */}
      <ParameterPanel schema={entry.parameter_schema} />

      {/* Action buttons */}
      <div className="flex items-center flex-wrap gap-3">
        <button
          onClick={handleRun}
          disabled={isRunning}
          className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 disabled:cursor-not-allowed rounded-lg font-semibold transition focus-ring text-sm inline-flex items-center gap-2 min-w-[140px] justify-center"
        >
          {isRunning && (
            <svg aria-hidden className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-90" fill="currentColor" d="M4 12a8 8 0 018-8v3a5 5 0 00-5 5H4z" />
            </svg>
          )}
          {isRunning ? "Running…" : "Run Simulator"}
        </button>

        <button
          onClick={handleLoadDemo}
          disabled={isRunning}
          className="px-5 py-2.5 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:cursor-not-allowed border border-gray-600 rounded-lg font-semibold transition focus-ring text-sm"
        >
          Load Demo
        </button>

        {currentRun && (
          <>
            <button
              onClick={handleExport}
              className="px-4 py-2 border border-gray-700 hover:bg-gray-800 rounded-lg text-sm transition focus-ring"
            >
              Export JSON
            </button>
            <CopyButton
              value={() => JSON.stringify(currentRun.result, null, 2)}
              label="Copy result"
              className="text-xs text-gray-400 hover:text-white transition border border-gray-700 hover:bg-gray-800 rounded-lg px-4 py-2 focus-ring"
            />
            <button onClick={() => dispatch(clearRun())} className="text-sm text-gray-500 hover:text-gray-300 focus-ring rounded">
              Clear
            </button>
          </>
        )}

        {currentRun && (
          <span className="text-xs text-gray-500 ml-auto tabular-nums">
            {currentRun.metrics.runtime_ms.toFixed(1)} ms · v{currentRun.algorithm_version}
          </span>
        )}
      </div>

      {/* Run history */}
      {runHistory.length > 0 && (
        <details className="bg-gray-900/60 border border-gray-800 rounded-xl group">
          <summary className="flex items-center justify-between cursor-pointer select-none list-none px-4 py-3 text-sm text-gray-300 hover:text-white transition focus-ring rounded-xl">
            <span>
              History{" "}
              <span className="ml-1 text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded-full">
                {runHistory.length}
              </span>
            </span>
            <span aria-hidden className="text-gray-500 group-open:rotate-180 transition-transform">▾</span>
          </summary>
          <ul className="border-t border-gray-800 divide-y divide-gray-800/60">
            {runHistory.map((run, idx) => (
              <li key={`${run.run_id}-${idx}`}>
                <button
                  onClick={() => dispatch(replayRun(idx))}
                  disabled={isRunning}
                  className="w-full text-left px-4 py-2.5 text-xs hover:bg-gray-800/50 transition flex items-center gap-3 focus-ring disabled:opacity-50"
                >
                  <span className="font-mono text-emerald-600 dark:text-emerald-400">●</span>
                  <span className="font-medium text-gray-200">{run.algorithm_id}</span>
                  <span className="text-gray-500 truncate flex-1">{run.input_fingerprint.slice(0, 12)}</span>
                  <span className="text-gray-500 tabular-nums">{run.metrics.runtime_ms.toFixed(0)} ms</span>
                  <span className="text-gray-600 w-16 text-right">{timeAgo(run.timestamp)}</span>
                  {idx === 0 && <span className="chip bg-indigo-500/15 text-indigo-700 dark:text-indigo-300">latest</span>}
                </button>
              </li>
            ))}
          </ul>
        </details>
      )}

      {/* Error */}
      {runStatus === "error" && runError && (
        <div role="alert" className="bg-red-50 border border-red-200 dark:bg-red-950 dark:border-red-800 rounded-xl px-5 py-4 text-red-700 dark:text-red-300 text-sm">
          <span className="font-semibold mr-2">Run failed:</span>
          {runError}
        </div>
      )}

      {/* Warnings */}
      {currentRun?.warnings?.length ? <WarningBanner warnings={currentRun.warnings} /> : null}

      {/* Results */}
      {currentRun ? (
        <>
          {(currentRun.receiver_mode_explanations?.length > 0 || currentRun.research_context) && (
            <ExplanationPanel
              mode={receiverMode}
              explanations={currentRun.receiver_mode_explanations ?? []}
              researchContext={currentRun.research_context}
              teachingNotes={currentRun.teaching_notes}
            />
          )}

          {currentRun.step_explanations?.length > 0 && (
            <StepTimeline steps={currentRun.step_explanations} />
          )}

          {currentRun.formula_cards?.length > 0 && (
            <FormulaPanel cards={currentRun.formula_cards} />
          )}

          <VisualizationPanel specs={currentRun.visualization_specs} />

          <TraceViewer trace={currentRun.trace} result={currentRun.result} level={traceLevel} />

          {currentRun.references?.length > 0 && (
            <ReferencesPanel references={currentRun.references} />
          )}
        </>
      ) : (
        !isRunning &&
        runStatus !== "error" && (
          <div className="panel p-12 text-center animate-fade-in">
            <div className="text-4xl mb-3" aria-hidden>🧪</div>
            <h2 className="font-semibold text-gray-100 mb-1">No simulation yet</h2>
            <p className="text-sm text-gray-400 max-w-md mx-auto mb-5">
              Paste your own text and hit <strong>Run Simulator</strong>, or load the built-in demo to see{" "}
              {entry.name} in action with sample data.
            </p>
            <button
              onClick={handleLoadDemo}
              className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-semibold transition focus-ring"
            >
              Load Demo
            </button>
          </div>
        )
      )}
    </div>
  );
}
