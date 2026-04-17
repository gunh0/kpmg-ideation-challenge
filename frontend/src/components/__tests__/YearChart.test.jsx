import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import YearChart, { niceMax } from "../YearChart";

const data = [
  { year: 2019, filed: 4, published: 1, granted: 0 },
  { year: 2020, filed: 2, published: 3, granted: 1 },
];

describe("YearChart", () => {
  it("switches between the chart and a table of the same numbers", () => {
    render(<YearChart data={data} />);
    expect(screen.getByRole("img", { name: /per year/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Show table" }));

    expect(screen.queryByRole("img")).not.toBeInTheDocument();
    const row = screen.getByRole("row", { name: /2020/ });
    expect(within(row).getAllByRole("cell").map((cell) => cell.textContent)).toEqual(["2", "3", "1"]);
    expect(screen.getByRole("button", { name: "Show chart" })).toHaveAttribute("aria-pressed", "true");
  });

  it("rounds the axis up to 1, 2, 2.5 or 5 times a power of ten", () => {
    expect([3, 7, 12, 180, 501, 2037].map(niceMax)).toEqual([5, 10, 20, 200, 1000, 2500]);
  });
});
