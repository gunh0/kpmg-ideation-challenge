export function formatDate(value) {
  return value || "—";
}

export default function PatentTable({ patents }) {
  return (
    <div className="table-wrap">
      <table className="table">
        <thead>
          <tr>
            <th>Patent</th>
            <th>Title</th>
            <th>Assignee</th>
            <th>Published</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {patents.map((patent) => (
            <tr key={patent.id}>
              <td className="mono nowrap">{patent.patent_id}</td>
              <td>{patent.title}</td>
              <td>{patent.assignee || "—"}</td>
              <td className="nowrap">{formatDate(patent.publication_date)}</td>
              <td>
                <span className={`badge ${patent.is_granted ? "badge-granted" : "badge-pending"}`}>
                  {patent.is_granted ? "Granted" : "Application"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
