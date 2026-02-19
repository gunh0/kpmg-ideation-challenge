import { lazy, Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router";

import Layout from "./components/Layout";
import { DatasetProvider } from "./DatasetContext";

// Each page is its own chunk; the first visit only loads the page it opens.
const Dashboard = lazy(() => import("./pages/Dashboard"));
const NotFound = lazy(() => import("./pages/NotFound"));
const Patents = lazy(() => import("./pages/Patents"));
const Profile = lazy(() => import("./pages/Profile"));
const Topics = lazy(() => import("./pages/Topics"));

function page(element) {
  return <Suspense fallback={<p className="muted">Loading…</p>}>{element}</Suspense>;
}

export default function App() {
  return (
    <BrowserRouter>
      <DatasetProvider>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={page(<Dashboard />)} />
            <Route path="patents" element={page(<Patents />)} />
            <Route path="topics" element={page(<Topics />)} />
            <Route path="datasets" element={<Navigate to="/topics" replace />} />
            <Route path="assignees/:name" element={page(<Profile kind="assignee" />)} />
            <Route path="inventors/:name" element={page(<Profile kind="inventor" />)} />
            <Route path="*" element={page(<NotFound />)} />
          </Route>
        </Routes>
      </DatasetProvider>
    </BrowserRouter>
  );
}
