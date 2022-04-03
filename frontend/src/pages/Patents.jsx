import { api } from "../api";
import PatentTable from "../components/PatentTable";
import useApi from "../hooks/useApi";

export default function Patents() {
  const { data, error, loading } = useApi(() => api.patents(), []);

  return (
    <section>
      <h1 className="page-title">Patents</h1>
      <p className="page-lead">Search and filter the patents of the selected dataset.</p>
      {error && <p className="error">{error.message}</p>}
      {loading && !data && <p className="muted">Loading…</p>}
      {data && (
        <>
          <p className="muted">{data.count} patents</p>
          <PatentTable patents={data.results} />
        </>
      )}
    </section>
  );
}
