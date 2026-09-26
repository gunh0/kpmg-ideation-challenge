import { NavLink, Outlet } from "react-router";

import TopicPicker from "./TopicPicker";

const links = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/patents", label: "Patents" },
  { to: "/topics", label: "Topics" },
];

export default function Layout() {
  return (
    <div className="shell">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="topbar">
        <div className="topbar-inner">
          <NavLink to="/" className="brand">
            <span className="brand-mark" aria-hidden="true">⚖</span>
            Patent Attorney <span className="brand-dim">Without Borders</span>
          </NavLink>
          <nav className="nav" aria-label="Main">
            {links.map((link) => (
              <NavLink key={link.to} to={link.to} end={link.end} className="nav-link">
                {link.label}
              </NavLink>
            ))}
          </nav>
          <TopicPicker />
        </div>
      </header>
      <main id="main" className="content" tabIndex={-1}>
        <Outlet />
      </main>
      <footer className="footer">
        <p>
          Patent data:{" "}
          <a href="https://console.cloud.google.com/marketplace/product/google_patents_public_datasets/google-patents-public-data">
            Google Patents Public Data
          </a>{" "}
          by IFI CLAIMS Patent Services and Google, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.
          Figures and links: <a href="https://patents.google.com">Google Patents</a>.
        </p>
        <p>
          <a href="https://github.com/gunh0/kpmg-ideation-challenge">Source code</a> · KPMG Ideation Challenge 2020,
          team Jackpop
        </p>
      </footer>
    </div>
  );
}
