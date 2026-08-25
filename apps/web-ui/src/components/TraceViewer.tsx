import { useState } from "react";
import type { TraceLevel } from "../types/api";
import CopyButton from "./CopyButton";

interface Props {
  trace: unknown;
  result: Record<string, unknown>;
  level: TraceLevel;
}

export default function TraceViewer({ trace, result, level }: Props) {
  const [expanded, setExpanded] = useState(false);
  if (level === "none" || !trace) return null;

  return (
    <section className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-3 gap-3">
        <h2 className="font-semibold">Trace</h2>
        <div className="flex items-center gap-3">
          <CopyButton value={() => JSON.stringify(trace, null, 2)} label="Copy JSON" />
          <button
            onClick={() => setExpanded((e) => !e)}
            aria-expanded={expanded}
            className="text-xs text-gray-500 hover:text-gray-300 focus-ring rounded"
          >
            {expanded ? "Collapse" : "Expand"}
          </button>
        </div>
      </div>
      {expanded ? (
        <pre
          tabIndex={0}
          aria-label="Full trace output"
          className="text-xs font-mono text-gray-600 dark:text-gray-300 overflow-auto max-h-96 rounded-lg bg-gray-950/60 dark:bg-transparent p-2 dark:p-0"
        >
          {JSON.stringify(trace, null, 2)}
        </pre>
      ) : (
        <SummaryView trace={trace} result={result} />
      )}
    </section>
  );
}

function SummaryView({ trace, result }: { trace: unknown; result: Record<string, unknown> }) {
  const obj = typeof trace === "object" && trace !== null ? (trace as Record<string, unknown>) : {};
  const topKeys = Object.keys(obj).slice(0, 8);
  return (
    <dl className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
      {topKeys.map((k) => {
        const v = obj[k];
        const display = typeof v === "object" ? `[${Array.isArray(v) ? v.length + " items" : "object"}]` : String(v);
        return (
          <div key={k} className="bg-gray-800 rounded-lg p-3">
            <dt className="text-gray-500 text-xs mb-1">{k}</dt>
            <dd className="font-mono text-gray-700 dark:text-gray-200 truncate" title={display}>{display}</dd>
          </div>
        );
      })}
    </dl>
  );
}
