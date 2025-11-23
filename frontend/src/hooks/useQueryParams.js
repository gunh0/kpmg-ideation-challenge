import { useCallback, useMemo } from "react";
import { useSearchParams } from "react-router";

// Filter state kept in the URL so views can be bookmarked, shared and reached
// from other pages. Changing any filter other than "page" returns to page 1.
export default function useQueryParams(defaults) {
  const [searchParams, setSearchParams] = useSearchParams();

  const params = useMemo(() => {
    const values = { ...defaults };
    Object.keys(defaults).forEach((key) => {
      if (searchParams.has(key)) values[key] = searchParams.get(key);
    });
    return values;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const update = useCallback(
    (changes) => {
      const next = new URLSearchParams(searchParams);
      Object.entries(changes).forEach(([key, value]) => {
        if (value === "" || value === null || value === undefined || value === defaults[key]) next.delete(key);
        else next.set(key, value);
      });
      if (!("page" in changes)) next.delete("page");
      setSearchParams(next, { replace: true });
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [searchParams, setSearchParams]
  );

  return [params, update];
}
