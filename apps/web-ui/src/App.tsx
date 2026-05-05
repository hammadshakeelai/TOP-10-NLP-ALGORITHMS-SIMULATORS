import { useEffect } from "react";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import { Provider } from "react-redux";
import { store } from "./store/store";
import { useAppDispatch, useAppSelector } from "./store/hooks";
import { loadCatalog } from "./store/simulationSlice";
import AlgorithmCatalog from "./pages/AlgorithmCatalog";
import SimulatorPage from "./pages/SimulatorPage";

function StatusDot({ status }: { status: "idle" | "loading" | "ready" | "error" }) {
  const map = {
    idle:    { color: "bg-gray-500",    pulse: false, label: "Idle" },
    loading: { color: "bg-amber-400",   pulse: true,  label: "Connecting…" },
    ready:   { color: "bg-emerald-400", pulse: false, label: "API online" },
    error:   { color: "bg-rose-500",    pulse: false, label: "API offline" },
  } as const;
  const { color, pulse, label } = map[status];
  return (
    <span
      className="hidden sm:inline-flex items-center gap-2 text-xs text-gray-400 px-2.5 py-1 rounded-full bg-gray-900/60 border border-gray-800"
      title={label}
    >
      <span className="relative flex h-2 w-2">
        {pulse && <span className={`absolute inline-flex h-full w-full rounded-full ${color} opacity-60 animate-ping`} />}
        <span className={`relative inline-flex h-2 w-2 rounded-full ${color}`} />
      </span>
      <span>{label}</span>
    </span>
  );
}

function Brand() {
  return (
    <NavLink to="/" className="flex items-center gap-2.5 group">
      <span className="relative inline-flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 via-fuchsia-500 to-sky-500 text-white font-extrabold text-sm shadow-glow">
        N
      </span>
      <span className="leading-tight">
        <span className="block text-base font-bold gradient-text">NLP Simulator</span>
        <span className="block text-[10px] uppercase tracking-[0.18em] text-gray-500">
          Top-10 Algorithms · Interactive
        </span>
      </span>
    </NavLink>
  );
}

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `text-sm transition focus-ring rounded ${
    isActive ? "text-white font-medium" : "text-gray-400 hover:text-white"
  }`;

function AppShell() {
  const dispatch = useAppDispatch();
  const catalogStatus = useAppSelector((s) => s.simulation.catalogStatus);
  const catalogCount  = useAppSelector((s) => s.simulation.catalog.length);

  useEffect(() => {
    if (catalogStatus === "idle") dispatch(loadCatalog());
  }, [catalogStatus, dispatch]);

  return (
    <BrowserRouter>
      <div className="min-h-screen text-gray-100 flex flex-col">
        <header className="sticky top-0 z-30 backdrop-blur bg-gray-950/75 border-b border-gray-800/80">
          <div className="max-w-7xl mx-auto px-6 py-3 flex items-center gap-6">
            <Brand />
            <nav className="flex items-center gap-5 ml-2">
              <NavLink to="/" end className={navLinkClass}>Catalog</NavLink>
              <a
                href="http://127.0.0.1:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="text-sm text-gray-400 hover:text-white transition"
              >
                API Docs
              </a>
            </nav>
            <div className="ml-auto flex items-center gap-3">
              {catalogStatus === "ready" && (
                <span className="hidden md:inline text-xs text-gray-500">
                  {catalogCount} algorithm{catalogCount === 1 ? "" : "s"}
                </span>
              )}
              <StatusDot status={catalogStatus} />
              <a
                href="https://github.com/hammadai/ai-ml"
                target="_blank"
                rel="noreferrer"
                className="text-xs text-gray-400 hover:text-white px-2.5 py-1 rounded-md border border-gray-800 hover:border-gray-700 transition"
                aria-label="GitHub"
              >
                GitHub
              </a>
            </div>
          </div>
        </header>

        <main className="flex-1 px-6 py-8">
          <Routes>
            <Route path="/" element={<AlgorithmCatalog />} />
            <Route path="/simulate/:algorithmId" element={<SimulatorPage />} />
          </Routes>
        </main>

        <footer className="border-t border-gray-800/70 mt-12">
          <div className="max-w-7xl mx-auto px-6 py-5 text-xs text-gray-500 flex items-center justify-between">
            <span>© NLP Algorithm Simulator · Built for hands-on learning</span>
            <span className="hidden sm:inline">FastAPI · React · Vite · Tailwind</span>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}

export default function App() {
  return (
    <Provider store={store}>
      <AppShell />
    </Provider>
  );
}
