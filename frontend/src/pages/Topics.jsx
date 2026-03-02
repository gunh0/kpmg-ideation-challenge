import { Link, useNavigate } from "react-router";

import { api } from "../api";
import { useDatasets } from "../DatasetContext";
import ErrorMessage from "../components/ErrorMessage";
import { formatNumber } from "../format";
import useApi from "../hooks/useApi";
import useTitle from "../hooks/useTitle";

const SOURCE = "https://huggingface.co/datasets/labofsahil/patents-publications-dataset";

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString(undefined, { dateStyle: "medium" }) : "not yet";
}

// The technology fields the app follows, where their patents come from and
// when they were collected.
export default function Topics() {
  useTitle("Topics");
  const navigate = useNavigate();
  const { setSelected } = useDatasets();
  const { data, error, loading, retry } = useApi(() => api.datasets(), []);
  const revision = data?.find((topic) => topic.source_revision)?.source_revision;

  function open(topic, path) {
    setSelected(String(topic.id));
    navigate(path);
  }

  return (
    <section>
      <h1 className="page-title">Topics</h1>
      <p className="page-lead">
        US patents published since 2015 whose title matches a topic, one entry per application. They are collected from
        Google Patents Public Data and refreshed when it changes.
      </p>

      <ErrorMessage error={error} onRetry={retry} />
      {loading && !data && <p className="muted">Loading…</p>}
      {data && (
        <div className="topics">
          {data.map((topic) => (
            <article key={topic.id} className="panel topic">
              <h2 className="panel-title">{topic.name}</h2>
              <p>{topic.description}</p>
              <p className="topic-count">
                <strong>{formatNumber(topic.patent_count)}</strong> patents
                <span className="muted"> · collected {formatDate(topic.collected_at)}</span>
              </p>
              {topic.pattern && (
                <p className="muted small">
                  Title matches <code>{topic.pattern}</code>
                </p>
              )}
              <p className="topic-links">
                <button type="button" className="button button-primary" onClick={() => open(topic, "/")}>
                  Dashboard
                </button>
                <button type="button" className="button" onClick={() => open(topic, "/patents")}>
                  Patents
                </button>
              </p>
            </article>
          ))}
        </div>
      )}

      <h2 className="section-title">Source</h2>
      <p className="muted">
        <a href="https://console.cloud.google.com/marketplace/product/google_patents_public_datasets/google-patents-public-data">
          Google Patents Public Data
        </a>{" "}
        by IFI CLAIMS Patent Services and Google, licensed under{" "}
        <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>, read from its{" "}
        <a href={revision ? `${SOURCE}/tree/${revision}` : SOURCE}>Parquet copy</a>
        {revision && (
          <>
            {" "}
            at revision <code>{revision.slice(0, 12)}</code>
          </>
        )}
        . Figures and links lead to <a href="https://patents.google.com">Google Patents</a>. See also the{" "}
        <Link to="/patents">full patent list</Link>.
      </p>
    </section>
  );
}
