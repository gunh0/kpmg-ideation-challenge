import { Link } from "react-router-dom";

export default function EmptyState() {
  return (
    <div className="empty">
      <div className="empty-mark" aria-hidden="true">
        ⚖
      </div>
      <h2>No patents yet</h2>
      <p className="muted">
        Search on Google Patents, download the results as CSV and import the file to explore it here.
      </p>
      <Link className="button button-primary" to="/datasets">
        Import a dataset
      </Link>
    </div>
  );
}
