import { useState } from "react";

// Name, keywords and description of a topic, for adding or editing one.
// onSave(data) returns a promise; an ApiError's field messages are shown
// next to their fields.
export default function TopicForm({ initial = {}, submitLabel, onSave, onCancel }) {
  const [name, setName] = useState(initial.name || "");
  const [keywords, setKeywords] = useState((initial.keywords || []).join(", "));
  const [description, setDescription] = useState(initial.description || "");
  const [errors, setErrors] = useState({});
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setErrors({});
    try {
      await onSave({ name: name.trim(), keywords, description: description.trim() });
    } catch (error) {
      const body = error.body && typeof error.body === "object" ? error.body : {};
      setErrors({ ...body, detail: body.detail || (Object.keys(body).length ? "" : error.message) });
    } finally {
      setBusy(false);
    }
  }

  const fieldError = (field) =>
    errors[field] && (
      <span className="error small" id={`${field}-error`}>
        {[errors[field]].flat().join(" ")}
      </span>
    );

  return (
    <form className="topic-form" onSubmit={submit}>
      <label>
        Name
        <input
          className="input"
          value={name}
          maxLength={80}
          required
          aria-describedby={errors.name ? "name-error" : undefined}
          onChange={(event) => setName(event.target.value)}
        />
        {fieldError("name")}
      </label>
      <label>
        Keywords <span className="muted small">— words or phrases, separated by commas</span>
        <input
          className="input"
          value={keywords}
          required
          placeholder="drone, parcel locker, delivery robot"
          aria-describedby={errors.keywords ? "keywords-error" : undefined}
          onChange={(event) => setKeywords(event.target.value)}
        />
        {fieldError("keywords")}
      </label>
      <label>
        Description <span className="muted small">— optional</span>
        <input
          className="input"
          value={description}
          maxLength={300}
          onChange={(event) => setDescription(event.target.value)}
        />
      </label>
      {errors.detail && <p className="error">{errors.detail}</p>}
      <p className="topic-form-actions">
        <button type="submit" className="button button-primary" disabled={busy}>
          {busy ? "Saving…" : submitLabel}
        </button>
        {onCancel && (
          <button type="button" className="button" onClick={onCancel}>
            Cancel
          </button>
        )}
      </p>
    </form>
  );
}
