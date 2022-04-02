import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <section>
      <h1 className="page-title">Page not found</h1>
      <p className="page-lead">
        <Link to="/">Back to the dashboard</Link>
      </p>
    </section>
  );
}
