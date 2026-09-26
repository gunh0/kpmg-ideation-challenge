// 20152 -> "20,152". One locale for all counts, so they read the same everywhere.
export function formatNumber(value) {
  return Number(value).toLocaleString("en-US");
}

const REGIONS = typeof Intl.DisplayNames === "function" ? new Intl.DisplayNames(["en"], { type: "region" }) : null;

// "KR" -> "South Korea"; the code itself when the name is unknown.
export function countryName(code) {
  if (!code) return "—";
  try {
    return REGIONS?.of(code.toUpperCase()) || code;
  } catch {
    return code;
  }
}
