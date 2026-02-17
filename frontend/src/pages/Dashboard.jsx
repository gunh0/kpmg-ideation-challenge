import { api } from "../api";
import Ranking from "../components/Ranking";
import YearChart from "../components/YearChart";
import { useDatasets } from "../DatasetContext";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import useApi from "../hooks/useApi";
import useTitle from "../hooks/useTitle";

function percent(part, whole) {
  return whole ? `${Math.round((100 * part) / whole)}%` : "—";
}

export default function Dashboard() {
  useTitle("Dashboard");
  const { selected: dataset, datasets, loaded } = useDatasets();
  const { data, error, loading, retry } = useApi(() => api.stats({ dataset }), [dataset]);
  const current = datasets.find((item) => String(item.id) === dataset);
  const name = current?.name;

  if (loaded && datasets.length === 0) {
    return (
      <section>
        <h1 className="page-title">Dashboard</h1>
        <EmptyState />
      </section>
    );
  }

  return (
    <section>
      <h1 className="page-title">Dashboard</h1>
      <p className="page-lead">
        {name ? `Dataset “${name}”` : "All datasets"}
      </p>

      <ErrorMessage error={error} onRetry={retry} />
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
      {data && (
        <div className="grid-2">
          <div className="panel">
            <h2 className="panel-title">Top assignees</h2>
            <Ranking
              rows={data.top_assignees}
              linkTo={(row) => `/assignees/${encodeURIComponent(row.name)}`}
              emptyText="No assignees in this selection." />
          </div>
          <div className="panel">
            <h2 className="panel-title">Top inventors</h2>
            <Ranking
              rows={data.top_inventors}
              linkTo={(row) => `/inventors/${encodeURIComponent(row.name)}`}
              emptyText="No inventors in this selection." />
          </div>
        </div>
      )}
    </section>
  );
}
