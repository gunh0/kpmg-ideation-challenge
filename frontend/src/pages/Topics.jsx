import { useState } from "react";
import { Link, useNavigate } from "react-router";

import { api } from "../api";
import { useTopics } from "../TopicContext";
import ErrorMessage from "../components/ErrorMessage";
import TopicForm from "../components/TopicForm";
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
  const { setSelected, reload: reloadPicker } = useTopics();
  const [version, setVersion] = useState(0);
  const { data, error, loading, retry } = useApi(() => api.topics(), [version]);
  const config = useApi(() => api.config(), []);
  const [adding, setAdding] = useState(false);

  function changed() {
    setVersion((v) => v + 1);
    reloadPicker();
  }

  async function add(values) {
    await api.createTopic(values);
    setAdding(false);
    changed();
  }
  const revision = data?.find((topic) => topic.source_revision)?.source_revision;

  function open(topic, path) {
    setSelected([String(topic.id)]);
    navigate(path);
  }

  return (
    <section>
      <h1 className="page-title">Topics</h1>
      <p className="page-lead">
        US patents published since 2015 whose title or abstract matches a topic’s keywords, one entry per application.
        They are collected from Google Patents Public Data and refreshed when it changes.
      </p>

      {config.data?.topic_edits &&
        (adding ? (
          <div className="panel">
            <h2 className="panel-title">New topic</h2>
            <p className="muted small">
              It shows the stored patents that match at once, then grows while the public data is searched — that takes a
              while.
            </p>
            <TopicForm submitLabel="Add topic" onSave={add} onCancel={() => setAdding(false)} />
          </div>
        ) : (
          <p>
            <button type="button" className="button button-primary" onClick={() => setAdding(true)}>
              Add a topic
            </button>
          </p>
        ))}

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
              {topic.keywords.length > 0 && (
                <p className="keywords" aria-label="Keywords">
                  {topic.keywords.map((keyword) => (
                    <span key={keyword} className="keyword">
                      {keyword}
                    </span>
                  ))}
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
