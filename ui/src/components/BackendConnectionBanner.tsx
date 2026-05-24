import { useBackendStatus } from "../hooks/useBackendStatus";
import styles from "./BackendConnectionBanner.module.scss";

export function BackendConnectionBanner() {
  const isDown = useBackendStatus();

  if (!isDown) return null;

  return (
    <div role="alert" aria-live="assertive" className={styles.banner}>
      <span aria-hidden="true">⚠️</span>
      <span>
        Agent daemon unreachable. Please ensure the floating-agent daemon is
        running.
      </span>
    </div>
  );
}
