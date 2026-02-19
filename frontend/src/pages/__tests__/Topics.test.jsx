import { fireEvent, render, screen, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../../api";
import { DatasetProvider, useDatasets } from "../../DatasetContext";
import Topics from "../Topics";

const topics = [
  {
    id: 1,
    slug: "drones",
    name: "Drones",
    description: "Unmanned aerial vehicles.",
    pattern: "\\bdrones?\\b",
    source_revision: "4b67cee3bc34ec78f7d2173c227b6c827d038f20",
    collected_at: "2026-02-01T02:17:00Z",
    patent_count: 7431,
  },
];

function Where() {
  const location = useLocation();
  const { selected } = useDatasets();
  return (
    <output data-testid="where">
      {location.pathname} {selected}
    </output>
  );
}

beforeEach(() => {
  vi.spyOn(api, "datasets").mockResolvedValue(topics);
});

afterEach(() => {
  vi.restoreAllMocks();
  window.localStorage.clear();
});

describe("Topics", () => {
  it("describes each topic and credits the source", async () => {
    render(
      <MemoryRouter>
        <DatasetProvider>
          <Topics />
        </DatasetProvider>
      </MemoryRouter>
    );

    const card = (await screen.findByRole("heading", { name: "Drones" })).closest("article");
    expect(within(card).getByText("7,431")).toBeInTheDocument();
    expect(within(card).getByText("\\bdrones?\\b")).toBeInTheDocument();
    expect(screen.getByText("4b67cee3bc34")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "CC BY 4.0" })).toHaveAttribute(
      "href",
      "https://creativecommons.org/licenses/by/4.0/"
    );
  });

  it("opens the dashboard of a topic", async () => {
    render(
      <MemoryRouter initialEntries={["/topics"]}>
        <DatasetProvider>
          <Routes>
            <Route path="/topics" element={<Topics />} />
            <Route path="/" element={<p>dashboard</p>} />
          </Routes>
          <Where />
        </DatasetProvider>
      </MemoryRouter>
    );

    fireEvent.click(await screen.findByRole("button", { name: "Dashboard" }));

    expect(screen.getByTestId("where")).toHaveTextContent("/ 1");
  });
});
