import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../../api";
import { TopicProvider } from "../../TopicContext";
import Patents from "../Patents";

const patent = {
  id: 1,
  topics: [1],
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
      <TopicProvider>
        <Routes>
          <Route path="/patents" element={<Patents />} />
        </Routes>
        <Location />
      </TopicProvider>
    </MemoryRouter>
  );
}

beforeEach(() => {
  vi.spyOn(api, "topics").mockResolvedValue([{ id: 1, name: "Drones", patent_count: 1 }]);
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

  it("asks for the chosen number of rows and starts again at page 1", async () => {
    renderAt("/patents?page=3");

    fireEvent.change(await screen.findByRole("combobox", { name: "Rows" }), { target: { value: "100" } });

    expect(screen.getByTestId("location")).toHaveTextContent(/^\?page_size=100$/);
    await waitFor(() => expect(api.patents).toHaveBeenLastCalledWith(expect.objectContaining({ page: 1, page_size: 100 })));
  });

  it("ranks by the selected topics that a patent matches", async () => {
    window.localStorage.setItem("selected-topics", JSON.stringify(["1", "2"]));
    vi.spyOn(api, "topics").mockResolvedValue([
      { id: 1, name: "Drones", patent_count: 2 },
      { id: 2, name: "Lockers", patent_count: 1 },
    ]);
    api.patents.mockResolvedValue({ count: 1, results: [{ ...patent, topics: [1, 2], matched: 2 }] });
    renderAt("/patents");

    expect(await screen.findByText("2 of 2")).toBeInTheDocument();
    expect(api.patents).toHaveBeenLastCalledWith(expect.objectContaining({ topics: "1,2", ordering: "-matched,-cited_by" }));

    fireEvent.change(screen.getByRole("combobox", { name: "Topics to match" }), { target: { value: "all" } });
    await waitFor(() => expect(api.patents).toHaveBeenLastCalledWith(expect.objectContaining({ match: "all" })));

    fireEvent.click(screen.getByRole("button", { name: /published/i }));
    await waitFor(() => expect(api.patents).toHaveBeenLastCalledWith(expect.objectContaining({ ordering: "publication_date" })));
  });

  it("opens a shared link to a patent that is not on the page", async () => {
    const other = { ...patent, id: 9, title: "Landing pad for parcel drones" };
    vi.spyOn(api, "patent").mockResolvedValue(other);

    renderAt("/patents?patent=9");

    expect(await screen.findByRole("dialog", { name: "Landing pad for parcel drones" })).toBeInTheDocument();
    expect(api.patent).toHaveBeenCalledWith("9");
  });
});
