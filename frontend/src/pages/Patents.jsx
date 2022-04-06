import { useState } from "react";

import { api } from "../api";
import Pagination from "../components/Pagination";
import PatentTable from "../components/PatentTable";
import useApi from "../hooks/useApi";
import useDebounce from "../hooks/useDebounce";

const PAGE_SIZE = 25;

export default function Patents() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [ordering, setOrdering] = useState("-publication_date");
  const query = useDebounce(search.trim());
  const { data, error, loading } = useApi(
    () => api.patents({ search: query, ordering, page, page_size: PAGE_SIZE }),
    [query, ordering, page]
  );

  function changeOrdering(value) {
    setOrdering(value);
    setPage(1);
  }

  function changeSearch(value) {
    setSearch(value);
    setPage(1);
  }

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
          onChange={(event) => changeSearch(event.target.value)}
        />
      </div>

      {error && <p className="error">{error.message}</p>}
      {loading && !data && <p className="muted">Loading…</p>}
      {data && (
        <>
          <p className="muted">
            {data.count} patents{query && <> matching “{query}”</>}
          </p>
          <PatentTable patents={data.results} ordering={ordering} onSort={changeOrdering} />
          <Pagination page={page} pageSize={PAGE_SIZE} count={data.count} onChange={setPage} />
        </>
      )}
    </section>
  );
}
