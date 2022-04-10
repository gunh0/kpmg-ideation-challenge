import { useEffect } from "react";

import { formatDate } from "./PatentTable";

const DATES = [
  ["priority_date", "Priority"],
  ["filing_date", "Filed"],
  ["publication_date", "Published"],
  ["grant_date", "Granted"],
];

export default function PatentDetail({ patent, onClose }) {
  useEffect(() => {
    const onKey = (event) => event.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <aside
        className="drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="patent-title"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="drawer-head">
          <span className="mono muted">{patent.patent_id}</span>
          <button type="button" className="icon-button" aria-label="Close" onClick={onClose}>
            ×
          </button>
        </div>
        <h2 id="patent-title" className="drawer-title">
          {patent.title}
        </h2>
        <span className={`badge ${patent.is_granted ? "badge-granted" : "badge-pending"}`}>
          {patent.is_granted ? "Granted" : "Application"}
        </span>

        <dl className="facts">
          <dt>Assignee</dt>
          <dd>{patent.assignee || "—"}</dd>
          <dt>Inventors</dt>
          <dd>{patent.inventors.length ? patent.inventors.join(", ") : "—"}</dd>
          {DATES.map(([field, label]) => (
            <div key={field} className="fact-row">
              <dt>{label}</dt>
              <dd>{formatDate(patent[field])}</dd>
            </div>
          ))}
        </dl>
      </aside>
    </div>
  );
}
