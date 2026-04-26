import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useSystemStats } from "../modules/system/useSystemStats";
import type { ReactNode } from "react";

// Mock getDaemonUrl
vi.mock("@/lib/daemon", () => ({ getDaemonUrl: () => Promise.resolve("http://mock-daemon") }));

const mockStats = {
  cpu_percent: 42.5,
  ram_used_gb: 8.1,
  ram_total_gb: 16.0,
  ram_percent: 50.6,
  disk_used_gb: 100.0,
  disk_total_gb: 500.0,
  disk_percent: 20.0,
};

function wrapper({ children }: { children: ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
}

describe("useSystemStats", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockStats),
        } as Response)
      )
    );
  });

  it("returns system stats on success", async () => {
    const { result } = renderHook(() => useSystemStats(), { wrapper });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.cpu_percent).toBe(42.5);
    expect(result.current.data?.ram_percent).toBe(50.6);
  });
});
