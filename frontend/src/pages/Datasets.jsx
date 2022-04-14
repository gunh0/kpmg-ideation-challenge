import { useState } from "react";

import { api } from "../api";
import UploadDataset from "../components/UploadDataset";
import useApi from "../hooks/useApi";

function formatDateTime(value) {
  return new Date(value).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

export default function Datasets() {
  const [version, setVersion] = useState(0);
  const { data, error, loading } = useApi(() => api.datasets(), [version]);

  return (
    <section>
      <h1 className="page-title">Datasets</h1>
      <p className="page-lead">
        On <a href="https://patents.google.com" target="_blank" rel="noopener noreferrer">patents.google.com</a>, run a
        search and choose <em>Download (CSV)</em>, then import the file here.
      </p>

      <UploadDataset onUploaded={() => setVersion((v) => v + 1)} />

      {error && <p className="error">{error.message}</p>}
      {loading && !data && <p className="muted">Loading…</p>}
      {data && (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Patents</th>
                <th>Imported</th>
              </tr>
            </thead>
            <tbody>
              {data.map((dataset) => (
                <tr key={dataset.id}>
                  <td>
                    <strong>{dataset.name}</strong>
                    {dataset.search_url && (
                      <div className="muted small ellipsis" title={dataset.search_url}>
                        {dataset.search_url}
                      </div>
                    )}
                  </td>
                  <td>{dataset.patent_count}</td>
                  <td className="nowrap">{formatDateTime(dataset.imported_at)}</td>
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
