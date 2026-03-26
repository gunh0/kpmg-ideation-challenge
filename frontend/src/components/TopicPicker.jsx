import { useEffect, useRef, useState } from "react";

import { useTopics } from "../TopicContext";
import { formatNumber } from "../format";

export function pickerLabel(topics, selected) {
  const names = topics.filter((topic) => selected.includes(String(topic.id))).map((topic) => topic.name);
  if (!names.length) return "All topics";
  if (names.length <= 2) return names.join(" + ");
  return `${names.length} topics`;
}

// Several topics can be selected: the patent list then ranks the patents
// that match more of them first.
export default function TopicPicker() {
  const { topics, selected, setSelected } = useTopics();
  const [open, setOpen] = useState(false);
  const box = useRef(null);

  useEffect(() => {
    if (!open) return undefined;
    const close = (event) => {
      if (event.type === "keydown" ? event.key === "Escape" : !box.current?.contains(event.target)) setOpen(false);
    };
    document.addEventListener("mousedown", close);
    document.addEventListener("keydown", close);
    return () => {
      document.removeEventListener("mousedown", close);
      document.removeEventListener("keydown", close);
    };
  }, [open]);

  function toggle(id) {
    setSelected(selected.includes(id) ? selected.filter((item) => item !== id) : [...selected, id]);
  }

  return (
    <div className="picker" ref={box}>
      <button
        type="button"
        className="select picker-button"
        aria-haspopup="true"
        aria-expanded={open}
        onClick={() => setOpen(!open)}
      >
        {pickerLabel(topics, selected)}
      </button>
      {open && (
        <fieldset className="picker-menu">
          <legend className="visually-hidden">Topics</legend>
          <label className="picker-option">
            <input type="checkbox" checked={!selected.length} onChange={() => setSelected([])} />
            All topics
          </label>
          {topics.map((topic) => (
            <label key={topic.id} className="picker-option">
              <input
                type="checkbox"
                checked={selected.includes(String(topic.id))}
                onChange={() => toggle(String(topic.id))}
              />
              {topic.name}
              <span className="muted small">{formatNumber(topic.patent_count)}</span>
            </label>
          ))}
        </fieldset>
      )}
    </div>
  );
}
