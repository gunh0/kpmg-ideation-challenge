import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../../api";
import { DatasetProvider } from "../../DatasetContext";
import Dashboard from "../Dashboard";

const stats = {
  total: 3,
  granted: 2,
  by_year: [
    { year: 2019, filed: 1, published: 1, granted: 1 },
    { year: 2020, filed: 0, published: 2, granted: 1 },
  ],
  top_assignees: [{ name: "Example Robotics Inc.", count: 2, granted: 2 }],
  top_inventors: [{ name: "John Roe", count: 2 }],
};

function renderDashboard() {
  return render(
    <MemoryRouter>
      <DatasetProvider>
        <Dashboard />
      </DatasetProvider>
    </MemoryRouter>
  );
}

beforeEach(() => {
  vi.spyOn(api, "config").mockResolvedValue({ read_only: false });
});

afterEach(() => {
  vi.restoreAllMocks();
  window.localStorage.clear();
});

describe("Dashboard", () => {
  it("summarises the selection and links rankings to their pages", async () => {
    vi.spyOn(api, "datasets").mockResolvedValue([{ id: 1, name: "Drones", search_url: "", patent_count: 3 }]);
    vi.spyOn(api, "stats").mockResolvedValue(stats);

    renderDashboard();

    expect(await screen.findByText("67% of all")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /per year/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Example Robotics Inc." })).toHaveAttribute(
      "href",
      "/assignees/Example%20Robotics%20Inc."
    );
    expect(screen.getByRole("link", { name: "John Roe" })).toHaveAttribute("href", "/inventors/John%20Roe");
    expect(screen.getByText("100% granted")).toBeInTheDocument();
  });

  it("asks to import data when there is none", async () => {
    vi.spyOn(api, "datasets").mockResolvedValue([]);
    vi.spyOn(api, "stats").mockResolvedValue({ ...stats, total: 0 });

    renderDashboard();

    expect(await screen.findByText("No patents yet")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Import a dataset" })).toHaveAttribute("href", "/datasets");
  });

  it("offers a retry when the API fails", async () => {
    vi.spyOn(api, "datasets").mockResolvedValue([{ id: 1, name: "Drones", search_url: "", patent_count: 3 }]);
    vi.spyOn(api, "stats").mockRejectedValue(new TypeError("Failed to fetch"));

    renderDashboard();

    expect(await screen.findByText(/api is not reachable/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument();
  });
});
