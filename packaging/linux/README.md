# Floating Agent — Debian beta packaging notes

This directory contains the Linux-specific assets used by the user-level installer:

- `packaging/desktop/floating-agent.desktop` for the desktop launcher
- `packaging/systemd/floating-agent.service` for optional user autostart
- `install.sh` / `uninstall.sh` to wire the local `uv` environment

Hyprland toggle binding:

```ini
bind = SUPER, SPACE, exec, ~/.local/bin/floating-agent --toggle
```

The overlay is offline-first and degrades cleanly when the tray is unavailable.

