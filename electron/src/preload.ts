/**
 * Electron preload script — secure IPC bridge
 *
 * Exposes a limited API to the renderer via contextBridge.
 * nodeIntegration is disabled; only these APIs are available.
 */

import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("floatingAgent", {
  // ─── Daemon ─────────────────────────────────────────────────────────────
  getDaemonUrl: (): Promise<string> => ipcRenderer.invoke("daemon:url"),

  // ─── Window ─────────────────────────────────────────────────────────────
  hide: (): void => ipcRenderer.send("window:hide"),
  show: (): void => ipcRenderer.send("window:show"),
});

// Type declaration for renderer (also exported via ui/src/types/electron.d.ts)
export type FloatingAgentAPI = {
  getDaemonUrl: () => Promise<string>;
  hide: () => void;
  show: () => void;
};
