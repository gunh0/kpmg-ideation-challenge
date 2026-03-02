import { useState } from "react";
import { Link, useParams } from "react-router";

import { api } from "../api";
import { useDatasets } from "../DatasetContext";
import ErrorMessage from "../components/ErrorMessage";
import PatentDetail from "../components/PatentDetail";
import PatentTable from "../components/PatentTable";
import Ranking from "../components/Ranking";
import YearChart from "../components/YearChart";
import useApi from "../hooks/useApi";
import useFigures from "../hooks/useFigures";
import useTitle from "../hooks/useTitle";
import { formatNumber } from "../format";

const LATEST = 5;

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

const path = (kind, name) => `/${kind}s/${encodeURIComponent(name)}`;

// What each kind of profile ranks next to the yearly chart.
const KINDS = {
  assignee: {
    label: "Assignee",
    rankings: [{ title: "Top inventors", key: "top_inventors", kind: "inventor" }],
  },
  inventor: {
    label: "Inventor",
    rankings: [
      { title: "Assignees", key: "top_assignees", kind: "assignee" },
      { title: "Co-inventors", key: "top_inventors", kind: "inventor" },
    ],
  },
};

// One assignee or inventor across the selected dataset: how much they file,
// since when, and with whom. The filters are those of the patent list.
export default function Profile({ kind }) {
  const { name } = useParams();
  useTitle(name);
  const { selected: dataset } = useDatasets();
  const filter = { [kind]: name };
  const { data, error, loading, retry } = useApi(() => api.stats({ ...filter, dataset }), [kind, name, dataset]);
  const latest = useApi(
    () => api.patents({ ...filter, dataset, ordering: "-publication_date", page_size: LATEST }),
    [kind, name, dataset]
  );
  const [open, setOpen] = useState(null);
  const figures = useFigures(latest.data?.results);
  const listUrl = `/patents?${kind}=${encodeURIComponent(name)}`;
  const { label, rankings } = KINDS[kind];

  return (
    <section>
      <p className="breadcrumb">
        <Link to="/">Dashboard</Link> / {label}
      </p>
      <h1 className="page-title">{name}</h1>

      <ErrorMessage error={error} onRetry={retry} />
      {loading && !data && <p className="muted">Loading…</p>}
      {data && data.total === 0 && (
        <p className="page-lead">No patents of this {kind} in the selected topic.</p>
      )}
      {data && data.total > 0 && (
        <>
          <div className="cards">
            <div className="card">
              <div className="card-label">Patents</div>
              <div className="card-value">{formatNumber(data.total)}</div>
              <div className="card-note">
                <Link to={listUrl}>Show all</Link>
              </div>
            </div>
            <div className="card">
              <div className="card-label">Granted</div>
              <div className="card-value">{formatNumber(data.granted)}</div>
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
          {latest.data && (
            <div className="panel">
              <h2 className="panel-title">Latest publications</h2>
              <PatentTable patents={latest.data.results} onSelect={setOpen} figures={figures} />
              {data.total > LATEST && (
                <p className="panel-more">
                  <Link to={listUrl}>All {formatNumber(data.total)} patents →</Link>
                </p>
              )}
            </div>
          )}
          <div className="grid-2">
            {rankings.map((ranking) => (
              <div className="panel" key={ranking.key}>
                <h2 className="panel-title">{ranking.title}</h2>
                <Ranking
                  // An inventor is always among the top inventors of their own patents.
                  rows={data[ranking.key].filter((row) => ranking.kind !== kind || row.name !== name)}
                  linkTo={(row) => path(ranking.kind, row.name)}
                  emptyText="Nobody else is listed."
                />
              </div>
            ))}
          </div>
        </>
      )}
      {open && <PatentDetail patent={open} onClose={() => setOpen(null)} />}
    </section>
  );
}
