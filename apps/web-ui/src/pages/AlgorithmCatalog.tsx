import { useNavigate } from "react-router-dom";
import { useAppSelector, useAppDispatch } from "../store/hooks";
import { selectAlgorithm } from "../store/simulationSlice";
import type { AlgorithmEntry } from "../types/api";

const FAMILY_COLORS: Record<string, string> = {
  preprocessing:  "bg-blue-900 text-blue-300",
  vectorization:  "bg-purple-900 text-purple-300",
  classification: "bg-green-900 text-green-300",
  extraction:     "bg-amber-900 text-amber-300",
  sequence:       "bg-rose-900 text-rose-300",
  transformer:    "bg-indigo-900 text-indigo-300",
};

export default function AlgorithmCatalog() {
  const catalog = useAppSelector((s) => s.simulation.catalog);
  const status   = useAppSelector((s) => s.simulation.catalogStatus);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  if (status === "loading") return <div className="text-gray-400 text-center mt-20">Loading catalog…</div>;
  if (status === "error")   return <div className="text-red-400 text-center mt-20">Failed to load catalog. Is the API running?</div>;

  const families = [...new Set(catalog.map((a) => a.family))];

  function launch(entry: AlgorithmEntry) {
    dispatch(selectAlgorithm(entry.id));
    navigate(`/simulate/${entry.id}`);
  }

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">Algorithm Catalog</h1>
      {families.map((family) => (
        <section key={family} className="mb-10">
          <h2 className="text-sm font-semibold uppercase tracking-widest text-gray-500 mb-4">{family}</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {catalog.filter((a) => a.family === family).map((entry) => (
              <button
                key={entry.id}
                onClick={() => launch(entry)}
                className="text-left p-5 rounded-xl border border-gray-800 hover:border-indigo-500 bg-gray-900 hover:bg-gray-800 transition group"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-white group-hover:text-indigo-400">{entry.name}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${FAMILY_COLORS[family] ?? "bg-gray-800 text-gray-300"}`}>
                    {entry.family}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mb-3 leading-snug">{entry.description}</p>
                <div className="flex flex-wrap gap-1">
                  {entry.use_cases.map((uc) => (
                    <span key={uc} className="text-xs bg-gray-800 text-gray-300 px-2 py-0.5 rounded-full">{uc}</span>
                  ))}
                </div>
                <div className="mt-3 text-xs text-gray-600">Complexity: {entry.complexity}</div>
              </button>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
