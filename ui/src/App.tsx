import SystemModule from "./modules/system/SystemModule";
import { BackendConnectionBanner } from "./components/BackendConnectionBanner";
import styles from "./App.module.scss";

export default function App() {
  return (
    <div className={styles.overlay}>
      <BackendConnectionBanner />
      <header className={styles.header}>
        <span className={styles.title}>🪄 Floating Agent</span>
        <button
          className={styles.hideBtn}
          onClick={() => window.floatingAgent?.hide()}
          aria-label="Hide"
        >
          ×
        </button>
      </header>
      <main className={styles.content}>
        <SystemModule />
      </main>
    </div>
  );
}
