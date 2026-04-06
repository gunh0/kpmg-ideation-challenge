import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { api } from "./api";

const TopicContext = createContext(null);
const STORAGE_KEY = "selected-topics";
const POLL_MS = 5000;

export const isCollecting = (topic) => topic.status === "queued" || topic.status === "collecting";

// Ids of the selected topics, as strings; [] means all topics.
function stored() {
  try {
    const value = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || "[]");
    if (Array.isArray(value)) return value.map(String);
    return [];
  } catch {
    return [];
  }
}

// The topics chosen in the header apply to the dashboard, the patent list and
// the profiles. topicsParam is the selection as the API takes it ("1,3").
export function TopicProvider({ children }) {
  const [topics, setTopics] = useState([]);
  const [loaded, setLoaded] = useState(false);
  const [choice, setSelected] = useState(stored);

  const reload = useCallback(
    () =>
      api
        .topics()
        .then(setTopics)
        .catch(() => setTopics([]))
        .finally(() => setLoaded(true)),
    []
  );

  useEffect(() => {
    reload();
  }, [reload]);

  // While a topic is being collected, its counts and progress keep changing.
  const busy = topics.some(isCollecting);
  useEffect(() => {
    if (!busy) return undefined;
    const timer = window.setTimeout(reload, POLL_MS);
    return () => window.clearTimeout(timer);
  }, [busy, topics, reload]);

  // Topics deleted since they were selected drop out of the selection.
  const selected = useMemo(
    () => (topics.length ? choice.filter((id) => topics.some((topic) => String(topic.id) === id)) : choice),
    [choice, topics]
  );

  useEffect(() => {
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(selected));
    } catch {
      // storage may be unavailable (private mode); the selection just won't persist
    }
  }, [selected]);

  const value = useMemo(
    () => ({ topics, loaded, selected, setSelected, reload, topicsParam: selected.join(",") }),
    [topics, loaded, selected, reload]
  );
  return <TopicContext value={value}>{children}</TopicContext>;
}

export function useTopics() {
  return useContext(TopicContext);
}
