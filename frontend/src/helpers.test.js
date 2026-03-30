import { describe, expect, it } from "vitest";

import { nextOrdering, parseOrdering } from "./components/PatentTable";
import { niceMax } from "./components/YearChart";
import { countryName, formatNumber } from "./format";
import { safeUrl } from "./links";

describe("safeUrl", () => {
  it("keeps http and https links", () => {
    expect(safeUrl("https://patents.google.com/patent/US1/en")).toBe("https://patents.google.com/patent/US1/en");
    expect(safeUrl("http://example.org/a.png")).toBe("http://example.org/a.png");
  });

  it("rejects script and other schemes", () => {
    expect(safeUrl("javascript:alert(1)")).toBeNull();
    expect(safeUrl("data:text/html,<b>x</b>")).toBeNull();
    expect(safeUrl("")).toBeNull();
    expect(safeUrl("not a url")).toBeNull();
  });
});

describe("ordering", () => {
  it("parses the direction", () => {
    expect(parseOrdering("-publication_date")).toEqual({ field: "publication_date", descending: true });
    expect(parseOrdering("title")).toEqual({ field: "title", descending: false });
  });

  it("sorts a new column ascending, then toggles", () => {
    expect(nextOrdering("-publication_date", "title")).toBe("title");
    expect(nextOrdering("title", "title")).toBe("-title");
    expect(nextOrdering("-title", "title")).toBe("title");
  });
});

describe("niceMax", () => {
  it("rounds up to 5, 10, 20, 50 ...", () => {
    expect(niceMax(0)).toBe(5);
    expect(niceMax(3)).toBe(5);
    expect(niceMax(7)).toBe(10);
    expect(niceMax(11)).toBe(20);
    expect(niceMax(21)).toBe(50);
    expect(niceMax(120)).toBe(200);
  });
});

describe("formatNumber", () => {
  it("groups thousands", () => {
    expect(formatNumber(20152)).toBe("20,152");
    expect(formatNumber(7)).toBe("7");
  });
});

describe("countryName", () => {
  it("names regions and keeps unknown codes", () => {
    expect(countryName("KR")).toBe("South Korea");
    expect(countryName("us")).toBe("United States");
    expect(countryName("")).toBe("—");
  });
});
