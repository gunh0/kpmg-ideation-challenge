import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../../api";
import { DatasetProvider } from "../../DatasetContext";
import Patents from "../Patents";

const patent = {
  id: 1,
  dataset: 1,
  patent_id: "ZZ-0000001-B2",
  title: "Parcel release mechanism",
  assignee: "Example Robotics Inc.",
  inventors: ["Jane Doe"],
  publication_date: "2021-08-20",
  grant_date: "2021-08-20",
  is_granted: true,
  result_link: "",
  figure_link: "",
};

function Location() {
  const location = useLocation();
  return <output data-testid="location">{location.search}</output>;
}

function renderAt(path) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <DatasetProvider>
        <Routes>
          <Route path="/patents" element={<Patents />} />
        </Routes>
        <Location />
      </DatasetProvider>
    </MemoryRouter>
  );
}

beforeEach(() => {
  vi.spyOn(api, "config").mockResolvedValue({ read_only: false });
  vi.spyOn(api, "datasets").mockResolvedValue([{ id: 1, name: "Drones", search_url: "", patent_count: 1 }]);
  vi.spyOn(api, "assignees").mockResolvedValue([]);
  vi.spyOn(api, "patents").mockResolvedValue({ count: 1, results: [patent] });
});

afterEach(() => {
  vi.restoreAllMocks();
  window.localStorage.clear();
});

describe("Patents", () => {
  it("keeps the open patent in the URL", async () => {
    renderAt("/patents");

    fireEvent.click(await screen.findByText("Parcel release mechanism"));

    expect(screen.getByRole("dialog", { name: "Parcel release mechanism" })).toBeInTheDocument();
    expect(screen.getByTestId("location")).toHaveTextContent("?patent=1");
    fireEvent.click(screen.getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("keeps a trailing space while typing a search", async () => {
    renderAt("/patents");
    const box = await screen.findByRole("searchbox", { name: "Search patents" });

    fireEvent.change(box, { target: { value: "parcel " } });

    await waitFor(() => expect(screen.getByTestId("location")).toHaveTextContent("?search=parcel"));
    expect(box).toHaveValue("parcel ");
  });

  it("clears all filters at once", async () => {
    renderAt("/patents?search=parcel&granted=true&year_from=2019&ordering=title");

    fireEvent.click(await screen.findByRole("button", { name: "Clear filters" }));

    expect(screen.getByTestId("location")).toHaveTextContent(/^\?ordering=title$/);
    expect(screen.getByRole("searchbox", { name: "Search patents" })).toHaveValue("");
    expect(screen.queryByRole("button", { name: "Clear filters" })).not.toBeInTheDocument();
  });

  it("opens a shared link to a patent that is not on the page", async () => {
    const other = { ...patent, id: 9, title: "Landing pad for parcel drones" };
    vi.spyOn(api, "patent").mockResolvedValue(other);

    renderAt("/patents?patent=9");

    expect(await screen.findByRole("dialog", { name: "Landing pad for parcel drones" })).toBeInTheDocument();
    expect(api.patent).toHaveBeenCalledWith("9");
  });
});
