import { useRef, useState } from "react";

import { api } from "../api";

export default function UploadDataset({ onUploaded }) {
  const input = useRef(null);
  const [file, setFile] = useState(null);
  const [name, setName] = useState("");
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  function choose(files) {
    setError("");
    setFile(files && files[0] ? files[0] : null);
  }

  async function submit(event) {
    event.preventDefault();
    if (!file) return;
    setBusy(true);
    setError("");
    try {
      const result = await api.uploadDataset(file, name.trim());
      setFile(null);
      setName("");
      if (input.current) input.current.value = "";
      onUploaded(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="upload" onSubmit={submit}>
      <label
        className={`dropzone${dragging ? " dragging" : ""}`}
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDragging(false);
          choose(event.dataTransfer.files);
        }}
      >
        <input
          ref={input}
          type="file"
          accept=".csv,text/csv"
          className="visually-hidden"
          onChange={(event) => choose(event.target.files)}
        />
        {file ? (
          <strong>{file.name}</strong>
        ) : (
          <>
            <strong>Drop a Google Patents CSV here</strong>
            <span className="muted">or click to choose a file</span>
          </>
        )}
      </label>
      <div className="upload-actions">
        <input
          className="input"
          placeholder="Dataset name (default: the search query)"
          aria-label="Dataset name"
          value={name}
          onChange={(event) => setName(event.target.value)}
        />
        <button type="submit" className="button button-primary" disabled={!file || busy}>
          {busy ? "Importing…" : "Import"}
        </button>
      </div>
      {error && <p className="error">{error}</p>}
    </form>
  );
}
