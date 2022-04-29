import { describe, expect, it } from "vitest";

import { errorMessage, toQuery } from "./api";

describe("toQuery", () => {
  it("skips empty values", () => {
    expect(toQuery({ search: "drone", assignee: "", granted: null, page: 2 })).toBe("?search=drone&page=2");
  });

  it("returns an empty string without parameters", () => {
    expect(toQuery()).toBe("");
    expect(toQuery({ search: "" })).toBe("");
  });

  it("encodes values", () => {
    expect(toQuery({ assignee: "Example Robotics Inc." })).toBe("?assignee=Example+Robotics+Inc.");
  });
});

describe("errorMessage", () => {
  it("reads DRF detail and field errors", () => {
    expect(errorMessage({ detail: "Not found." })).toBe("Not found.");
    expect(errorMessage({ file: ["The file is not UTF-8 text."] })).toBe("The file is not UTF-8 text.");
  });

  it("ignores bodies without messages", () => {
    expect(errorMessage(null)).toBe("");
    expect(errorMessage("oops")).toBe("");
  });
});
