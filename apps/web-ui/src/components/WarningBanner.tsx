import type { WarningEntry } from "../types/api";

export default function WarningBanner({ warnings }: { warnings: WarningEntry[] }) {
  if (!warnings?.length) return null;
  return (
    <div className="bg-amber-950 border border-amber-800 rounded-xl px-5 py-4 space-y-2">
      {warnings.map((w, i) => (
        <div key={i} className="text-amber-300 text-sm">
          <span className="font-semibold">[{w.code}]</span> {w.message}
          {w.suggestion && <span className="text-amber-400 ml-2">→ {w.suggestion}</span>}
        </div>
      ))}
    </div>
  );
}
