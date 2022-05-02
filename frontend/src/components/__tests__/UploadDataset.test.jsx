import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { api, ApiError } from "../../api";
import Pagination from "../Pagination";
import UploadDataset from "../UploadDataset";

afterEach(() => vi.restoreAllMocks());

function chooseFile(name, content = "id,title\n") {
  const file = new File([content], name, { type: "text/csv" });
  fireEvent.change(document.querySelector('input[type="file"]'), { target: { files: [file] } });
  return file;
}

describe("UploadDataset", () => {
  it("uploads the chosen file with the typed name", async () => {
    const result = { id: 3, name: "Drones", import: { imported: 3, duplicates: 0, skipped: 0 } };
    const upload = vi.spyOn(api, "uploadDataset").mockResolvedValue(result);
    const onUploaded = vi.fn();
    render(<UploadDataset onUploaded={onUploaded} />);

    const file = chooseFile("gp-search.csv");
    fireEvent.change(screen.getByLabelText("Dataset name"), { target: { value: " Drones " } });
    fireEvent.click(screen.getByRole("button", { name: "Import" }));

    await waitFor(() => expect(onUploaded).toHaveBeenCalledWith(result));
    expect(upload).toHaveBeenCalledWith(file, "Drones");
  });

  it("refuses non-CSV files before uploading", () => {
    const upload = vi.spyOn(api, "uploadDataset");
    render(<UploadDataset onUploaded={() => {}} />);

    chooseFile("results.xlsx");

    expect(screen.getByText(/choose the \.csv file/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Import" })).toBeDisabled();
    expect(upload).not.toHaveBeenCalled();
  });

  it("shows the error returned by the API", async () => {
    vi.spyOn(api, "uploadDataset").mockRejectedValue(new ApiError("Not a Google Patents export: missing column(s): id.", 400));
    render(<UploadDataset onUploaded={() => {}} />);

    chooseFile("other.csv");
    fireEvent.click(screen.getByRole("button", { name: "Import" }));

    expect(await screen.findByText(/not a google patents export/i)).toBeInTheDocument();
  });
});

describe("Pagination", () => {
  it("is hidden for a single page", () => {
    const { container } = render(<Pagination page={1} pageSize={25} count={10} onChange={() => {}} />);

    expect(container).toBeEmptyDOMElement();
  });

  it("shows the range and moves between pages", () => {
    const onChange = vi.fn();
    render(<Pagination page={2} pageSize={25} count={60} onChange={onChange} />);

    expect(screen.getByText("26–50 of 60 · page 2 of 3")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /previous/i }));
    fireEvent.click(screen.getByRole("button", { name: /next/i }));
    expect(onChange.mock.calls).toEqual([[1], [3]]);
  });
});
