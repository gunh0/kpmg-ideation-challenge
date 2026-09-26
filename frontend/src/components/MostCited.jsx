import { safeUrl } from "../links";
import { formatNumber } from "../format";

// The patents cited by the most other applications, each opening on Google Patents.
export default function MostCited({ patents }) {
  const cited = patents.filter((patent) => patent.cited_by > 0);
  if (!cited.length) return <p className="muted">No citations counted for this selection.</p>;
  return (
    <ol className="cited">
      {cited.map((patent) => (
        <li key={patent.id}>
          <a href={safeUrl(patent.result_link) || undefined} target="_blank" rel="noopener noreferrer">
            {patent.title}
          </a>
          <span className="muted small">
            {patent.assignee || "—"} · {patent.patent_id}
          </span>
          <span className="cited-count">
            {formatNumber(patent.cited_by)} <span className="muted small">cited by</span>
          </span>
        </li>
      ))}
    </ol>
  );
}
