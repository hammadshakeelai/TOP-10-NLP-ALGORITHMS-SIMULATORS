import { useEffect } from "react";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import { Provider } from "react-redux";
import { store } from "./store/store";
import { useAppDispatch, useAppSelector } from "./store/hooks";
import { loadCatalog } from "./store/simulationSlice";
import AlgorithmCatalog from "./pages/AlgorithmCatalog";
import SimulatorPage from "./pages/SimulatorPage";

function AppShell() {
  const dispatch = useAppDispatch();
  const catalogStatus = useAppSelector((s) => s.simulation.catalogStatus);

  useEffect(() => {
    if (catalogStatus === "idle") dispatch(loadCatalog());
  }, [catalogStatus, dispatch]);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col">
        <header className="border-b border-gray-800 px-6 py-4 flex items-center gap-6">
          <span className="text-lg font-bold text-indigo-400 tracking-tight">NLP Simulator</span>
          <NavLink to="/" className={({ isActive }) => isActive ? "text-white font-medium" : "text-gray-400 hover:text-white"}>
            Catalog
          </NavLink>
        </header>
        <main className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<AlgorithmCatalog />} />
            <Route path="/simulate/:algorithmId" element={<SimulatorPage />} />
          </Routes>
        </main>
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
