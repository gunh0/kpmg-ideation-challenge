import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router";

import { api } from "../api";
import { useTopics } from "../TopicContext";
import EmptyState from "../components/EmptyState";
import AssigneeFilter from "../components/AssigneeFilter";
import Pagination from "../components/Pagination";
import PatentDetail from "../components/PatentDetail";
import PatentTable from "../components/PatentTable";
import ErrorMessage from "../components/ErrorMessage";
import useApi from "../hooks/useApi";
import useDebounce from "../hooks/useDebounce";
import useFigures from "../hooks/useFigures";
import useQueryParams from "../hooks/useQueryParams";
import useTitle from "../hooks/useTitle";
import { formatNumber } from "../format";

const PAGE_SIZES = ["25", "50", "100"];
const FILTERS = ["search", "assignee", "inventor", "granted", "year_from", "year_to"];
const DEFAULTS = {
  search: "",
  assignee: "",
  inventor: "",
  granted: "",
  year_from: "",
  year_to: "",
  ordering: "-publication_date",
  page: "1",
  page_size: "25",
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
  const { topicsParam: topics, topics: allTopics, loaded } = useTopics();
  const page = Number(params.page) || 1;
  const pageSize = PAGE_SIZES.includes(params.page_size) ? Number(params.page_size) : 25;
  const [search, setSearch] = useDebouncedParam(params.search, (value) => update({ search: value.trim() }));
  const [yearFrom, setYearFrom] = useDebouncedParam(params.year_from, (value) => update({ year_from: value }));
  const [yearTo, setYearTo] = useDebouncedParam(params.year_to, (value) => update({ year_to: value }));

  const searchInput = useRef(null);
  const filtered = FILTERS.some((key) => params[key]);

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
    () => api.patents({ ...params, topics, page, page_size: pageSize }),
    [params, topics]
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
  const figures = useFigures(data?.results);
  function setOpen(patent) {
    const next = new URLSearchParams(searchParams);
    if (patent) next.set("patent", patent.id);
    else next.delete("patent");
    setSearchParams(next);
  }

  if (loaded && allTopics.length === 0) {
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
      <p className="page-lead">Search and filter the patents of the selected topics.</p>

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
        <AssigneeFilter value={params.assignee} topics={topics} onChange={(value) => update({ assignee: value })} />
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
        {filtered && (
          <button
            type="button"
            className="button"
            onClick={() => update(Object.fromEntries(FILTERS.map((key) => [key, ""])))}
          >
            Clear filters
          </button>
        )}
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
              {formatNumber(data.count)} patents{params.search && <> matching “{params.search}”</>}
            </p>
            <div className="result-actions">
              <label className="muted small">
                Rows{" "}
                <select
                  className="select"
                  value={String(pageSize)}
                  onChange={(event) => update({ page_size: event.target.value })}
                >
                  {PAGE_SIZES.map((size) => (
                    <option key={size}>{size}</option>
                  ))}
                </select>
              </label>
              {data.count > 0 && (
                <a
                  className="button"
                  href={api.exportUrl({ ...params, page: undefined, page_size: undefined, topics })}
                  download
                >
                  Download CSV
                </a>
              )}
            </div>
          </div>
          <PatentTable
            patents={data.results}
            ordering={params.ordering}
            onSort={(ordering) => update({ ordering })}
            onSelect={setOpen}
            figures={figures}
            topicNames={
              allTopics.length > 1 ? Object.fromEntries(allTopics.map((item) => [item.id, item.name])) : undefined
            }
          />
          <Pagination
            page={page}
            pageSize={pageSize}
            count={data.count}
            onChange={(next) => update({ page: String(next) })}
          />
        </>
      )}
      {openPatent && <PatentDetail patent={openPatent} onClose={() => setOpen(null)} />}
    </section>
  );
}
