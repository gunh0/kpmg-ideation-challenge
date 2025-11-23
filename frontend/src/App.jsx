import { lazy, Suspense } from "react";
import { BrowserRouter, Route, Routes } from "react-router";

import Layout from "./components/Layout";
import { DatasetProvider } from "./DatasetContext";

// Each page is its own chunk; the first visit only loads the page it opens.
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Datasets = lazy(() => import("./pages/Datasets"));
const NotFound = lazy(() => import("./pages/NotFound"));
const Patents = lazy(() => import("./pages/Patents"));

function page(Component) {
  return (
    <Suspense fallback={<p className="muted">Loading…</p>}>
      <Component />
    </Suspense>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <DatasetProvider>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={page(Dashboard)} />
            <Route path="patents" element={page(Patents)} />
            <Route path="datasets" element={page(Datasets)} />
            <Route path="*" element={page(NotFound)} />
          </Route>
        </Routes>
      </DatasetProvider>
    </BrowserRouter>
  );
}
