import { useState } from "react";

import { api } from "../api";
import PatentTable from "../components/PatentTable";
import useApi from "../hooks/useApi";
import useDebounce from "../hooks/useDebounce";

export default function Patents() {
  const [search, setSearch] = useState("");
  const query = useDebounce(search.trim());
  const { data, error, loading } = useApi(() => api.patents({ search: query }), [query]);

  return (
    <section>
      <h1 className="page-title">Patents</h1>
      <p className="page-lead">Search and filter the patents of the selected dataset.</p>

      <div className="toolbar">
        <input
          type="search"
          className="input search"
          placeholder="Search id, title, assignee or inventor"
          aria-label="Search patents"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
      </div>

      {error && <p className="error">{error.message}</p>}
      {loading && !data && <p className="muted">Loading…</p>}
      {data && (
        <>
          <p className="muted">
            {data.count} patents{query && <> matching “{query}”</>}
          </p>
          <PatentTable patents={data.results} />
        </>
      )}
    </section>
  );
}
