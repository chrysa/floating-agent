import { useSystemStats } from "./useSystemStats";
import styles from "./SystemModule.module.scss";

function gaugeColor(value: number): string {
  if (value > 85) return "#ef4444";
  if (value > 60) return "#f59e0b";
  return "#22c55e";
}

function GaugeBar({ value, label }: { value: number; label: string }) {
  const color = gaugeColor(value);
  return (
    <div className={styles.gauge}>
      <div className={styles.gaugeLabel}>
        <span>{label}</span>
        <span>{value.toFixed(0)}%</span>
      </div>
      <div className={styles.gaugeTrack}>
        <div
          className={styles.gaugeFill}
          style={{ width: `${value}%`, background: color }}
        />
      </div>
    </div>
  );
}

export default function SystemModule() {
  const { data, isLoading, isError } = useSystemStats();

  if (isLoading) return <div className={styles.card}>Loading…</div>;
  if (isError || !data)
    return <div className={styles.cardError}>Daemon unreachable</div>;

  return (
    <div className={styles.card}>
      <h3 className={styles.title}>System</h3>
      <GaugeBar value={data.cpu_percent} label="CPU" />
      <GaugeBar
        value={data.ram_percent}
        label={`RAM ${data.ram_used_gb.toFixed(1)} / ${data.ram_total_gb.toFixed(1)} GB`}
      />
      <GaugeBar
        value={data.disk_percent}
        label={`Disk ${data.disk_used_gb.toFixed(0)} / ${data.disk_total_gb.toFixed(0)} GB`}
      />
    </div>
  );
}
