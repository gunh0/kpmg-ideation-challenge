import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../../api";
import { DatasetProvider } from "../../DatasetContext";
import Profile from "../Profile";

const stats = {
  total: 2,
  granted: 1,
  by_year: [
    { year: 2019, filed: 1, published: 1, granted: 0 },
    { year: 2021, filed: 1, published: 1, granted: 1 },
  ],
  top_assignees: [{ name: "Example Robotics Inc.", count: 2, granted: 1 }],
  top_inventors: [
    { name: "John Roe", count: 2 },
    { name: "Jane Doe", count: 1 },
  ],
};
const latest = {
  count: 1,
  results: [
    {
      id: 1,
      dataset: 1,
      patent_id: "ZZ-0000001-B2",
      title: "Parcel release mechanism",
      assignee: "Example Robotics Inc.",
      inventors: ["Jane Doe", "John Roe"],
      publication_date: "2021-08-20",
      grant_date: "2021-08-20",
      is_granted: true,
    },
  ],
};

function renderAt(path) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <DatasetProvider>
        <Routes>
          <Route path="/assignees/:name" element={<Profile kind="assignee" />} />
          <Route path="/inventors/:name" element={<Profile kind="inventor" />} />
        </Routes>
      </DatasetProvider>
    </MemoryRouter>
  );
}

beforeEach(() => {
  vi.spyOn(api, "datasets").mockResolvedValue([{ id: 1, name: "Drones", patent_count: 2 }]);
  vi.spyOn(api, "patents").mockResolvedValue(latest);
});

afterEach(() => {
  vi.restoreAllMocks();
  window.localStorage.clear();
});

describe("Profile", () => {
  it("shows an assignee's activity and inventors", async () => {
    vi.spyOn(api, "stats").mockResolvedValue(stats);

    renderAt("/assignees/Example%20Robotics%20Inc.");

    expect(await screen.findByRole("heading", { name: "Example Robotics Inc." })).toBeInTheDocument();
    expect(await screen.findByText("2019–2021")).toBeInTheDocument();
    expect(screen.getByText("50% of all")).toBeInTheDocument();
    expect(api.stats).toHaveBeenCalledWith({ assignee: "Example Robotics Inc.", dataset: "" });
    expect(screen.getByRole("link", { name: "Jane Doe" })).toHaveAttribute("href", "/inventors/Jane%20Doe");
    expect(await screen.findByText("Parcel release mechanism")).toBeInTheDocument();
  });

  it("leaves an inventor out of their own co-inventors", async () => {
    vi.spyOn(api, "stats").mockResolvedValue(stats);

    renderAt("/inventors/John%20Roe");

    expect(await screen.findByRole("heading", { name: "Co-inventors" })).toBeInTheDocument();
    expect(api.stats).toHaveBeenCalledWith({ inventor: "John Roe", dataset: "" });
    expect(screen.getByRole("link", { name: "Jane Doe" })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "John Roe" })).not.toBeInTheDocument();
    // in the assignee ranking and in the latest publications
    for (const link of screen.getAllByRole("link", { name: "Example Robotics Inc." })) {
      expect(link).toHaveAttribute("href", "/assignees/Example%20Robotics%20Inc.");
    }
  });

  it("says so when the name has no patents in the dataset", async () => {
    vi.spyOn(api, "stats").mockResolvedValue({ ...stats, total: 0, granted: 0, by_year: [] });

    renderAt("/assignees/Nobody");

    expect(await screen.findByText(/no patents of this assignee/i)).toBeInTheDocument();
  });
});
