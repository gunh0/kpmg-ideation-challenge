import { useEffect, useState } from "react";

import { api } from "../api";

const MAX_ROUNDS = 5;

// Representative figures of the given patents, {id: {thumbnail, figure}}.
// Known figures come with the patents; the others are asked for in one
// request, and again for those the backend had no time to look up yet.
export default function useFigures(patents) {
  const [found, setFound] = useState({});
  const key = (patents || []).map((patent) => patent.id).join(",");

  useEffect(() => {
    let current = true;
    const missing = (patents || []).filter((patent) => !patent.thumbnail_link).map((patent) => patent.id);

    async function lookUp(ids, round) {
      if (!ids.length || round >= MAX_ROUNDS) return;
      const rows = await api.figures(ids).catch(() => []);
      if (!current) return;
      setFound((previous) => {
        const next = { ...previous };
        rows.filter((row) => row.checked).forEach((row) => (next[row.id] = row));
        return next;
      });
      const unchecked = rows.filter((row) => !row.checked).map((row) => row.id);
      if (unchecked.length < ids.length) await lookUp(unchecked, round + 1);
    }

    lookUp(missing, 0);
    return () => {
      current = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  const figures = {};
  (patents || []).forEach((patent) => {
    figures[patent.id] = patent.thumbnail_link
      ? { thumbnail: patent.thumbnail_link, figure: patent.figure_link }
      : found[patent.id] || null;
  });
  return figures;
}
