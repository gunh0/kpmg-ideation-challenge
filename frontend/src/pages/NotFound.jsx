import { Link } from "react-router";
import useTitle from "../hooks/useTitle";

export default function NotFound() {
  useTitle("Page not found");
  return (
    <section>
      <h1 className="page-title">Page not found</h1>
      <p className="page-lead">
        <Link to="/">Back to the dashboard</Link>
      </p>
    </section>
  );
}
