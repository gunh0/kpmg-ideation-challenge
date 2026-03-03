import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { afterEach, describe, expect, it, vi } from "vitest";

import { api } from "../../api";
import { DatasetProvider } from "../../DatasetContext";
import Layout from "../Layout";

afterEach(() => vi.restoreAllMocks());

describe("Layout", () => {
  it("credits the patent data on every page", () => {
    vi.spyOn(api, "datasets").mockResolvedValue([]);
    render(
      <MemoryRouter>
        <DatasetProvider>
          <Layout />
        </DatasetProvider>
      </MemoryRouter>
    );

    const footer = screen.getByRole("contentinfo");
    expect(footer).toHaveTextContent("Google Patents Public Data by IFI CLAIMS Patent Services and Google, CC BY 4.0");
    expect(screen.getByRole("link", { name: "Topics" })).toHaveAttribute("href", "/topics");
  });
});
