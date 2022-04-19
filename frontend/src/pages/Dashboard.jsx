import { api } from "../api";
import YearChart from "../components/YearChart";
import { useDatasets } from "../DatasetContext";
import useApi from "../hooks/useApi";

function percent(part, whole) {
  return whole ? `${Math.round((100 * part) / whole)}%` : "—";
}

export default function Dashboard() {
  const { selected: dataset, datasets } = useDatasets();
  const { data, error, loading } = useApi(() => api.stats({ dataset }), [dataset]);
  const name = datasets.find((item) => String(item.id) === dataset)?.name;

  return (
    <section>
      <h1 className="page-title">Dashboard</h1>
      <p className="page-lead">{name ? `Dataset “${name}”` : "All datasets"}</p>

      {error && <p className="error">{error.message}</p>}
      {loading && !data && <p className="muted">Loading…</p>}
      {data && (
        <div className="cards">
          <div className="card">
            <div className="card-label">Patents</div>
            <div className="card-value">{data.total}</div>
          </div>
          <div className="card">
            <div className="card-label">Granted</div>
            <div className="card-value">{data.granted}</div>
            <div className="card-note">{percent(data.granted, data.total)} of all</div>
          </div>
          <div className="card">
            <div className="card-label">Applications</div>
            <div className="card-value">{data.total - data.granted}</div>
          </div>
          <div className="card">
            <div className="card-label">Top assignee</div>
            <div className="card-value card-value-text">{data.top_assignees[0]?.name || "—"}</div>
            {data.top_assignees[0] && <div className="card-note">{data.top_assignees[0].count} patents</div>}
          </div>
        </div>
      )}
      {data && (
        <div className="panel">
          <h2 className="panel-title">Patents per year</h2>
          <YearChart data={data.by_year} />
        </div>
      )}
    </section>
  );
}
