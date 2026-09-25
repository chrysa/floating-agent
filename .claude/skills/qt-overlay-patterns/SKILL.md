---
name: qt-overlay-patterns
description: 'Use when working in floating_agent/overlay/ — PySide6 frameless always-on-top window, Wayland/X11 quirks, tray icon lifecycle, or dual-OS autostart (systemd user service / Windows Task Scheduler).'
---

# Qt overlay patterns — floating-agent

## When to invoke
Auto-invoke when: editing `floating_agent/overlay/`, debugging frameless/
always-on-top window behavior, tray icon issues, Wayland vs X11 positioning,
or autostart setup on Linux/Windows.

## Frameless, always-on-top window

- `Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint` on
  the top-level `QWidget`; test both flags together — dropping one breaks the
  overlay contract (D-0002: no browser chrome, no Electron).
- `Qt.WindowType.Tool` avoids a taskbar entry on Windows without losing
  always-on-top.
- Translucency requires `setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)`
  **and** a compositor — on X11 without a compositing WM the window renders
  opaque black instead of transparent. Check for this first when translucency
  "doesn't work" in a VM/CI screenshot.

## Wayland vs X11

- Wayland forbids a client from setting its own absolute window position
  (no `move()` support) — position via `QScreen` geometry at show time
  instead of after.
- Force a backend explicitly when debugging: `QT_QPA_PLATFORM=xcb` (X11) or
  `QT_QPA_PLATFORM=wayland`, since auto-detection differs across distros.
- CI and `pytest-qt` always run `QT_QPA_PLATFORM=offscreen` — never rely on
  windowing-system behavior (focus, opacity, raise/lower) in unit tests; test
  that behavior manually or skip with a marker.

## Tray icon lifecycle

- Create `QSystemTrayIcon` after `QApplication` exists but before the event
  loop starts; setting an icon before `QApplication` construction segfaults.
- Guard against `QSystemTrayIcon.isSystemTrayAvailable()` returning `False`
  (headless CI, some minimal Linux DEs) — degrade to overlay-only, don't crash.

## Autostart (dual-OS)

- **Linux**: systemd user service unit in `~/.config/systemd/user/`, enabled
  with `systemctl --user enable`; runs the same `python -m floating_agent`
  entry point as manual launch — no separate autostart code path to maintain.
- **Windows**: registry `Run` key or Task Scheduler task pointing at the
  packaged `.exe`; prefer Task Scheduler for a log-on trigger with retry.
- Keep both under a single `install_autostart()` seam so tests can mock the
  OS-specific branch instead of duplicating assertions per OS.
