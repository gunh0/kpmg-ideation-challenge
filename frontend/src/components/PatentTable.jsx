import { useState } from "react";
import { Link } from "react-router";

import { safeUrl } from "../links";

export function formatDate(value) {
  return value || "—";
}

const COLUMNS = [
  { key: "patent_id", label: "Patent", sortable: true },
  { key: "title", label: "Title", sortable: true },
  { key: "assignee", label: "Assignee" },
  { key: "publication_date", label: "Published", sortable: true },
  { key: "cited_by", label: "Cited", sortable: true },
  { key: "grant_date", label: "Status", sortable: true },
];

// "-publication_date" -> {field: "publication_date", descending: true}; of
// "-matched,-cited_by" the first field counts.
export function parseOrdering(ordering) {
  const first = ordering.split(",")[0];
  const descending = first.startsWith("-");
  return { field: descending ? first.slice(1) : first, descending };
}

export function nextOrdering(ordering, field) {
  const current = parseOrdering(ordering);
  if (current.field !== field) return field;
  return current.descending ? field : `-${field}`;
}

function SortHeader({ column, ordering, onSort }) {
  if (!column.sortable || !onSort) return <th>{column.label}</th>;
  const current = parseOrdering(ordering);
  const active = current.field === column.key;
  const direction = active ? (current.descending ? "descending" : "ascending") : "none";
  return (
    <th aria-sort={direction}>
      <button type="button" className="sort" onClick={() => onSort(nextOrdering(ordering, column.key))}>
        {column.label}
        <span className="sort-arrow" aria-hidden="true">
          {active ? (current.descending ? "↓" : "↑") : "↕"}
        </span>
      </button>
    </th>
  );
}

const stop = (event) => event.stopPropagation();

// The representative figure, which opens the patent on Google Patents; the
// rest of the row opens the details. figure: undefined while it is looked up.
function Thumbnail({ patent, figure }) {
  const [failed, setFailed] = useState(null);
  const link = safeUrl(patent.result_link);
  const src = figure ? safeUrl(figure.thumbnail) : null;
  const image = src && src !== failed ? (
    <img src={src} alt="" loading="lazy" referrerPolicy="no-referrer" onError={() => setFailed(src)} />
  ) : (
    <span className={figure ? "thumb-none" : "thumb-wait"} aria-hidden="true" />
  );
  if (!link) return <span className="thumb">{image}</span>;
  return (
    <a
      className="thumb"
      href={link}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={`${patent.patent_id} on Google Patents`}
      onClick={stop}
      onKeyDown={stop}
    >
      {image}
    </a>
  );
}

// topicNames: {id: name}; given, a column names the topics of each patent.
// matchOf: the number of selected topics; above 0, a column shows how many of
// them each patent matches.
// figures: {id: {thumbnail, figure}} from useFigures, shown as the first column.
const MATCHES = { key: "matched", label: "Matches", sortable: true };

export default function PatentTable({ patents, ordering = "", onSort, onSelect, topicNames, figures, matchOf = 0 }) {
  return (
    <div className="table-wrap">
      <table className={`table patent-table${figures ? " with-figures" : ""}`}>
        <thead>
          <tr>
            {figures && <th className="cell-figure">Figure</th>}
            {matchOf > 0 && <SortHeader column={MATCHES} ordering={ordering} onSort={onSort} />}
            {COLUMNS.map((column) => (
              <SortHeader key={column.key} column={column} ordering={ordering} onSort={onSort} />
            ))}
            {topicNames && <th>Topics</th>}
          </tr>
        </thead>
        <tbody>
          {patents.map((patent) => (
            <tr
              key={patent.id}
              className={onSelect ? "clickable" : undefined}
              tabIndex={onSelect ? 0 : undefined}
              onClick={onSelect && (() => onSelect(patent))}
              onKeyDown={onSelect && ((event) => event.key === "Enter" && onSelect(patent))}
            >
              {figures && (
                <td className="cell-figure">
                  <Thumbnail patent={patent} figure={figures[patent.id] ?? undefined} />
                </td>
              )}
              {matchOf > 0 && (
                <td className="nowrap cell-matches">
                  <span className={`badge badge-match${patent.matched === matchOf ? " badge-match-all" : ""}`}>
                    {patent.matched} of {matchOf}
                  </span>
                </td>
              )}
              <td className="mono nowrap cell-id">{patent.patent_id}</td>
              <td className="cell-title">{patent.title}</td>
              <td className="cell-assignee">
                {patent.assignee ? (
                  <Link
                    to={`/assignees/${encodeURIComponent(patent.assignee)}`}
                    // The row itself opens the details.
                    onClick={stop}
                    onKeyDown={stop}
                  >
                    {patent.assignee}
                  </Link>
                ) : (
                  "—"
                )}
              </td>
              <td className="nowrap cell-date">{formatDate(patent.publication_date)}</td>
              <td className="numeric cell-cited">{patent.cited_by ?? "—"}</td>
              <td className="cell-status">
                <span className={`badge ${patent.is_granted ? "badge-granted" : "badge-pending"}`}>
                  {patent.is_granted ? "Granted" : "Application"}
                </span>
              </td>
              {topicNames && (
                <td className="muted small cell-topics">
                  {patent.topics.map((id) => topicNames[id]).filter(Boolean).join(", ") || "—"}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
