import { BrowserRouter, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import { DatasetProvider } from "./DatasetContext";
import Dashboard from "./pages/Dashboard";
import Datasets from "./pages/Datasets";
import NotFound from "./pages/NotFound";
import Patents from "./pages/Patents";

export default function App() {
  return (
    <BrowserRouter>
      <DatasetProvider>
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="patents" element={<Patents />} />
            <Route path="datasets" element={<Datasets />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </DatasetProvider>
    </BrowserRouter>
  );
}
