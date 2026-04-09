import { afterEach, describe, expect, it, vi } from "vitest";

import { api, errorMessage, toQuery } from "./api";

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

describe("request errors", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("marks a proxy answering for a stopped backend as unreachable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response("", { status: 502 })));

    await expect(api.topics()).rejects.toMatchObject({ status: 502, unreachable: true });
  });

  it("keeps the API's own errors", async () => {
    const body = JSON.stringify({ keywords: ["Give at least one keyword."] });
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(body, { status: 400 })));

    await expect(api.createTopic({})).rejects.toMatchObject({
      message: "Give at least one keyword.",
      unreachable: false,
    });
  });
});
