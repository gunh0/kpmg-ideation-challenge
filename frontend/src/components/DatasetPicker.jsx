import { useDatasets } from "../DatasetContext";

export default function DatasetPicker() {
  const { datasets, selected, setSelected } = useDatasets();

  return (
    <select
      className="select picker"
      aria-label="Topic"
      value={selected}
      onChange={(event) => setSelected(event.target.value)}
    >
      <option value="">All topics</option>
      {datasets.map((dataset) => (
        <option key={dataset.id} value={dataset.id}>
          {dataset.name} ({dataset.patent_count})
        </option>
      ))}
    </select>
  );
}
