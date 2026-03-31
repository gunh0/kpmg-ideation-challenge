import { Link, useSearchParams } from "react-router";

import { api } from "../api";
import LatestPatents from "../components/LatestPatents";
import MostCited from "../components/MostCited";
import Ranking from "../components/Ranking";
import TopicTrends from "../components/TopicTrends";
import YearChart from "../components/YearChart";
import { useTopics } from "../TopicContext";
import EmptyState from "../components/EmptyState";
import ErrorMessage from "../components/ErrorMessage";
import useApi from "../hooks/useApi";
import useTitle from "../hooks/useTitle";
import { countryName, formatNumber } from "../format";

function percent(part, whole) {
  return whole ? `${Math.round((100 * part) / whole)}%` : "—";
}

export default function Dashboard() {
  useTitle("Dashboard");
  const { selected, topicsParam: topics, topics: allTopics, loaded } = useTopics();
  // ?country=KR narrows the whole dashboard to one country's assignees.
  const [searchParams, setSearchParams] = useSearchParams();
  const country = searchParams.get("country") || "";
  const { data, error, loading, retry } = useApi(() => api.stats({ topics, country }), [topics, country]);
  const latest = useApi(
    () => api.patents({ topics, country, has_figure: true, ordering: "-publication_date", page_size: 8 }),
    [topics, country]
  );
  const cited = useApi(() => api.patents({ topics, country, ordering: "-cited_by", page_size: 8 }), [topics, country]);
  const names = allTopics.filter((topic) => selected.includes(String(topic.id))).map((topic) => topic.name);

  if (loaded && allTopics.length === 0) {
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
        {names.length ? names.map((name) => `“${name}”`).join(" + ") : "All topics"}
      </p>
      {country && (
        <p className="chips">
          <span className="chip">
            Assignees from {countryName(country)}
            <button type="button" aria-label="Show all countries" onClick={() => setSearchParams({})}>
              ×
            </button>
          </span>
        </p>
      )}

      <ErrorMessage error={error} onRetry={retry} />
      {loading && !data && <p className="muted">Loading…</p>}
      {data && (
        <div className="cards">
          <div className="card">
            <div className="card-label">Patents</div>
            <div className="card-value">{formatNumber(data.total)}</div>
          </div>
          <div className="card">
            <div className="card-label">Granted</div>
            <div className="card-value">{formatNumber(data.granted)}</div>
            <div className="card-note">{percent(data.granted, data.total)} of all</div>
          </div>
          <div className="card">
            <div className="card-label">Applications</div>
            <div className="card-value">{formatNumber(data.total - data.granted)}</div>
          </div>
          <div className="card">
            <div className="card-label">Top assignee</div>
            <div className="card-value card-value-text">{data.top_assignees[0]?.name || "—"}</div>
            {data.top_assignees[0] && <div className="card-note">{formatNumber(data.top_assignees[0].count)} patents</div>}
          </div>
        </div>
      )}
      {latest.data && (
        <div className="panel">
          <div className="panel-head">
            <h2 className="panel-title">Latest patents</h2>
            <Link to="/patents" className="small">
              All patents →
            </Link>
          </div>
          <LatestPatents patents={latest.data.results} />
        </div>
      )}
      {data && (
        <div className="panel">
          <h2 className="panel-title">Patents per year</h2>
          <YearChart data={data.by_year} />
        </div>
      )}
      {data && data.by_topic.length > 1 && (
        <div className="panel">
          <h2 className="panel-title">Topics per year</h2>
          <TopicTrends topics={data.by_topic} allTopics={allTopics} />
        </div>
      )}
      {data && (
        <div className="grid-2 grid-gap">
          <div className="panel">
            <h2 className="panel-title">Assignee countries</h2>
            <Ranking
              rows={data.top_countries.map((row) => ({ ...row, name: countryName(row.code) }))}
              linkTo={(row) => `/?country=${row.code}`}
              emptyText="No assignee countries in this selection."
            />
          </div>
          <div className="panel">
            <div className="panel-head">
              <h2 className="panel-title">Most cited</h2>
              <Link to="/patents?ordering=-cited_by" className="small">
                All by citations →
              </Link>
            </div>
            {cited.data && <MostCited patents={cited.data.results} />}
          </div>
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
