import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAppSelector, useAppDispatch } from "../store/hooks";
import { selectAlgorithm, loadCatalog } from "../store/simulationSlice";
import type { AlgorithmEntry } from "../types/api";
import { isStaticMode } from "../api/client";

const FAMILY_COLORS: Record<string, string> = {
  preprocessing:  "bg-blue-100 text-blue-800 ring-blue-300 dark:bg-blue-900/60 dark:text-blue-200 dark:ring-blue-700/40",
  vectorization:  "bg-purple-100 text-purple-800 ring-purple-300 dark:bg-purple-900/60 dark:text-purple-200 dark:ring-purple-700/40",
  classification: "bg-emerald-100 text-emerald-800 ring-emerald-300 dark:bg-emerald-900/60 dark:text-emerald-200 dark:ring-emerald-700/40",
  extraction:     "bg-amber-100 text-amber-800 ring-amber-300 dark:bg-amber-900/60 dark:text-amber-200 dark:ring-amber-700/40",
  sequence:       "bg-rose-100 text-rose-800 ring-rose-300 dark:bg-rose-900/60 dark:text-rose-200 dark:ring-rose-700/40",
  transformer:    "bg-indigo-100 text-indigo-800 ring-indigo-300 dark:bg-indigo-900/60 dark:text-indigo-200 dark:ring-indigo-700/40",
};

function familyChip(family: string) {
  return (
    FAMILY_COLORS[family] ??
    "bg-gray-200 text-gray-800 ring-gray-400 dark:bg-gray-800 dark:text-gray-300 dark:ring-gray-700/40"
  );
}

const FAMILY_ORDER = [
  "preprocessing",
  "vectorization",
  "classification",
  "extraction",
  "sequence",
  "transformer",
];

function CatalogSkeleton() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="panel-soft p-5 h-40 animate-pulse">
          <div className="h-4 w-2/3 bg-gray-800 rounded mb-3" />
          <div className="h-3 w-full bg-gray-800/70 rounded mb-2" />
          <div className="h-3 w-5/6 bg-gray-800/70 rounded mb-4" />
          <div className="flex gap-2">
            <div className="h-5 w-14 bg-gray-800 rounded-full" />
            <div className="h-5 w-20 bg-gray-800 rounded-full" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function AlgorithmCatalog() {
  const catalog = useAppSelector((s) => s.simulation.catalog);
  const status   = useAppSelector((s) => s.simulation.catalogStatus);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const searchRef = useRef<HTMLInputElement>(null);

  const [query, setQuery] = useState("");
  const [activeFamily, setActiveFamily] = useState<string | "all">("all");

  useEffect(() => {
    document.title = "NLP Algorithm Simulator";
  }, []);

  // Press "/" anywhere on the catalog to jump to search.
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey) return;
      const target = e.target as HTMLElement | null;
      if (target && /^(input|textarea|select)$/i.test(target.tagName)) return;
      e.preventDefault();
      searchRef.current?.focus();
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const families = useMemo(() => {
    const present = new Set(catalog.map((a) => a.family));
    return FAMILY_ORDER.filter((f) => present.has(f)).concat(
      [...present].filter((f) => !FAMILY_ORDER.includes(f))
    );
  }, [catalog]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return catalog.filter((a) => {
      if (activeFamily !== "all" && a.family !== activeFamily) return false;
      if (!q) return true;
      const haystack = [
        a.name,
        a.description,
        a.family,
        ...(a.use_cases ?? []),
      ]
        .join(" ")
        .toLowerCase();
      return haystack.includes(q);
    });
  }, [catalog, query, activeFamily]);

  function launch(entry: AlgorithmEntry) {
    dispatch(selectAlgorithm(entry.id));
    navigate(`/simulate/${entry.id}`);
  }

  const grouped = useMemo(() => {
    const map = new Map<string, AlgorithmEntry[]>();
    for (const entry of filtered) {
      if (!map.has(entry.family)) map.set(entry.family, []);
      map.get(entry.family)!.push(entry);
    }
    return families
      .map((f) => [f, map.get(f) ?? []] as const)
      .filter(([, items]) => items.length > 0);
  }, [filtered, families]);

  return (
    <div className="max-w-7xl mx-auto animate-fade-in">
      {/* Hero */}
      <section className="mb-10 text-center md:text-left">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-700 dark:text-indigo-300 text-xs font-medium mb-4">
          <span className="h-1.5 w-1.5 rounded-full bg-indigo-400 animate-pulse" aria-hidden />
          Interactive learning platform
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight mb-3">
          The Top NLP Algorithms,{" "}
          <span className="gradient-text">visualised step-by-step.</span>
        </h1>
        <p className="text-gray-400 max-w-2xl text-sm sm:text-base leading-relaxed mx-auto md:mx-0">
          Pick an algorithm, load a demo, and watch it run — with formulas, pipeline
          steps, references, and explanations tuned for every learner from beginner to
          researcher.
        </p>

        {/* Stat ribbon */}
        {status === "ready" && (
          <div className="mt-6 flex flex-wrap gap-3 justify-center md:justify-start">
            <Stat label="Algorithms" value={catalog.length} />
            <Stat label="Families" value={families.length} />
            <Stat label="Receiver modes" value={5} />
            <Stat label="Trace levels" value={3} />
          </div>
        )}
      </section>

      {/* Filters */}
      <div className="panel p-4 mb-8 flex flex-col gap-4 md:flex-row md:items-center md:gap-4">
        <div className="relative flex-1">
          <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm" aria-hidden>
            ⌕
          </span>
          <input
            ref={searchRef}
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search algorithms…  (press /)"
            className="w-full bg-gray-950/60 border border-gray-800 rounded-lg pl-9 pr-3 py-2 text-sm placeholder:text-gray-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 outline-none transition"
            aria-label="Search algorithms"
          />
        </div>

        <div className="flex flex-wrap gap-2">
          <FamilyPill label="All" active={activeFamily === "all"} onClick={() => setActiveFamily("all")} />
          {families.map((f) => (
            <FamilyPill
              key={f}
              label={f}
              colorClass={familyChip(f)}
              active={activeFamily === f}
              onClick={() => setActiveFamily(f)}
            />
          ))}
        </div>
      </div>

      {/* Body */}
      {status === "loading" && <CatalogSkeleton />}

      {status === "error" && (
        <div className="panel p-8 text-center">
          <div className="text-rose-700 dark:text-rose-300 font-medium mb-1">Failed to load catalog.</div>
          <p className="text-sm text-gray-400 mb-4">
            {isStaticMode() ? (
              <>Bundled demo data could not be read. Reloading the page usually clears this.</>
            ) : (
              <>
                Make sure the API is running at{" "}
                <code className="text-gray-600 dark:text-gray-300">127.0.0.1:8000</code>.
              </>
            )}
          </p>
          <button
            onClick={() => dispatch(loadCatalog())}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-semibold transition focus-ring"
          >
            Retry
          </button>
        </div>
      )}

      {status === "ready" && grouped.length === 0 && (
        <div className="panel p-10 text-center">
          <div className="text-3xl mb-2">∅</div>
          <div className="font-medium text-gray-200 mb-1">No algorithms match your filters.</div>
          <p className="text-sm text-gray-500">Try clearing the search or picking a different family.</p>
        </div>
      )}

      {status === "ready" &&
        grouped.map(([family, items], i) => (
          <section key={family} className="mb-10 animate-slide-up" style={{ animationDelay: `${i * 40}ms` }}>
            <div className="flex items-baseline justify-between mb-4">
              <h2 className="text-sm font-semibold uppercase tracking-widest text-gray-400">
                {family}
              </h2>
              <span className="text-xs text-gray-600">{items.length} item{items.length === 1 ? "" : "s"}</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {items.map((entry) => (
                <CatalogCard key={entry.id} entry={entry} onClick={() => launch(entry)} />
              ))}
            </div>
          </section>
        ))}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-baseline gap-2 px-3 py-1.5 rounded-lg bg-gray-900/60 border border-gray-800">
      <span className="text-xl font-bold gradient-text">{value}</span>
      <span className="text-xs text-gray-400">{label}</span>
    </div>
  );
}

