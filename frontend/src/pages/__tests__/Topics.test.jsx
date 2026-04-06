import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../../api";
import { TopicProvider, useTopics } from "../../TopicContext";
import Topics from "../Topics";

const topics = [
  {
    id: 1,
    slug: "drones",
    name: "Drones",
    description: "Unmanned aerial vehicles.",
    keywords: ["drone", "uav"],
    pattern: "\\bdrones?\\b",
    status: "ready",
    progress: 0,
    progress_total: 0,
    error: "",
    source_revision: "4b67cee3bc34ec78f7d2173c227b6c827d038f20",
    collected_at: "2026-02-01T02:17:00Z",
    patent_count: 7431,
  },
];

function Where() {
  const location = useLocation();
  const { selected } = useTopics();
  return (
    <output data-testid="where">
      {location.pathname} {selected}
    </output>
  );
}

beforeEach(() => {
  vi.spyOn(api, "topics").mockResolvedValue(topics);
  vi.spyOn(api, "config").mockResolvedValue({ topic_edits: true, max_topics: 20 });
});

afterEach(() => {
  vi.restoreAllMocks();
  window.localStorage.clear();
});

describe("Topics", () => {
  it("describes each topic and credits the source", async () => {
    render(
      <MemoryRouter>
        <TopicProvider>
          <Topics />
        </TopicProvider>
      </MemoryRouter>
    );

    const card = (await screen.findByRole("heading", { name: "Drones" })).closest("article");
    expect(within(card).getByText("7,431")).toBeInTheDocument();
    expect(within(within(card).getByLabelText("Keywords")).getByText("uav")).toBeInTheDocument();
    expect(screen.getByText("4b67cee3bc34")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "CC BY 4.0" })).toHaveAttribute(
      "href",
      "https://creativecommons.org/licenses/by/4.0/"
    );
  });

  it("adds a topic and shows the API's objections next to the fields", async () => {
    const create = vi
      .spyOn(api, "createTopic")
      .mockRejectedValueOnce(Object.assign(new Error("Bad request"), { body: { keywords: ["“dr.ne”: use letters"] } }))
      .mockResolvedValueOnce({ id: 2 });
    render(
      <MemoryRouter>
        <TopicProvider>
          <Topics />
        </TopicProvider>
      </MemoryRouter>
    );

    fireEvent.click(await screen.findByRole("button", { name: "Add a topic" }));
    fireEvent.change(screen.getByRole("textbox", { name: "Name" }), { target: { value: "Lockers" } });
    fireEvent.change(screen.getByRole("textbox", { name: /^Keywords/ }), { target: { value: "dr.ne" } });
    fireEvent.click(screen.getByRole("button", { name: "Add topic" }));
    expect(await screen.findByText("“dr.ne”: use letters")).toBeInTheDocument();

    fireEvent.change(screen.getByRole("textbox", { name: /^Keywords/ }), { target: { value: "locker, parcel box" } });
    fireEvent.click(screen.getByRole("button", { name: "Add topic" }));

    await waitFor(() => expect(screen.queryByRole("button", { name: "Add topic" })).not.toBeInTheDocument());
    expect(create).toHaveBeenLastCalledWith({ name: "Lockers", keywords: "locker, parcel box", description: "" });
  });

  it("edits and deletes a topic", async () => {
    const update = vi.spyOn(api, "updateTopic").mockResolvedValue({});
    const remove = vi.spyOn(api, "deleteTopic").mockResolvedValue(null);
    vi.spyOn(window, "confirm").mockReturnValue(true);
    render(
      <MemoryRouter>
        <TopicProvider>
          <Topics />
        </TopicProvider>
      </MemoryRouter>
    );

    fireEvent.click(await screen.findByRole("button", { name: "Edit" }));
    expect(screen.getByRole("textbox", { name: /^Keywords/ })).toHaveValue("drone, uav");
    fireEvent.change(screen.getByRole("textbox", { name: /^Keywords/ }), { target: { value: "drone, uav, quadcopter" } });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    await waitFor(() =>
      expect(update).toHaveBeenCalledWith(1, expect.objectContaining({ keywords: "drone, uav, quadcopter" }))
    );

    fireEvent.click(await screen.findByRole("button", { name: "Delete" }));
    await waitFor(() => expect(remove).toHaveBeenCalledWith(1));
    expect(window.confirm).toHaveBeenCalledWith(expect.stringContaining("Delete “Drones”"));
  });

  it("shows the progress of a collection and retries a failed one", async () => {
    api.topics.mockResolvedValue([
      { ...topics[0], status: "collecting", progress: 28, progress_total: 112 },
      { ...topics[0], id: 2, name: "Lockers", slug: "lockers", status: "failed", error: "HTTP 503" },
    ]);
    const collect = vi.spyOn(api, "collectTopic").mockResolvedValue({});
    render(
      <MemoryRouter>
        <TopicProvider>
          <Topics />
        </TopicProvider>
      </MemoryRouter>
    );

    expect(await screen.findByRole("progressbar", { name: "Collecting Drones" })).toHaveAttribute("aria-valuenow", "25");
    expect(screen.getByText(/Collection failed: HTTP 503/)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Try again" }));
    await waitFor(() => expect(collect).toHaveBeenCalledWith(2));
  });

  it("hides editing where the instance does not allow it", async () => {
    api.config.mockResolvedValue({ topic_edits: false, max_topics: 20 });
    render(
      <MemoryRouter>
        <TopicProvider>
          <Topics />
        </TopicProvider>
      </MemoryRouter>
    );

    await screen.findByRole("heading", { name: "Drones" });
    expect(screen.queryByRole("button", { name: "Add a topic" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Delete" })).not.toBeInTheDocument();
  });

  it("opens the dashboard of a topic", async () => {
    render(
      <MemoryRouter initialEntries={["/topics"]}>
        <TopicProvider>
          <Routes>
            <Route path="/topics" element={<Topics />} />
            <Route path="/" element={<p>dashboard</p>} />
          </Routes>
          <Where />
        </TopicProvider>
      </MemoryRouter>
    );

    fireEvent.click(await screen.findByRole("button", { name: "Dashboard" }));

    expect(screen.getByTestId("where")).toHaveTextContent("/ 1");
  });
});
