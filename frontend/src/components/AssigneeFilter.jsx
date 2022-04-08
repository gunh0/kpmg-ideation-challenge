import { useEffect, useState } from "react";

import { api } from "../api";
import useDebounce from "../hooks/useDebounce";

// Free-text input with suggestions from /api/assignees/. The filter matches the
// whole name, so the value is only applied once it is one of the suggestions
// or the user presses Enter.
export default function AssigneeFilter({ value, dataset, onChange }) {
  const [text, setText] = useState(value);
  const [suggestions, setSuggestions] = useState([]);
  const query = useDebounce(text.trim(), 250);

  useEffect(() => setText(value), [value]);

  useEffect(() => {
    let current = true;
    api
      .assignees({ search: query, dataset })
      .then((rows) => current && setSuggestions(rows))
      .catch(() => current && setSuggestions([]));
    return () => {
      current = false;
    };
  }, [query, dataset]);

  function update(next) {
    setText(next);
    if (next === "" || suggestions.some((row) => row.name === next)) onChange(next);
  }

  return (
    <>
      <input
        className="input assignee"
        list="assignee-suggestions"
        placeholder="Assignee"
        aria-label="Assignee"
        value={text}
        onChange={(event) => update(event.target.value)}
        onKeyDown={(event) => event.key === "Enter" && onChange(text.trim())}
      />
      <datalist id="assignee-suggestions">
        {suggestions.map((row) => (
          <option key={row.name} value={row.name}>
            {row.count} patents
          </option>
        ))}
      </datalist>
    </>
  );
}
