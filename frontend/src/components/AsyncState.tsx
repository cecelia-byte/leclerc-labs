/** Shared loading, error and empty views. */

export function LoadingState({ label }: { label: string }) {
  return (
    <div className="async-state" role="status">
      <span className="async-state__pulse" />
      <span>{label}…</span>
    </div>
  )
}

export function ErrorState({
  message,
  onRetry,
}: {
  message: string
  onRetry: () => void
}) {
  return (
    <div className="async-state async-state--error" role="alert">
      <span>{message}</span>
      <button type="button" className="retry-button" onClick={onRetry}>
        Retry
      </button>
    </div>
  )
}

export function EmptyState({ title, message }: { title: string; message: string }) {
  return (
    <div className="async-state async-state--empty">
      <strong>{title}</strong>
      <span>{message}</span>
    </div>
  )
}
