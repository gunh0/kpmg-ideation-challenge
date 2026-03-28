import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../../api";
import { TopicProvider } from "../../TopicContext";
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
  top_countries: [],
  by_topic: [],
};

function renderDashboard() {
  return render(
    <MemoryRouter>
      <TopicProvider>
        <Dashboard />
      </TopicProvider>
    </MemoryRouter>
  );
}

beforeEach(() => {
});

afterEach(() => {
  vi.restoreAllMocks();
  window.localStorage.clear();
});

describe("Dashboard", () => {
  it("summarises the selection and links rankings to their pages", async () => {
    vi.spyOn(api, "patents").mockResolvedValue({ count: 0, results: [] });
    vi.spyOn(api, "topics").mockResolvedValue([{ id: 1, name: "Drones", patent_count: 3 }]);
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

  it("shows the latest patents with their figures, linked to Google Patents", async () => {
    vi.spyOn(api, "topics").mockResolvedValue([{ id: 1, name: "Drones", patent_count: 3 }]);
    vi.spyOn(api, "stats").mockResolvedValue(stats);
    vi.spyOn(api, "patents").mockResolvedValue({
      count: 1,
      results: [
        {
          id: 7,
          patent_id: "US-12351339-B2",
          title: "Drone landing gear",
          assignee: "Example Robotics Inc.",
          publication_date: "2025-07-08",
          result_link: "https://patents.google.com/patent/US12351339B2/en",
          thumbnail_link: "https://patentimages.storage.googleapis.com/t.png",
        },
      ],
    });

    renderDashboard();

    const card = await screen.findByRole("link", { name: /Drone landing gear/ });
    expect(card).toHaveAttribute("href", "https://patents.google.com/patent/US12351339B2/en");
    expect(card.querySelector("img")).toHaveAttribute("src", "https://patentimages.storage.googleapis.com/t.png");
    expect(api.patents).toHaveBeenCalledWith(expect.objectContaining({ has_figure: true, page_size: 8 }));
  });

  it("explains where the data comes from when there is none", async () => {
    vi.spyOn(api, "topics").mockResolvedValue([]);
    vi.spyOn(api, "stats").mockResolvedValue({ ...stats, total: 0 });

    renderDashboard();

    expect(await screen.findByText("No patents yet")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "About the topics" })).toHaveAttribute("href", "/topics");
  });

  it("offers a retry when the API fails", async () => {
    vi.spyOn(api, "topics").mockResolvedValue([{ id: 1, name: "Drones", patent_count: 3 }]);
    vi.spyOn(api, "stats").mockRejectedValue(new TypeError("Failed to fetch"));

    renderDashboard();

    expect(await screen.findByText(/api is not reachable/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument();
  });
});
