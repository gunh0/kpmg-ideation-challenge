// 20152 -> "20,152". One locale for all counts, so they read the same everywhere.
export function formatNumber(value) {
  return Number(value).toLocaleString("en-US");
}
