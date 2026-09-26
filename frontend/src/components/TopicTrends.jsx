import { useState } from "react";

import { niceMax } from "./YearChart";

// Colour follows the topic, not its rank: slot by the topic's place among all
// topics (by id), in the fixed order of the validated categorical palette.
export function topicColor(id, allTopics) {
  const order = [...allTopics].map((topic) => topic.id).sort((a, b) => a - b);
  const slot = Math.max(0, order.indexOf(id)) % 8;
  return `var(--series-${slot + 1})`;
}

const WIDTH = 1100;
const HEIGHT = 300;
const PAD = { top: 12, right: 150, bottom: 28, left: 44 };

function trendCells(trends, year) {
  return trends.map((trend) => (
    <td key={trend.id} className="numeric">
      {trend.values[year] || 0}
    </td>
  ));
}

function TrendTable({ trends, years }) {
  return (
    <div className="table-wrap">
      <table className="table">
        <caption className="visually-hidden">Publications per year of each topic</caption>
        <thead>
          <tr>
            <th scope="col">Year</th>
            {trends.map((trend) => (
              <th key={trend.id} scope="col" className="numeric">
                {trend.name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {years.map((year) => (
            <tr key={year}>
              <th scope="row">{year}</th>
              {trendCells(trends, year)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// Publications per year of several topics, one line each, labelled at its end.
export default function TopicTrends({ topics, allTopics }) {
  const [hover, setHover] = useState(null);
  const [asTable, setAsTable] = useState(false);
  const trends = topics.map((topic) => ({
    ...topic,
    color: topicColor(topic.id, allTopics),
    values: Object.fromEntries(topic.by_year.map((row) => [row.year, row.published])),
  }));
  const years = [...new Set(topics.flatMap((topic) => topic.by_year.map((row) => row.year)))].sort((a, b) => a - b);
  if (years.length < 2) return <p className="muted">Not enough years to compare.</p>;

  const max = niceMax(Math.max(...trends.flatMap((trend) => Object.values(trend.values))));
  const innerW = WIDTH - PAD.left - PAD.right;
  const innerH = HEIGHT - PAD.top - PAD.bottom;
  const x = (i) => PAD.left + (innerW * i) / (years.length - 1);
  const y = (v) => PAD.top + innerH - (innerH * v) / max;
  const ticks = [0, 1, 2, 3, 4, 5].map((i) => (max * i) / 5);
  const labelEvery = Math.ceil(years.length / 12);
  // End labels, nudged apart so that close lines keep readable names.
  const ends = trends
    .map((trend) => ({ trend, y: y(trend.values[years[years.length - 1]] || 0) }))
    .sort((a, b) => a.y - b.y);
  ends.forEach((end, i) => {
    if (i > 0 && end.y - ends[i - 1].y < 14) end.y = ends[i - 1].y + 14;
  });

  return (
    <div className="chart">
      <div className="chart-head">
        <ul className="legend">
          {trends.map((trend) => (
            <li key={trend.id}>
              <span className="legend-swatch" style={{ background: trend.color }} />
              {trend.name}
            </li>
          ))}
        </ul>
        <button type="button" className="link-button" aria-pressed={asTable} onClick={() => setAsTable(!asTable)}>
          {asTable ? "Show chart" : "Show table"}
        </button>
      </div>
      {asTable ? (
        <TrendTable trends={trends} years={years} />
      ) : (
        <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label="Publications per year of each topic">
          {ticks.map((tick) => (
            <g key={tick}>
              <line x1={PAD.left} x2={WIDTH - PAD.right} y1={y(tick)} y2={y(tick)} className="grid" />
              <text x={PAD.left - 8} y={y(tick) + 4} textAnchor="end" className="axis">
                {tick}
              </text>
            </g>
          ))}
          {years.map((year, i) =>
            i % labelEvery === 0 ? (
              <text key={year} x={x(i)} y={HEIGHT - 8} textAnchor="middle" className="axis">
                {year}
              </text>
            ) : null
          )}
          {hover !== null && (
            <line x1={x(hover)} x2={x(hover)} y1={PAD.top} y2={PAD.top + innerH} className="crosshair" />
          )}
          {trends.map((trend) => (
            <polyline
              key={trend.id}
              fill="none"
              strokeWidth="2"
              style={{ stroke: trend.color }}
              points={years.map((year, i) => `${x(i)},${y(trend.values[year] || 0)}`).join(" ")}
            />
          ))}
          {hover !== null &&
            trends.map((trend) => (
              <circle
                key={trend.id}
                cx={x(hover)}
                cy={y(trend.values[years[hover]] || 0)}
                r="4.5"
                style={{ fill: trend.color }}
              />
            ))}
          {ends.map(({ trend, y: labelY }) => (
            <text key={trend.id} x={WIDTH - PAD.right + 8} y={labelY + 4} className="axis end-label">
              {trend.name}
            </text>
          ))}
          {years.map((year, i) => (
            <rect
              key={year}
              x={x(i) - innerW / (years.length - 1) / 2}
              y={PAD.top}
              width={innerW / (years.length - 1)}
              height={innerH}
              fill="transparent"
              onMouseEnter={() => setHover(i)}
              onMouseLeave={() => setHover(null)}
            />
          ))}
        </svg>
      )}
      {!asTable && hover !== null && (
        <div className="tooltip" role="status">
          <strong>{years[hover]}</strong>
          {trends.map((trend) => (
            <span key={trend.id}>
              <span className="legend-swatch" style={{ background: trend.color }} />
              {trend.name} {trend.values[years[hover]] || 0}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
