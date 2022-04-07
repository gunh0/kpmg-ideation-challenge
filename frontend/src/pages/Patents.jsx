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
  const [granted, setGranted] = useState("");
  const [yearFrom, setYearFrom] = useState("");
  const [yearTo, setYearTo] = useState("");
  const query = useDebounce(search.trim());
  const debouncedYearFrom = useDebounce(yearFrom);
  const debouncedYearTo = useDebounce(yearTo);
  const { data, error, loading } = useApi(
    () =>
      api.patents({
        search: query,
        granted,
        year_from: debouncedYearFrom,
        year_to: debouncedYearTo,
        ordering,
        page,
        page_size: PAGE_SIZE,
      }),
    [query, granted, debouncedYearFrom, debouncedYearTo, ordering, page]
  );

  function withFirstPage(setter) {
    return (value) => {
      setter(value);
      setPage(1);
    };
  }

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
        <select
          className="select"
          aria-label="Grant status"
          value={granted}
          onChange={(event) => withFirstPage(setGranted)(event.target.value)}
        >
          <option value="">All statuses</option>
          <option value="true">Granted</option>
          <option value="false">Applications</option>
        </select>
        <div className="year-range">
          <input
            type="number"
            className="input year"
            placeholder="From"
            aria-label="Published from year"
            min="1900"
            max="2100"
            value={yearFrom}
            onChange={(event) => withFirstPage(setYearFrom)(event.target.value)}
          />
          <span className="muted">–</span>
          <input
            type="number"
            className="input year"
            placeholder="To"
            aria-label="Published to year"
            min="1900"
            max="2100"
            value={yearTo}
            onChange={(event) => withFirstPage(setYearTo)(event.target.value)}
          />
        </div>
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
