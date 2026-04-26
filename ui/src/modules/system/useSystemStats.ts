import { useQuery } from "@tanstack/react-query";
import { getDaemonUrl } from "@/lib/daemon";

export interface SystemStats {
  cpu_percent: number;
  ram_used_gb: number;
  ram_total_gb: number;
  ram_percent: number;
  disk_used_gb: number;
  disk_total_gb: number;
  disk_percent: number;
}

async function fetchSystemStats(): Promise<SystemStats> {
  const base = await getDaemonUrl();
  const res = await fetch(`${base}/system`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<SystemStats>;
}

export function useSystemStats() {
  return useQuery<SystemStats>({
    queryKey: ["system"],
    queryFn: fetchSystemStats,
    refetchInterval: 3000,
  });
}
