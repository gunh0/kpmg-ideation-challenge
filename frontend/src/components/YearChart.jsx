import { useState } from "react";

// Categorical slots 1-3 of the validated palette (light/dark steps in index.css).
export const SERIES = [
  { key: "filed", label: "Filed", color: "var(--series-1)" },
  { key: "published", label: "Published", color: "var(--series-2)" },
  { key: "granted", label: "Granted", color: "var(--series-3)" },
];

// Close to the rendered width, so text keeps its size when the SVG scales.
const WIDTH = 1100;
const HEIGHT = 280;
const PAD = { top: 12, right: 16, bottom: 28, left: 36 };

// Round the axis maximum up to 1, 2, 2.5 or 5 times a power of ten.
export function niceMax(value) {
  if (value <= 5) return 5;
  const power = 10 ** Math.floor(Math.log10(value));
  // 2.5 keeps a peak of 2,100 from being drawn against a 5,000 axis
  const step = [1, 2, 2.5, 5, 10].find((m) => m * power >= value);
  return step * power;
}

// The same numbers for screen readers, copying and exact values.
function YearTable({ data }) {
  return (
    <div className="table-wrap">
      <table className="table">
        <caption className="visually-hidden">Filings, publications and grants per year</caption>
        <thead>
          <tr>
            <th scope="col">Year</th>
            {SERIES.map((series) => (
              <th key={series.key} scope="col" className="numeric">
                {series.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((point) => (
            <tr key={point.year}>
              <th scope="row">{point.year}</th>
              {SERIES.map((series) => (
                <td key={series.key} className="numeric">
                  {point[series.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function YearChart({ data }) {
  const [hover, setHover] = useState(null);
  const [asTable, setAsTable] = useState(false);
  if (!data.length) return <p className="muted">No dated patents in this selection.</p>;

  const max = niceMax(Math.max(...data.flatMap((row) => SERIES.map((s) => row[s.key]))));
  const innerW = WIDTH - PAD.left - PAD.right;
  const innerH = HEIGHT - PAD.top - PAD.bottom;
  const x = (i) => PAD.left + (data.length === 1 ? innerW / 2 : (innerW * i) / (data.length - 1));
  const y = (v) => PAD.top + innerH - (innerH * v) / max;
  // niceMax() returns 5, 10, 20, 25, 50, ... so fifths are whole numbers.
  const ticks = [0, 1, 2, 3, 4, 5].map((i) => (max * i) / 5);
  const labelEvery = Math.ceil(data.length / 12);
  const row = hover === null ? null : data[hover];

  return (
    <div className="chart">
      <div className="chart-head">
        <ul className="legend">
          {SERIES.map((series) => (
            <li key={series.key}>
              <span className="legend-swatch" style={{ background: series.color }} />
              {series.label}
            </li>
          ))}
        </ul>
        <button type="button" className="link-button" aria-pressed={asTable} onClick={() => setAsTable(!asTable)}>
          {asTable ? "Show chart" : "Show table"}
        </button>
      </div>
      {asTable ? (
        <YearTable data={data} />
      ) : (
        <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label="Filings, publications and grants per year">
          {ticks.map((tick) => (
            <g key={tick}>
              <line x1={PAD.left} x2={WIDTH - PAD.right} y1={y(tick)} y2={y(tick)} className="grid" />
              <text x={PAD.left - 8} y={y(tick) + 4} textAnchor="end" className="axis">
                {tick}
              </text>
            </g>
          ))}
          {data.map((point, i) =>
            i % labelEvery === 0 ? (
              <text key={point.year} x={x(i)} y={HEIGHT - 8} textAnchor="middle" className="axis">
                {point.year}
              </text>
            ) : null,
          )}
          {hover !== null && (
            <line x1={x(hover)} x2={x(hover)} y1={PAD.top} y2={PAD.top + innerH} className="crosshair" />
          )}
          {SERIES.map((series) => (
            <g key={series.key}>
              <polyline
                fill="none"
                style={{ stroke: series.color }}
                strokeWidth="2"
                points={data.map((point, i) => `${x(i)},${y(point[series.key])}`).join(" ")}
              />
              {data.map((point, i) => (
                <circle
                  key={point.year}
                  cx={x(i)}
                  cy={y(point[series.key])}
                  r={hover === i ? 4.5 : 3}
                  style={{ fill: series.color }}
                />
              ))}
            </g>
          ))}
          {data.map((point, i) => (
            <rect
              key={point.year}
              x={x(i) - innerW / Math.max(data.length - 1, 1) / 2}
              y={PAD.top}
              width={innerW / Math.max(data.length - 1, 1)}
              height={innerH}
              fill="transparent"
              onMouseEnter={() => setHover(i)}
              onMouseLeave={() => setHover(null)}
            />
          ))}
        </svg>
      )}
      {!asTable && row && (
        <div className="tooltip" role="status">
          <strong>{row.year}</strong>
          {SERIES.map((series) => (
            <span key={series.key}>
              <span className="legend-swatch" style={{ background: series.color }} />
              {series.label} {row[series.key]}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
