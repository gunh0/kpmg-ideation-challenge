export default function ErrorMessage({ error, onRetry }) {
  if (!error) return null;
  // fetch() rejects with a TypeError when there is no server at all
  const offline = error instanceof TypeError || error.unreachable;
  return (
    <div className="alert" role="alert">
      <span>
        {offline ? (
          <>
            The API is not reachable. Start the backend — <code>make dev-back</code>, or <code>docker compose up</code> —
            and try again.
          </>
        ) : (
          error.message
        )}
      </span>
      {onRetry && (
        <button type="button" className="button" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}
