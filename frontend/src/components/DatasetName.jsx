import { useState } from "react";

import { api } from "../api";

// Dataset name with inline renaming: Enter saves, Escape cancels.
export default function DatasetName({ dataset, editable, onRenamed }) {
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(dataset.name);
  const [error, setError] = useState("");

  async function save() {
    const next = name.trim();
    if (!next || next === dataset.name) {
      setEditing(false);
      setName(dataset.name);
      return;
    }
    try {
      await api.renameDataset(dataset.id, next);
      setEditing(false);
      setError("");
      onRenamed();
    } catch (err) {
      setError(err.message);
    }
  }

  if (!editing) {
    return (
      <span className="dataset-name">
        <strong>{dataset.name}</strong>
        {editable && (
          <button type="button" className="link-button" onClick={() => setEditing(true)}>
            Rename
          </button>
        )}
      </span>
    );
  }

  return (
    <span className="dataset-name">
      <input
        className="input"
        aria-label="New dataset name"
        value={name}
        autoFocus
        onChange={(event) => setName(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter") save();
          if (event.key === "Escape") {
            setEditing(false);
            setName(dataset.name);
          }
        }}
      />
      <button type="button" className="button" onClick={save}>
        Save
      </button>
      {error && <span className="error small">{error}</span>}
    </span>
  );
}