function FamilyPill({
  label,
  colorClass,
  active,
  onClick,
}: {
  label: string;
  colorClass?: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`text-xs font-medium px-3 py-1 rounded-full ring-1 transition focus-ring capitalize ${
        active
          ? `${
              colorClass ?? "bg-indigo-100 text-indigo-800 ring-indigo-300 dark:bg-indigo-500/20 dark:text-indigo-200 dark:ring-indigo-400/50"
            } ring-2`
          : "bg-gray-900/60 text-gray-400 ring-gray-800 hover:text-gray-100 hover:ring-gray-600"
      }`}
    >
      {label}
    </button>
  );
}

function CatalogCard({ entry, onClick }: { entry: AlgorithmEntry; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="text-left p-5 rounded-xl border border-gray-800 hover:border-indigo-500/70 bg-gray-900/60 hover:bg-gray-900 transition group focus-ring relative overflow-hidden"
    >
      <div
        className="absolute inset-x-0 -top-px h-px bg-gradient-to-r from-transparent via-indigo-500/60 to-transparent opacity-0 group-hover:opacity-100 transition"
        aria-hidden
      />
      <div className="flex items-start justify-between gap-3 mb-2">
        <span className="font-semibold text-gray-50 group-hover:text-indigo-700 dark:group-hover:text-indigo-300 transition">
          {entry.name}
        </span>
        <span className={`chip ring-1 ${familyChip(entry.family)}`}>{entry.family}</span>
      </div>
      <p className="text-sm text-gray-400 mb-3 leading-snug line-clamp-3">{entry.description}</p>
      <div className="flex flex-wrap gap-1 mb-3">
        {entry.use_cases.slice(0, 4).map((uc) => (
          <span key={uc} className="text-[11px] bg-gray-800/80 text-gray-300 px-2 py-0.5 rounded-full">
            {uc}
          </span>
        ))}
        {entry.use_cases.length > 4 && (
          <span className="text-[11px] text-gray-500 px-1">+{entry.use_cases.length - 4}</span>
        )}
      </div>
      <div className="flex items-center justify-between text-xs">
        <span className="text-gray-500">
          Complexity: <span className="text-gray-300">{entry.complexity}</span>
        </span>
        <span className="text-gray-600 group-hover:text-indigo-700 dark:group-hover:text-indigo-300 transition">Open →</span>
      </div>
    </button>
  );
}
