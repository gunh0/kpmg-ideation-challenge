import { Link } from "react-router";

// Shown until the first topic is stored: the backend loads the bundled
// snapshot when it starts, so this is only seen on an empty custom setup.
export default function EmptyState() {
  return (
    <div className="empty">
      <div className="empty-mark" aria-hidden="true">
        ⚖
      </div>
      <h2>No patents yet</h2>
      <p className="muted">
        The topics are filled from the bundled snapshot when the backend starts, and collected again when Google
        Patents Public Data changes. Run <code>python manage.py load_seed</code> or <code>collect_patents</code> if
        you started the backend another way.
      </p>
      <Link className="button button-primary" to="/topics">
        About the topics
      </Link>
    </div>
  );
}
