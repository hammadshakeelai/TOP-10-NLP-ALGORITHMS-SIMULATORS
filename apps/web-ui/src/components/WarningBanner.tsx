import type { WarningEntry } from "../types/api";

export default function WarningBanner({ warnings }: { warnings: WarningEntry[] }) {
  if (!warnings?.length) return null;
  return (
    <div
      role="status"
      aria-label="Run warnings"
      className="bg-amber-100 border border-amber-300/70 dark:bg-amber-950 dark:border-amber-800 rounded-xl px-5 py-4 space-y-2"
    >
      <div className="text-xs font-semibold uppercase tracking-wide text-amber-700 dark:text-amber-400 mb-1">
        Warnings ({warnings.length})
      </div>
      {warnings.map((w, i) => (
        <div key={i} className="text-amber-800 dark:text-amber-300 text-sm">
          <span className="font-semibold">[{w.code}]</span> {w.message}
          {w.suggestion && <span className="text-amber-700 dark:text-amber-400 ml-2">→ {w.suggestion}</span>}
        </div>
      ))}
    </div>
  );
}
