// Type definitions for the Electron preload bridge exposed via contextBridge

interface FloatingAgentAPI {
  getDaemonUrl: () => Promise<string>;
  hide: () => void;
  show: () => void;
}

declare global {
  interface Window {
    floatingAgent?: FloatingAgentAPI;
  }
}

export {};
