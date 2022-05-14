import { useState } from "react";

import { api } from "../api";
import { useDatasets } from "../DatasetContext";
import DatasetName from "../components/DatasetName";
import UploadDataset from "../components/UploadDataset";
import ErrorMessage from "../components/ErrorMessage";
import useApi from "../hooks/useApi";

async function remove(dataset, onDone) {
  const ok = window.confirm(`Delete “${dataset.name}” and its ${dataset.patent_count} patents?`);
  if (!ok) return;
  await api.deleteDataset(dataset.id);
  onDone();
}

function formatDateTime(value) {
  return new Date(value).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

export default function Datasets() {
  const [version, setVersion] = useState(0);
  const { reload, readOnly } = useDatasets();
  const [notice, setNotice] = useState(null);
  const [actionError, setActionError] = useState("");
  const { data, error, loading, retry } = useApi(() => api.datasets(), [version]);
  const changed = () => {
    setVersion((v) => v + 1);
    reload();
  };

  return (
    <section>
      <h1 className="page-title">Datasets</h1>
      <p className="page-lead">
        On <a href="https://patents.google.com" target="_blank" rel="noopener noreferrer">patents.google.com</a>, run a
        search and choose <em>Download (CSV)</em>, then import the file here.
      </p>

      {readOnly ? (
        <p className="read-only-note">This is a read-only demo: importing and deleting datasets is disabled.</p>
      ) : (
        <UploadDataset
          onUploaded={(dataset) => {
            setNotice(dataset);
            changed();
          }}
        />
      )}
      {notice && (
        <div className="notice" role="status">
          Imported <strong>{notice.import.imported}</strong> patents into “{notice.name}”
          {notice.import.duplicates > 0 && <> · {notice.import.duplicates} duplicate rows merged</>}
          {notice.import.skipped > 0 && <> · {notice.import.skipped} rows without id or title skipped</>}
          <button type="button" className="icon-button" aria-label="Dismiss" onClick={() => setNotice(null)}>
            ×
          </button>
        </div>
      )}

      <ErrorMessage error={error} onRetry={retry} />
      {actionError && <p className="error">{actionError}</p>}
      {loading && !data && <p className="muted">Loading…</p>}
      {data && (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Patents</th>
                <th>Imported</th>
                {!readOnly && <th aria-label="Actions" />}
              </tr>
            </thead>
            <tbody>
              {data.map((dataset) => (
                <tr key={dataset.id}>
                  <td>
                    <DatasetName dataset={dataset} editable={!readOnly} onRenamed={changed} />
                    {dataset.search_url && (
                      <div className="muted small ellipsis" title={dataset.search_url}>
                        {dataset.search_url}
                      </div>
                    )}
                  </td>
                  <td>{dataset.patent_count}</td>
                  <td className="nowrap">{formatDateTime(dataset.imported_at)}</td>
                  {!readOnly && (
                    <td className="actions">
                      <button
                        type="button"
                        className="button button-danger"
                        onClick={() => {
                          setActionError("");
                          remove(dataset, changed).catch((err) => setActionError(err.message));
                        }}
                      >
                        Delete
                      </button>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <button type="button" className="button refresh" onClick={() => setVersion((v) => v + 1)}>
        Refresh
      </button>
    </section>
  );
}
