import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../../api";
import { TopicProvider, useTopics } from "../../TopicContext";
import TopicPicker, { pickerLabel } from "../TopicPicker";

const topics = [
  { id: 1, name: "Drones", patent_count: 7431 },
  { id: 2, name: "Autonomous driving", patent_count: 8648 },
  { id: 3, name: "Cybersecurity", patent_count: 4073 },
];

function Selection() {
  const { topicsParam } = useTopics();
  return <output data-testid="selection">{topicsParam || "all"}</output>;
}

beforeEach(() => vi.spyOn(api, "topics").mockResolvedValue(topics));
afterEach(() => {
  vi.restoreAllMocks();
  window.localStorage.clear();
});

describe("TopicPicker", () => {
  it("selects several topics and back to all", async () => {
    render(
      <TopicProvider>
        <TopicPicker />
        <Selection />
      </TopicProvider>
    );

    fireEvent.click(await screen.findByRole("button", { name: "All topics" }));
    fireEvent.click(await screen.findByRole("checkbox", { name: /Drones/ }));
    fireEvent.click(screen.getByRole("checkbox", { name: /Cybersecurity/ }));

    expect(screen.getByTestId("selection")).toHaveTextContent("1,3");
    expect(screen.getByRole("button", { name: "Drones + Cybersecurity" })).toHaveAttribute("aria-expanded", "true");
    expect(JSON.parse(window.localStorage.getItem("selected-topics"))).toEqual(["1", "3"]);

    fireEvent.click(screen.getByRole("checkbox", { name: "All topics" }));
    expect(screen.getByTestId("selection")).toHaveTextContent("all");

    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.queryByRole("checkbox")).not.toBeInTheDocument();
  });

  it("forgets topics that were deleted", async () => {
    window.localStorage.setItem("selected-topics", JSON.stringify(["1", "9"]));
    render(
      <TopicProvider>
        <Selection />
      </TopicProvider>
    );

    expect(await screen.findByText("1")).toBeInTheDocument();
  });

  it("names the selection shortly", () => {
    expect(pickerLabel(topics, [])).toBe("All topics");
    expect(pickerLabel(topics, ["2"])).toBe("Autonomous driving");
    expect(pickerLabel(topics, ["1", "2", "3"])).toBe("3 topics");
  });
});
