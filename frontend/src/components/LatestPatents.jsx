import { useState } from "react";

import { safeUrl } from "../links";

// A card per patent: its representative figure, title, assignee and date.
// The whole card opens the patent on Google Patents.
function Card({ patent }) {
  const [failed, setFailed] = useState(false);
  const link = safeUrl(patent.result_link);
  const src = safeUrl(patent.thumbnail_link);

  return (
    <li>
      <a className="latest-card" href={link || undefined} target="_blank" rel="noopener noreferrer">
        <span className="latest-figure">
          {src && !failed ? (
            <img src={src} alt="" loading="lazy" referrerPolicy="no-referrer" onError={() => setFailed(true)} />
          ) : (
            <span className="thumb-none" aria-hidden="true" />
          )}
        </span>
        <span className="latest-title">{patent.title}</span>
        <span className="latest-meta">
          {patent.assignee || "—"} · {patent.publication_date}
        </span>
      </a>
    </li>
  );
}

export default function LatestPatents({ patents }) {
  if (!patents.length) return <p className="muted">No figures looked up for this selection yet.</p>;
  return (
    <ul className="latest">
      {patents.map((patent) => (
        <Card key={patent.id} patent={patent} />
      ))}
    </ul>
  );
}
