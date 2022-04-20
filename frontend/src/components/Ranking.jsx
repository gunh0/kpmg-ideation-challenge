// Horizontal bars for a ranked list. One hue: the bars compare magnitude,
// the names carry identity.
export default function Ranking({ rows, emptyText = "Nothing to rank." }) {
  if (!rows.length) return <p className="muted">{emptyText}</p>;
  const max = Math.max(...rows.map((row) => row.count));

  return (
    <ol className="ranking">
      {rows.map((row) => (
        <li key={row.name}>
          <span className="ranking-name" title={row.name}>
            {row.name}
          </span>
          <span className="ranking-bar">
            <span style={{ width: `${(100 * row.count) / max}%` }} />
          </span>
          <span className="ranking-count">{row.count}</span>
        </li>
      ))}
    </ol>
  );
}
