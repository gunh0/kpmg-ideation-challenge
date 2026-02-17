// Thin client for the Django API. In development Vite proxies /api to :8000,
// in Docker nginx does, so relative URLs work everywhere.

export class ApiError extends Error {
  constructor(message, status, body) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

export function toQuery(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") query.set(key, value);
  });
  const text = query.toString();
  return text ? `?${text}` : "";
}

async function request(path, options = {}) {
  const response = await fetch(`/api/${path}`, {
    headers: { Accept: "application/json" },
    ...options,
  });
  if (response.status === 204) return null;
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiError(errorMessage(body) || `Request failed (${response.status})`, response.status, body);
  }
  return body;
}

// DRF errors look like {"detail": "..."} or {"field": ["..."]}.
export function errorMessage(body) {
  if (!body || typeof body !== "object") return "";
  if (typeof body.detail === "string") return body.detail;
  return Object.values(body).flat().filter((value) => typeof value === "string").join(" ");
}

export const api = {
  datasets: () => request("datasets/"),
  patents: (params) => request(`patents/${toQuery(params)}`),
  patent: (id) => request(`patents/${id}/`),
  stats: (params) => request(`stats/${toQuery(params)}`),
  assignees: (params) => request(`assignees/${toQuery(params)}`),
  exportUrl: (params) => `/api/patents/export/${toQuery(params)}`,
};
