import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router";

import { api } from "../api";
import { useDatasets } from "../DatasetContext";
import EmptyState from "../components/EmptyState";
import AssigneeFilter from "../components/AssigneeFilter";
import Pagination from "../components/Pagination";
import PatentDetail from "../components/PatentDetail";
import PatentTable from "../components/PatentTable";
import ErrorMessage from "../components/ErrorMessage";
import useApi from "../hooks/useApi";
import useDebounce from "../hooks/useDebounce";
import useQueryParams from "../hooks/useQueryParams";
import useTitle from "../hooks/useTitle";

const PAGE_SIZE = 25;
const DEFAULTS = {
  search: "",
  assignee: "",
  inventor: "",
  granted: "",
  year_from: "",
  year_to: "",
  ordering: "-publication_date",
  page: "1",
};

// Text inputs keep their own state while typing and write to the URL debounced.
function useDebouncedParam(value, onChange) {
  const [text, setText] = useState(value);
  const [shown, setShown] = useState(value);
  const debounced = useDebounce(text);
  // Take over values set from outside, but not the trimmed echo of what is
  // being typed: "drone " would lose its space before the next word.
  if (value !== shown) {
    setShown(value);
    if (value !== text.trim()) setText(value);
  }
  useEffect(() => {
    if (debounced !== value) onChange(debounced);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debounced]);
  return [text, setText];
}

export default function Patents() {
  useTitle("Patents");
  const [params, update] = useQueryParams(DEFAULTS);
  const { selected: dataset, datasets, loaded } = useDatasets();
  const page = Number(params.page) || 1;
  const [search, setSearch] = useDebouncedParam(params.search, (value) => update({ search: value.trim() }));
  const [yearFrom, setYearFrom] = useDebouncedParam(params.year_from, (value) => update({ year_from: value }));
  const [yearTo, setYearTo] = useDebouncedParam(params.year_to, (value) => update({ year_to: value }));

  const searchInput = useRef(null);

  // "/" focuses the search, as on GitHub and Google Patents.
  useEffect(() => {
    function onKey(event) {
      const typing = ["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement?.tagName);
      if (event.key === "/" && !typing) {
        event.preventDefault();
        searchInput.current?.focus();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);
  const { data, error, loading, retry } = useApi(
    () => api.patents({ ...params, dataset, page, page_size: PAGE_SIZE }),
    [params, dataset]
  );

  // The open patent is part of the URL (?patent=<id>), so it can be shared and
  // Back closes it. A patent that is not on the current page is fetched.
  const [searchParams, setSearchParams] = useSearchParams();
  const openId = searchParams.get("patent");
  const listed = data?.results.find((patent) => String(patent.id) === openId);
  const fetched = useApi(
    () => (openId && data && !listed ? api.patent(openId) : Promise.resolve(null)),
    [openId, Boolean(data), Boolean(listed)]
  );
  const openPatent = openId ? listed || fetched.data : null;
  function setOpen(patent) {
    const next = new URLSearchParams(searchParams);
    if (patent) next.set("patent", patent.id);
    else next.delete("patent");
    setSearchParams(next);
  }

  if (loaded && datasets.length === 0) {
    return (
      <section>
        <h1 className="page-title">Patents</h1>
        <EmptyState />
      </section>
    );
  }

  return (
    <section>
      <h1 className="page-title">Patents</h1>
      <p className="page-lead">Search and filter the patents of the selected dataset.</p>

      <div className="toolbar">
        <input
          ref={searchInput}
          type="search"
          className="input search"
          placeholder="Search id, title, assignee or inventor  ( / )"
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

      {params.inventor && (
        <p className="chips">
          <span className="chip">
            Inventor: {params.inventor}
            <button type="button" aria-label="Remove inventor filter" onClick={() => update({ inventor: "" })}>
              ×
            </button>
          </span>
        </p>
      )}

      <ErrorMessage error={error} onRetry={retry} />
      {loading && !data && <p className="muted">Loading…</p>}
      {data && (
        <>
          <div className="result-bar">
            <p className="muted">
              {data.count} patents{params.search && <> matching “{params.search}”</>}
            </p>
            {data.count > 0 && (
              <a className="button" href={api.exportUrl({ ...params, page: undefined, dataset })} download>
                Download CSV
              </a>
            )}
          </div>
          <PatentTable
            patents={data.results}
            ordering={params.ordering}
            onSort={(ordering) => update({ ordering })}
            onSelect={setOpen}
            datasetNames={
              !dataset && datasets.length > 1
                ? Object.fromEntries(datasets.map((item) => [item.id, item.name]))
                : undefined
            }
          />
          <Pagination
            page={page}
            pageSize={PAGE_SIZE}
            count={data.count}
            onChange={(next) => update({ page: String(next) })}
          />
        </>
      )}
      {openPatent && <PatentDetail patent={openPatent} onClose={() => setOpen(null)} />}
    </section>
  );
}
