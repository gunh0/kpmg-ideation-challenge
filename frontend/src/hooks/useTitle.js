import { useEffect } from "react";

const APP = "Patent Attorney Without Borders";

export default function useTitle(title) {
  useEffect(() => {
    document.title = title ? `${title} · ${APP}` : APP;
  }, [title]);
}
