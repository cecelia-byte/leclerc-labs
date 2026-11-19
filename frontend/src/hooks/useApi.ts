import { useEffect, useState } from 'react'

interface ApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

/**
 * Fetches data and exposes its state.
 *
 * `deps` works like useEffect's dependency list: pass the values that, when
 * changed, should trigger a fresh request (for example [year]).
 * `enabled` lets us skip a request until we have the IDs it needs.
 */
export function useApi<T>(
  fetcher: (signal: AbortSignal) => Promise<T>,
  deps: unknown[],
  enabled = true,
) {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: enabled,
    error: null,
  })
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    if (!enabled) {
      setState({ data: null, loading: false, error: null })
      return
    }

    const controller = new AbortController()
    setState({ data: null, loading: true, error: null })

    fetcher(controller.signal)
      .then((data) => {
        if (!controller.signal.aborted) {
          setState({ data, loading: false, error: null })
        }
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) return
        setState({
          data: null,
          loading: false,
          error: error instanceof Error ? error.message : 'Something went wrong',
        })
      })

    return () => controller.abort()
    // `fetcher` is intentionally omitted; `deps` controls refetching.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, attempt, enabled])

  return { ...state, refetch: () => setAttempt((value) => value + 1) }
}
