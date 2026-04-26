const DAEMON_FALLBACK = "http://127.0.0.1:34001" as const;

let _cachedUrl: string | null = null;

export async function getDaemonUrl(): Promise<string> {
  if (_cachedUrl) return _cachedUrl;
  if (window.floatingAgent) {
    _cachedUrl = await window.floatingAgent.getDaemonUrl();
  } else {
    _cachedUrl = DAEMON_FALLBACK;
  }
  return _cachedUrl;
}
