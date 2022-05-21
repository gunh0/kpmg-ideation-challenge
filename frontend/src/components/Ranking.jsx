import { Link } from "react-router-dom";

// Horizontal bars for a ranked list. One hue: the bars compare magnitude,
// the names carry identity. linkTo(row) turns names into links.
export default function Ranking({ rows, linkTo, emptyText = "Nothing to rank." }) {
  if (!rows.length) return <p className="muted">{emptyText}</p>;
  const max = Math.max(...rows.map((row) => row.count));

  return (
    <ol className="ranking">
      {rows.map((row) => (
        <li key={row.name}>
          {linkTo ? (
            <Link className="ranking-name" title={`Show patents of ${row.name}`} to={linkTo(row)}>
              {row.name}
            </Link>
          ) : (
            <span className="ranking-name" title={row.name}>
              {row.name}
            </span>
          )}
          <span className="ranking-bar">
            <span style={{ width: `${(100 * row.count) / max}%` }} />
          </span>
          <span className="ranking-count">
            {row.count}
            {row.granted !== undefined && (
              <span className="ranking-rate" title={`${row.granted} of ${row.count} granted`}>
                {Math.round((100 * row.granted) / row.count)}% granted
              </span>
            )}
          </span>
        </li>
      ))}
    </ol>
  );
}
