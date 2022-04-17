import { useEffect, useState } from "react";

import { api } from "../api";
import { useDatasets } from "../DatasetContext";
import AssigneeFilter from "../components/AssigneeFilter";
import Pagination from "../components/Pagination";
import PatentDetail from "../components/PatentDetail";
import PatentTable from "../components/PatentTable";
import useApi from "../hooks/useApi";
import useDebounce from "../hooks/useDebounce";
import useQueryParams from "../hooks/useQueryParams";

const PAGE_SIZE = 25;
const DEFAULTS = {
  search: "",
  assignee: "",
  granted: "",
  year_from: "",
  year_to: "",
  ordering: "-publication_date",
  page: "1",
};

// Text inputs keep their own state while typing and write to the URL debounced.
function useDebouncedParam(value, onChange) {
  const [text, setText] = useState(value);
  const debounced = useDebounce(text);
  useEffect(() => setText(value), [value]);
  useEffect(() => {
    if (debounced !== value) onChange(debounced);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debounced]);
  return [text, setText];
}

export default function Patents() {
  const [params, update] = useQueryParams(DEFAULTS);
  const { selected: dataset } = useDatasets();
  const page = Number(params.page) || 1;
  const [search, setSearch] = useDebouncedParam(params.search, (value) => update({ search: value.trim() }));
  const [yearFrom, setYearFrom] = useDebouncedParam(params.year_from, (value) => update({ year_from: value }));
  const [yearTo, setYearTo] = useDebouncedParam(params.year_to, (value) => update({ year_to: value }));

  const [selected, setSelected] = useState(null);
  const { data, error, loading } = useApi(
    () => api.patents({ ...params, dataset, page, page_size: PAGE_SIZE }),
    [params, dataset]
  );

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
        <AssigneeFilter value={params.assignee} dataset={dataset} onChange={(value) => update({ assignee: value })} />
        <select
          className="select"
          aria-label="Grant status"
          value={params.granted}
          onChange={(event) => update({ granted: event.target.value })}
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
            onChange={(event) => setYearFrom(event.target.value)}
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
            onChange={(event) => setYearTo(event.target.value)}
          />
        </div>
      </div>

      {error && <p className="error">{error.message}</p>}
      {loading && !data && <p className="muted">Loading…</p>}
      {data && (
        <>
          <p className="muted">
            {data.count} patents{params.search && <> matching “{params.search}”</>}
          </p>
          <PatentTable
            patents={data.results}
            ordering={params.ordering}
            onSort={(ordering) => update({ ordering })}
            onSelect={setSelected}
          />
          <Pagination
            page={page}
            pageSize={PAGE_SIZE}
            count={data.count}
            onChange={(next) => update({ page: String(next) })}
          />
        </>
      )}
      {selected && <PatentDetail patent={selected} onClose={() => setSelected(null)} />}
    </section>
  );
}
