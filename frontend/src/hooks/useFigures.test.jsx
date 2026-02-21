import { renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { api } from "../api";
import useFigures from "./useFigures";

const known = { id: 1, thumbnail_link: "https://patentimages.storage.googleapis.com/t1.png", figure_link: "f1" };
const unknown = { id: 2, thumbnail_link: "", figure_link: "" };
const slow = { id: 3, thumbnail_link: "", figure_link: "" };

afterEach(() => vi.restoreAllMocks());

describe("useFigures", () => {
  it("uses known figures and asks for the others until they are looked up", async () => {
    vi.spyOn(api, "figures")
      .mockResolvedValueOnce([
        { id: 2, thumbnail: "t2", figure: "f2", checked: true },
        { id: 3, thumbnail: "", figure: "", checked: false },
      ])
      .mockResolvedValueOnce([{ id: 3, thumbnail: "", figure: "", checked: true }]);

    const { result } = renderHook(() => useFigures([known, unknown, slow]));

    expect(result.current[1]).toEqual({ thumbnail: known.thumbnail_link, figure: "f1" });
    await waitFor(() => expect(result.current[2]).toMatchObject({ thumbnail: "t2" }));
    await waitFor(() => expect(result.current[3]).toMatchObject({ thumbnail: "", checked: true }));
    expect(api.figures.mock.calls).toEqual([[[2, 3]], [[3]]]);
  });

  it("does not ask when every figure is known", () => {
    vi.spyOn(api, "figures");

    renderHook(() => useFigures([known]));

    expect(api.figures).not.toHaveBeenCalled();
  });
});
