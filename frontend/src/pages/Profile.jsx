import { Link, useParams } from "react-router";

import { api } from "../api";
import { useDatasets } from "../DatasetContext";
import ErrorMessage from "../components/ErrorMessage";
import Ranking from "../components/Ranking";
import YearChart from "../components/YearChart";
import useApi from "../hooks/useApi";
import useTitle from "../hooks/useTitle";

function percent(part, whole) {
  return whole ? `${Math.round((100 * part) / whole)}%` : "—";
}

function activeYears(byYear) {
  const years = byYear.filter((row) => row.published > 0).map((row) => row.year);
  if (!years.length) return "—";
  const first = Math.min(...years);
  const last = Math.max(...years);
  return first === last ? String(first) : `${first}–${last}`;
}

// One assignee across the selected dataset: how much it files, since when,
// and who invents for it. The filters are those of the patent list.
export default function Profile() {
  const { name } = useParams();
  useTitle(name);
  const { selected: dataset } = useDatasets();
  const filter = { assignee: name };
  const { data, error, loading, retry } = useApi(() => api.stats({ ...filter, dataset }), [name, dataset]);
  const listUrl = `/patents?assignee=${encodeURIComponent(name)}`;

  return (
    <section>
      <p className="breadcrumb">
        <Link to="/">Dashboard</Link> / Assignee
      </p>
      <h1 className="page-title">{name}</h1>

      <ErrorMessage error={error} onRetry={retry} />
      {loading && !data && <p className="muted">Loading…</p>}
      {data && data.total === 0 && (
        <p className="page-lead">No patents of this assignee in the selected dataset.</p>
      )}
      {data && data.total > 0 && (
        <>
          <div className="cards">
            <div className="card">
              <div className="card-label">Patents</div>
              <div className="card-value">{data.total}</div>
              <div className="card-note">
                <Link to={listUrl}>Show all</Link>
              </div>
            </div>
            <div className="card">
              <div className="card-label">Granted</div>
              <div className="card-value">{data.granted}</div>
              <div className="card-note">{percent(data.granted, data.total)} of all</div>
            </div>
            <div className="card">
              <div className="card-label">Active</div>
              <div className="card-value card-value-text">{activeYears(data.by_year)}</div>
              <div className="card-note">years with publications</div>
            </div>
          </div>
          <div className="panel">
            <h2 className="panel-title">Patents per year</h2>
            <YearChart data={data.by_year} />
          </div>
          <div className="panel">
            <h2 className="panel-title">Top inventors</h2>
            <Ranking
              rows={data.top_inventors}
              linkTo={(row) => `/patents?assignee=${encodeURIComponent(name)}&inventor=${encodeURIComponent(row.name)}`}
              emptyText="No inventors listed."
            />
          </div>
        </>
      )}
    </section>
  );
}
