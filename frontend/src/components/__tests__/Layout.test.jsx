import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { afterEach, describe, expect, it, vi } from "vitest";

import { api } from "../../api";
import { TopicProvider } from "../../TopicContext";
import Layout from "../Layout";

afterEach(() => vi.restoreAllMocks());

describe("Layout", () => {
  it("credits the patent data on every page", () => {
    vi.spyOn(api, "topics").mockResolvedValue([]);
    render(
      <MemoryRouter>
        <TopicProvider>
          <Layout />
        </TopicProvider>
      </MemoryRouter>
    );

    const footer = screen.getByRole("contentinfo");
    expect(footer).toHaveTextContent("Google Patents Public Data by IFI CLAIMS Patent Services and Google, CC BY 4.0");
    expect(screen.getByRole("link", { name: "Topics" })).toHaveAttribute("href", "/topics");
  });
});
