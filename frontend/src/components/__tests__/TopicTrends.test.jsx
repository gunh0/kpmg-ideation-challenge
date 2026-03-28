import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import TopicTrends, { topicColor } from "../TopicTrends";

const allTopics = [{ id: 7 }, { id: 3 }, { id: 5 }];
const topics = [
  { id: 5, name: "Drones", count: 3, by_year: [{ year: 2020, published: 1 }, { year: 2021, published: 2 }] },
  { id: 3, name: "Lockers", count: 1, by_year: [{ year: 2021, published: 1 }] },
];

describe("TopicTrends", () => {
  it("draws one labelled line per topic", () => {
    render(<TopicTrends topics={topics} allTopics={allTopics} />);

    const chart = screen.getByRole("img", { name: /each topic/ });
    expect(chart.querySelectorAll("polyline")).toHaveLength(2);
    expect(within(chart).getByText("Drones")).toHaveClass("end-label");
  });

  it("shows the same numbers as a table, zero where a topic has none", () => {
    render(<TopicTrends topics={topics} allTopics={allTopics} />);

    fireEvent.click(screen.getByRole("button", { name: "Show table" }));

    const row = screen.getByRole("row", { name: /2020/ });
    expect(within(row).getAllByRole("cell").map((cell) => cell.textContent)).toEqual(["1", "0"]);
  });

  it("gives each topic the colour of its place among all topics, not of its rank", () => {
    expect(topicColor(3, allTopics)).toBe("var(--series-1)");
    expect(topicColor(5, allTopics)).toBe("var(--series-2)");
    // a topic added later (a higher id) takes the next colour, the others keep theirs
    expect(topicColor(5, [...allTopics, { id: 9 }])).toBe("var(--series-2)");
    expect(topicColor(9, [...allTopics, { id: 9 }])).toBe("var(--series-4)");
  });
});
