import { Fragment, useEffect, useRef } from "react";
import { Link } from "react-router";

import { safeUrl } from "../links";
import { formatDate } from "./PatentTable";

const DATES = [
  ["priority_date", "Priority"],
  ["filing_date", "Filed"],
  ["publication_date", "Published"],
  ["grant_date", "Granted"],
];

export default function PatentDetail({ patent, onClose }) {
  const link = safeUrl(patent.result_link);
  const figure = safeUrl(patent.figure_link);

  const drawer = useRef(null);

  useEffect(() => {
    const onKey = (event) => event.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  // Move focus into the dialog and give it back to the row that opened it.
  useEffect(() => {
    const opener = document.activeElement;
    drawer.current?.querySelector("button")?.focus();
    return () => opener?.focus?.();
  }, []);

  // Tab and Shift+Tab cycle within the dialog while it is open.
  function trapFocus(event) {
    if (event.key !== "Tab") return;
    const items = drawer.current.querySelectorAll("a[href], button");
    const first = items[0];
    const last = items[items.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <aside
        className="drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="patent-title"
        ref={drawer}
        onKeyDown={trapFocus}
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
          <dd>
            {patent.assignee ? (
              <Link to={`/assignees/${encodeURIComponent(patent.assignee)}`} onClick={onClose}>
                {patent.assignee}
              </Link>
            ) : (
              "—"
            )}
          </dd>
          <dt>Inventors</dt>
          <dd>
            {patent.inventors.length
              ? patent.inventors.map((name, i) => (
                  <Fragment key={name}>
                    {i > 0 && ", "}
                    <Link to={`/inventors/${encodeURIComponent(name)}`} onClick={onClose}>
                      {name}
                    </Link>
                  </Fragment>
                ))
              : "—"}
          </dd>
          {DATES.map(([field, label]) => (
            <div key={field} className="fact-row">
              <dt>{label}</dt>
              <dd>{formatDate(patent[field])}</dd>
            </div>
          ))}
        </dl>

        {figure && (
          <figure className="figure">
            <img src={figure} alt={`Representative figure of ${patent.patent_id}`} loading="lazy" referrerPolicy="no-referrer" />
          </figure>
        )}
        {link && (
          <a className="button button-primary" href={link} target="_blank" rel="noopener noreferrer">
            Open in Google Patents ↗
          </a>
        )}
      </aside>
    </div>
  );
}
