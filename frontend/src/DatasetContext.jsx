import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { api } from "./api";

const DatasetContext = createContext(null);
const STORAGE_KEY = "selected-dataset";

function stored() {
  try {
    return window.localStorage.getItem(STORAGE_KEY) || "";
  } catch {
    return "";
  }
}

// The dataset chosen in the header applies to the dashboard and the patent
// list. "" means all datasets.
export function DatasetProvider({ children }) {
  const [datasets, setDatasets] = useState([]);
  const [loaded, setLoaded] = useState(false);
  const [selected, setSelected] = useState(stored);
  const [readOnly, setReadOnly] = useState(false);

  useEffect(() => {
    api
      .config()
      .then((config) => setReadOnly(Boolean(config.read_only)))
      .catch(() => setReadOnly(false));
  }, []);

  const reload = useCallback(
    () =>
      api
        .datasets()
        .then(setDatasets)
        .catch(() => setDatasets([]))
        .finally(() => setLoaded(true)),
    []
  );

  useEffect(() => {
    reload();
  }, [reload]);

  // Forget a selection whose dataset was deleted.
  useEffect(() => {
    if (selected && datasets.length && !datasets.some((dataset) => String(dataset.id) === selected)) {
      setSelected("");
    }
  }, [datasets, selected]);

  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEY, selected);
    } catch {
      // storage may be unavailable (private mode); the selection just won't persist
    }
  }, [selected]);

  const value = useMemo(
    () => ({ datasets, loaded, readOnly, selected, setSelected, reload }),
    [datasets, loaded, readOnly, selected, reload]
  );
  return <DatasetContext.Provider value={value}>{children}</DatasetContext.Provider>;
}

export function useDatasets() {
  return useContext(DatasetContext);
}
