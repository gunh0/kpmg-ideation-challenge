import { NavLink, Outlet } from "react-router-dom";

import DatasetPicker from "./DatasetPicker";

const links = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/patents", label: "Patents" },
  { to: "/datasets", label: "Datasets" },
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
          <DatasetPicker />
        </div>
      </header>
      <main id="main" className="content" tabIndex={-1}>
        <Outlet />
      </main>
    </div>
  );
}
