import { lazy, Suspense, useEffect, useState } from "react";
import { BrowserRouter, Link, NavLink, Route, Routes, useLocation } from "react-router-dom";
import { Provider } from "react-redux";
import { store } from "./store/store";
import { useAppDispatch, useAppSelector } from "./store/hooks";
import { loadCatalog } from "./store/simulationSlice";
import { isOfflineMode, isStaticMode, onOfflineModeChange } from "./api/client";
import ErrorBoundary from "./components/ErrorBoundary";
import PageLoader from "./components/PageLoader";
import Toaster from "./components/Toaster";

const AlgorithmCatalog = lazy(() => import("./pages/AlgorithmCatalog"));
const SimulatorPage = lazy(() => import("./pages/SimulatorPage"));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage"));

function StatusDot({ status, offline }: { status: "idle" | "loading" | "ready" | "error"; offline: boolean }) {
  const map = {
    idle:    { color: "bg-gray-500",    pulse: false, label: "Idle" },
    loading: { color: "bg-amber-400",   pulse: true,  label: "Connecting…" },
    ready:   { color: "bg-emerald-400", pulse: false, label: "API online" },
    error:   { color: "bg-rose-500",    pulse: false, label: "API offline" },
  } as const;
  const { color, pulse, label: baseLabel } = map[status];
  const label = offline ? (isStaticMode() ? "Static demo" : "Demo data") : baseLabel;
  const dotColor = offline ? "bg-amber-400" : color;
  return (
    <span
      className="hidden sm:inline-flex items-center gap-2 text-xs text-gray-400 px-2.5 py-1 rounded-full bg-gray-900/60 border border-gray-800"
      title={label}
    >
      <span className="relative flex h-2 w-2">
        {pulse && <span className={`absolute inline-flex h-full w-full rounded-full ${dotColor} opacity-60 animate-ping`} />}
        <span className={`relative inline-flex h-2 w-2 rounded-full ${dotColor}`} aria-hidden />
      </span>
      <span>{label}</span>
      <span className="sr-only">{label}</span>
    </span>
  );
}

function Brand() {
  return (
    <Link to="/" className="flex items-center gap-2.5 group focus-ring rounded-lg">
      <span
        aria-hidden
        className="relative inline-flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 via-fuchsia-500 to-sky-500 text-white font-extrabold text-sm shadow-glow"
      >
        N
      </span>
      <span className="leading-tight">
        <span className="block text-base font-bold gradient-text">NLP Simulator</span>
        <span className="block text-[10px] uppercase tracking-[0.18em] text-gray-500">
          Top-10 Algorithms · Interactive
        </span>
      </span>
    </Link>
  );
}

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  `text-sm transition focus-ring rounded ${
    isActive ? "text-gray-50 font-medium" : "text-gray-400 hover:text-gray-50"
  }`;

function ThemeToggle() {
  const [isLight, setIsLight] = useState(
    () => document.documentElement.classList.contains("light")
  );

  function toggle() {
    const next = !isLight;
    setIsLight(next);
    document.documentElement.classList.toggle("light", next);
    document.documentElement.classList.toggle("dark", !next);
    try {
      localStorage.setItem("nlp-theme", next ? "light" : "dark");
    } catch {
      // storage unavailable (private mode) — theme just won't persist
    }
  }

  return (
    <button
      onClick={toggle}
      aria-label={isLight ? "Switch to dark mode" : "Switch to light mode"}
      aria-pressed={isLight}
      title={isLight ? "Switch to dark mode" : "Switch to light mode"}
      className="inline-flex h-8 w-8 items-center justify-center rounded-md border border-gray-800 bg-gray-900/60 text-sm text-gray-400 hover:text-white hover:border-gray-700 transition focus-ring"
    >
      {isLight ? (
        <svg aria-hidden width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>
      ) : (
        <svg aria-hidden width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <circle cx="12" cy="12" r="4" />
          <path d="M12 2v2m0 16v2M4.93 4.93l1.41 1.41m11.32 11.32 1.41 1.41M2 12h2m16 0h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
        </svg>
      )}
    </button>
  );
}

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo({ top: 0 });
  }, [pathname]);
  return null;
}

function AppShell() {
  const dispatch = useAppDispatch();
  const catalogStatus = useAppSelector((s) => s.simulation.catalogStatus);
  const catalogCount  = useAppSelector((s) => s.simulation.catalog.length);
  const [offline, setOffline] = useState(isOfflineMode);

  useEffect(() => onOfflineModeChange(setOffline), []);

  useEffect(() => {
    if (catalogStatus === "idle") dispatch(loadCatalog());
  }, [catalogStatus, dispatch]);

  return (
    <div className="min-h-screen text-gray-100 flex flex-col">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-lg focus:bg-indigo-600 focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-white"
      >
        Skip to content
      </a>

      <header className="sticky top-0 z-30 backdrop-blur bg-gray-950/75 border-b border-gray-800/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center gap-4 sm:gap-6">
          <Brand />
          <nav aria-label="Primary" className="flex items-center gap-5 ml-2">
            <NavLink to="/" end className={navLinkClass}>Catalog</NavLink>
            {!offline && (
              <a
                href="http://127.0.0.1:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="text-sm text-gray-400 hover:text-white transition focus-ring rounded"
              >
                API Docs
              </a>
            )}
          </nav>
          <div className="ml-auto flex items-center gap-3">
            {offline && (
              <span
                className="inline-flex items-center gap-1.5 text-xs font-medium text-amber-700 dark:text-amber-300 bg-amber-100 dark:bg-amber-500/10 border border-amber-300 dark:border-amber-500/40 px-2.5 py-1 rounded-full"
                title={
                  isStaticMode()
                    ? "Static build — every algorithm shows its pre-computed reference run"
                    : "Backend unreachable — browsing pre-computed demo results"
                }
              >
                <span aria-hidden>⚡</span>
                <span className="hidden sm:inline">
                  {isStaticMode() ? "Static demo" : "Offline demo"}
                </span>
              </span>
            )}
            {catalogStatus === "ready" && (
              <span className="hidden md:inline text-xs text-gray-500">
                {catalogCount} algorithm{catalogCount === 1 ? "" : "s"}
              </span>
            )}
            <StatusDot status={catalogStatus} offline={offline} />
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main id="main-content" tabIndex={-1} className="flex-1 px-4 sm:px-6 py-8 outline-none">
        <ErrorBoundary>
          <Suspense fallback={<PageLoader />}>
            <Routes>
              <Route path="/" element={<AlgorithmCatalog />} />
              <Route path="/simulate/:algorithmId" element={<SimulatorPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Suspense>
        </ErrorBoundary>
      </main>

      <footer className="border-t border-gray-800/70 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-5 text-xs text-gray-500 flex flex-wrap items-center justify-between gap-2">
          <span>© NLP Algorithm Simulator · Built for hands-on learning</span>
          <span className="hidden sm:inline">FastAPI · React · Vite · Tailwind</span>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <Provider store={store}>
      <BrowserRouter basename={import.meta.env.BASE_URL}>
        <ScrollToTop />
        <AppShell />
        <Toaster />
      </BrowserRouter>
    </Provider>
  );
}
