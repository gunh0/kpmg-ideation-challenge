import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import PatentDetail from "../PatentDetail";
import PatentTable from "../PatentTable";

const patent = {
  id: 1,
  patent_id: "ZZ-0000001-B2",
  title: "Parcel release mechanism",
  assignee: "Example Robotics Inc.",
  inventors: ["Jane Doe", "John Roe"],
  priority_date: "2016-03-14",
  filing_date: "2017-03-10",
  publication_date: "2019-08-20",
  grant_date: "2019-08-20",
  is_granted: true,
  result_link: "https://patents.google.com/patent/ZZ0000001B2/en",
  figure_link: "javascript:alert(1)",
};
const application = { ...patent, id: 2, patent_id: "ZZ-2-A1", assignee: "", is_granted: false, grant_date: null };

describe("PatentTable", () => {
  it("shows one row per patent with its status", () => {
    render(<PatentTable patents={[patent, application]} />);

    const rows = screen.getAllByRole("row").slice(1);
    expect(rows).toHaveLength(2);
    expect(within(rows[0]).getByText("Granted")).toBeInTheDocument();
    expect(within(rows[1]).getByText("Application")).toBeInTheDocument();
    expect(within(rows[1]).getByText("—")).toBeInTheDocument();
  });

  it("sorts through the column headers", () => {
    const onSort = vi.fn();
    render(<PatentTable patents={[patent]} ordering="-publication_date" onSort={onSort} />);

    expect(screen.getByRole("columnheader", { name: /published/i })).toHaveAttribute("aria-sort", "descending");
    fireEvent.click(screen.getByRole("button", { name: /published/i }));
    fireEvent.click(screen.getByRole("button", { name: /title/i }));

    expect(onSort.mock.calls).toEqual([["publication_date"], ["title"]]);
  });

  it("selects a patent by click or Enter", () => {
    const onSelect = vi.fn();
    render(<PatentTable patents={[patent]} onSelect={onSelect} />);

    const row = screen.getByText("Parcel release mechanism").closest("tr");
    fireEvent.click(row);
    fireEvent.keyDown(row, { key: "Enter" });

    expect(onSelect).toHaveBeenCalledTimes(2);
  });
});

describe("PatentDetail", () => {
  it("lists inventors and dates and links to Google Patents", () => {
    render(<PatentDetail patent={patent} onClose={() => {}} />);

    expect(screen.getByRole("dialog", { name: "Parcel release mechanism" })).toBeInTheDocument();
    expect(screen.getByText("Jane Doe, John Roe")).toBeInTheDocument();
    expect(screen.getByText("2016-03-14")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /open in google patents/i })).toHaveAttribute("href", patent.result_link);
  });

  it("does not render unsafe figure links", () => {
    render(<PatentDetail patent={patent} onClose={() => {}} />);

    expect(screen.queryByRole("img")).not.toBeInTheDocument();
  });

  it("closes with Escape and the close button", () => {
    const onClose = vi.fn();
    render(<PatentDetail patent={patent} onClose={onClose} />);

    fireEvent.keyDown(window, { key: "Escape" });
    fireEvent.click(screen.getByRole("button", { name: "Close" }));

    expect(onClose).toHaveBeenCalledTimes(2);
  });
});
