import { api } from "../api";
import ErrorMessage from "../components/ErrorMessage";
import useApi from "../hooks/useApi";
import useTitle from "../hooks/useTitle";

function formatDateTime(value) {
  return value ? new Date(value).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }) : "—";
}

export default function Datasets() {
  useTitle("Datasets");
  const { data, error, loading, retry } = useApi(() => api.datasets(), []);

  return (
    <section>
      <h1 className="page-title">Datasets</h1>
      <ErrorMessage error={error} onRetry={retry} />
      {loading && !data && <p className="muted">Loading…</p>}
      {data && (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Patents</th>
                <th>Collected</th>
              </tr>
            </thead>
            <tbody>
              {data.map((dataset) => (
                <tr key={dataset.id}>
                  <td>
                    <strong>{dataset.name}</strong>
                  </td>
                  <td>{dataset.patent_count}</td>
                  <td className="nowrap">{formatDateTime(dataset.collected_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
