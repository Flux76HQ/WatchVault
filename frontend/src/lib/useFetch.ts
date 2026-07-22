import { useCallback, useEffect, useRef, useState } from "react";

// Minimal data hook: re-runs when any dep changes, exposes reload.
export function useFetch<T>(fn: () => Promise<T>, deps: any[]) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<unknown>(null);
  const [loading, setLoading] = useState(true);
  const requestId = useRef(0);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const run = useCallback(fn, deps);

  const load = useCallback(async () => {
    const currentRequest = ++requestId.current;
    setLoading(true);
    setError(null);
    try {
      const result = await run();
      if (requestId.current === currentRequest) setData(result);
    } catch (e) {
      if (requestId.current === currentRequest) setError(e);
    } finally {
      if (requestId.current === currentRequest) setLoading(false);
    }
  }, [run]);

  // Silent refetch: updates data in place without toggling `loading`, so the
  // page is not swapped for a spinner and the scroll position is preserved.
  // Keeps the existing data on failure (the triggering action reports its own error).
  const refresh = useCallback(async () => {
    const currentRequest = ++requestId.current;
    try {
      const result = await run();
      if (requestId.current === currentRequest) setData(result);
    } catch {
      /* keep current data */
    }
  }, [run]);

  useEffect(() => { load(); }, [load]);

  return { data, error, loading, reload: load, refresh, setData };
}
