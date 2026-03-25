import { useTopics } from "../TopicContext";

export default function TopicPicker() {
  const { topics, selected, setSelected } = useTopics();

  return (
    <select
      className="select picker"
      aria-label="Topic"
      value={selected[0] || ""}
      onChange={(event) => setSelected(event.target.value ? [event.target.value] : [])}
    >
      <option value="">All topics</option>
      {topics.map((topic) => (
        <option key={topic.id} value={topic.id}>
          {topic.name} ({topic.patent_count})
        </option>
      ))}
    </select>
  );
}
