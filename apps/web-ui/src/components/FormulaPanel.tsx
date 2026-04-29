import type { FormulaCard } from "../types/api";

interface Props {
  cards: FormulaCard[];
}

export default function FormulaPanel({ cards }: Props) {
  if (!cards?.length) return null;

  return (
    <section className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <h2 className="font-semibold text-lg mb-4">Formulas</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {cards.map((card, i) => (
          <div key={i} className="bg-gray-800 rounded-lg p-4 space-y-3">
            <div className="font-semibold text-sm text-indigo-300">{card.title}</div>

            <div className="font-mono text-xs bg-gray-900 rounded px-3 py-2 text-violet-300 overflow-x-auto">
              {card.formula}
            </div>

            <p className="text-xs text-gray-300">{card.explanation}</p>

            {Object.keys(card.variables ?? {}).length > 0 && (
              <div className="space-y-1">
                <div className="text-xs text-gray-500 font-medium">Variables</div>
                {Object.entries(card.variables).map(([k, v]) => (
                  <div key={k} className="flex gap-2 text-xs">
                    <code className="text-amber-300 font-mono whitespace-nowrap">{k}</code>
                    <span className="text-gray-400">=</span>
                    <span className="text-gray-300">{v}</span>
                  </div>
                ))}
              </div>
            )}

            {card.example && (
              <div className="text-xs text-emerald-300 bg-gray-900/60 rounded px-3 py-2 font-mono">
                {card.example}
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
