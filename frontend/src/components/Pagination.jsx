import { formatNumber } from "../format";

export default function Pagination({ page, pageSize, count, onChange }) {
  const pages = Math.max(1, Math.ceil(count / pageSize));
  if (pages === 1) return null;
  const first = (page - 1) * pageSize + 1;
  const last = Math.min(page * pageSize, count);

  return (
    <nav className="pagination" aria-label="Pages">
      <button type="button" className="button" disabled={page <= 1} onClick={() => onChange(page - 1)}>
        ← Previous
      </button>
      <span className="muted">
        {formatNumber(first)}–{formatNumber(last)} of {formatNumber(count)} · page {page} of {formatNumber(pages)}
      </span>
      <button type="button" className="button" disabled={page >= pages} onClick={() => onChange(page + 1)}>
        Next →
      </button>
    </nav>
  );
}
