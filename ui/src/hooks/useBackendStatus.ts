import { useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

/**
 * Detects whether the local daemon backend is reachable.
 * Monitors browser online/offline events + React Query cache errors.
 * Returns true when the daemon is unavailable.
 */
export function useBackendStatus(): boolean {
  const [isDown, setIsDown] = useState(!navigator.onLine);
  const queryClient = useQueryClient();

  useEffect(() => {
    const handleOnline = () => setIsDown(false);
    const handleOffline = () => setIsDown(true);

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    const unsubscribe = queryClient.getQueryCache().subscribe((event) => {
      if (event?.query?.state?.status === "error") {
        const err = event.query.state.error as Error & {
          response?: { status: number };
        };
        const isDaemonError =
          !navigator.onLine ||
          err?.message?.toLowerCase().includes("network") ||
          err?.message?.toLowerCase().includes("failed to fetch") ||
          err?.message?.toLowerCase().includes("timeout") ||
          err?.response?.status === 0;
        if (isDaemonError) setIsDown(true);
      }
      if (event?.query?.state?.status === "success") {
        if (!navigator.onLine) return;
        setIsDown(false);
      }
    });

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
      unsubscribe();
    };
  }, [queryClient]);

  return isDown;
}
