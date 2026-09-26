import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import MostCited from "../MostCited";

describe("MostCited", () => {
  it("lists cited patents with their counts, linked to Google Patents", () => {
    render(
      <MostCited
        patents={[
          { id: 1, patent_id: "US-8948935-B1", title: "Drone delivery", assignee: "Amazon", cited_by: 1200,
            result_link: "https://patents.google.com/patent/US8948935B1/en" },
          { id: 2, patent_id: "US-2-A1", title: "Uncited", cited_by: 0, result_link: "" },
        ]}
      />
    );

    expect(screen.getByRole("link", { name: "Drone delivery" })).toHaveAttribute(
      "href",
      "https://patents.google.com/patent/US8948935B1/en"
    );
    expect(screen.getByText("1,200")).toBeInTheDocument();
    expect(screen.queryByText("Uncited")).not.toBeInTheDocument();
  });

  it("says so when nothing is cited", () => {
    render(<MostCited patents={[]} />);
    expect(screen.getByText(/No citations/)).toBeInTheDocument();
  });
});
