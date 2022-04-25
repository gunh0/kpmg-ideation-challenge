export default function ErrorMessage({ error, onRetry }) {
  if (!error) return null;
  const offline = error instanceof TypeError; // fetch() rejects with TypeError when the API is unreachable
  return (
    <div className="alert" role="alert">
      <span>{offline ? "The API is not reachable. Is the backend running?" : error.message}</span>
      {onRetry && (
        <button type="button" className="button" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}
