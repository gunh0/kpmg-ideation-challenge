export function formatDate(value) {
  return value || "—";
}

const COLUMNS = [
  { key: "patent_id", label: "Patent", sortable: true },
  { key: "title", label: "Title", sortable: true },
  { key: "assignee", label: "Assignee" },
  { key: "publication_date", label: "Published", sortable: true },
  { key: "grant_date", label: "Status", sortable: true },
];

// "-publication_date" -> {field: "publication_date", descending: true}
export function parseOrdering(ordering) {
  const descending = ordering.startsWith("-");
  return { field: descending ? ordering.slice(1) : ordering, descending };
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

export default function PatentTable({ patents, ordering = "", onSort, onSelect }) {
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            {COLUMNS.map((column) => (
              <SortHeader key={column.key} column={column} ordering={ordering} onSort={onSort} />
            ))}
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
              <td className="mono nowrap">{patent.patent_id}</td>
              <td>{patent.title}</td>
              <td>{patent.assignee || "—"}</td>
              <td className="nowrap">{formatDate(patent.publication_date)}</td>
              <td>
                <span className={`badge ${patent.is_granted ? "badge-granted" : "badge-pending"}`}>
                  {patent.is_granted ? "Granted" : "Application"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
