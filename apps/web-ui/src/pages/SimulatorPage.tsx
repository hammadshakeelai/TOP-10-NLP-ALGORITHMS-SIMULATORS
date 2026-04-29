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
  } = useAppSelector((s) => s.simulation);

  const entry = catalog.find((a) => a.id === algorithmId);

  useEffect(() => {
    if (algorithmId && algorithmId !== selectedAlgorithm) {
      dispatch(selectAlgorithm(algorithmId as AlgorithmID));
    }
  }, [algorithmId, selectedAlgorithm, dispatch]);

  if (!entry) {
    return (
      <div className="text-center mt-20 text-gray-400">
        <p>Algorithm not found: <code>{algorithmId}</code></p>
        <button onClick={() => navigate("/")} className="mt-4 text-indigo-400 underline">
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

  const isRunning = runStatus === "running";

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <button onClick={() => navigate("/")} className="text-sm text-gray-500 hover:text-gray-300 mb-1">
            ← Catalog
          </button>
          <h1 className="text-2xl font-bold">{entry.name}</h1>
          <p className="text-gray-400 text-sm mt-1">{entry.description}</p>
        </div>
        <select
          value={traceLevel}
          onChange={(e) => dispatch(setTraceLevel(e.target.value as TraceLevel))}
          className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm"
        >
          <option value="none">Trace: None</option>
          <option value="summary">Trace: Summary</option>
          <option value="full">Trace: Full</option>
        </select>
      </div>

      {/* Receiver mode switcher */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <div className="text-xs text-gray-500 mb-2 font-medium">Learning depth</div>
        <ReceiverModeSwitcher
          value={receiverMode}
          onChange={(mode: ReceiverMode) => dispatch(setReceiverMode(mode))}
        />
      </div>

      {/* Input */}
      <section className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h2 className="font-semibold mb-3">Input</h2>
        <textarea
          rows={6}
          value={(currentRequest?.text as string) ?? ""}
          placeholder={
            entry.input_types.includes("documents")
              ? "Enter text here (for labelled docs use the JSON panel below)…"
              : "Paste your text here…"
          }
          className="w-full bg-gray-800 rounded-lg px-4 py-3 text-sm font-mono resize-y border border-gray-700 focus:border-indigo-500 outline-none"
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
          className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800 rounded-lg font-semibold transition text-sm"
        >
          {isRunning ? "Running…" : "Run Simulator"}
        </button>

        <button
          onClick={handleLoadDemo}
          disabled={isRunning}
          className="px-5 py-2.5 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 border border-gray-600 rounded-lg font-semibold transition text-sm"
        >
          Load Demo
        </button>

        {currentRun && (
          <button onClick={() => dispatch(clearRun())} className="text-sm text-gray-500 hover:text-gray-300">
            Clear
          </button>
        )}

        {currentRun && (
          <span className="text-xs text-gray-500 ml-auto">
            {currentRun.metrics.runtime_ms.toFixed(1)} ms · {currentRun.algorithm_version}
          </span>
        )}
      </div>

      {/* Error */}
      {runStatus === "error" && runError && (
        <div className="bg-red-950 border border-red-800 rounded-xl px-5 py-4 text-red-300 text-sm">
          {runError}
        </div>
      )}

      {/* Warnings */}
      {currentRun?.warnings?.length ? <WarningBanner warnings={currentRun.warnings} /> : null}

      {/* Results */}
      {currentRun && (
        <>
          {/* Layered explanation based on receiver mode */}
          {(currentRun.receiver_mode_explanations?.length > 0 || currentRun.research_context) && (
            <ExplanationPanel
              mode={receiverMode}
              explanations={currentRun.receiver_mode_explanations ?? []}
              researchContext={currentRun.research_context}
              teachingNotes={currentRun.teaching_notes}
            />
          )}

          {/* Step-by-step pipeline timeline */}
          {currentRun.step_explanations?.length > 0 && (
            <StepTimeline steps={currentRun.step_explanations} />
          )}

          {/* Math / formula cards */}
          {currentRun.formula_cards?.length > 0 && (
            <FormulaPanel cards={currentRun.formula_cards} />
          )}

          {/* Visualizations */}
          <VisualizationPanel specs={currentRun.visualization_specs} />

          {/* Trace */}
          <TraceViewer trace={currentRun.trace} result={currentRun.result} level={traceLevel} />

          {/* Research references */}
          {currentRun.references?.length > 0 && (
            <ReferencesPanel references={currentRun.references} />
          )}
        </>
      )}
    </div>
  );
}
