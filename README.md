# 🪄 Floating Multi-OS AI Assistant

[![CI](https://github.com/chrysa/floating-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/chrysa/floating-agent/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/chrysa/floating-agent?sort=semver&label=release)](https://github.com/chrysa/floating-agent/releases/latest)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An open-source floating multi-OS AI assistant that runs on **Windows** and **Linux**.
A proactive **whole-life agent** behind an always-on-top overlay: it reads/writes your Notion,
sends you reminders, and acts across system monitoring, calendar, and messaging — without
leaving your current context.

---

## Architecture

Single Python process — a native **PySide6 (Qt)** overlay over a tool-calling agent core.
Electron and the React UI were removed (see [DECISIONS.md](DECISIONS.md) D-0002).

```
┌──────────────────────────────────────────────────┐
│  Single Python process                             │
│                                                    │
│   PySide6 overlay  ── surface: chat + reminders    │
│        ▲ notify / surface          │ intent        │
│        │                           ▼               │
│   Proactive engine  ──wake──►   Agent (tool-loop)  │
│   (scheduler + notifier)            │              │
│                          ┌──────────┴───────────┐  │
│                       Tools: Notion(R/W) · System │
│                       · Calendar · Messaging · AI │
│                                     │ HTTP         │
│                          ┌──────────▼──────┐       │
│                          │  ai-aggregator  │       │
│                          └─────────────────┘       │
└──────────────────────────────────────────────────┘
```

## Quick Start

```bash
git clone https://github.com/chrysa/floating-agent.git
cd floating-agent
make install
make dev
```

## Development

```bash
make help       # Show all targets
make install    # Install runtime dependencies with uv
make install-dev # Install development dependencies + pre-commit hooks
make dev        # Launch the PySide6 overlay (python -m floating_agent)
make test       # Run tests in Docker
make lint       # Ruff
make build      # Package a standalone binary (PyInstaller)
```

## Platform Support

| Platform        | Status         | Overlay method    |
| --------------- | -------------- | ----------------- |
| Linux (X11)     | 🚧 In progress | `alwaysOnTop`     |
| Linux (Wayland) | 📋 Planned     | `wlr-layer-shell` |
| Windows 10/11   | 📋 Planned     | Win32 API         |

## Roadmap

### V0.2 — Extended monitoring

- [ ] **Network plugin** — bandwidth ↑↓ MB/s, active connections count (`psutil.net_io_counters`)
- [ ] **Processes plugin** — top 5 by CPU/RAM, kill action from UI (`psutil.process_iter`)
- [ ] **Alert thresholds** — configurable via env/config, `/alerts` endpoint, alert badge in overlay

### V0.3 — Dev environment awareness

- [ ] **Docker plugin** — container list with status, CPU/RAM per container (Docker socket)
- [ ] **Metrics history** — in-memory ring buffer (60 readings = 3 min), sparkline charts in UI
- [ ] **Notion plugin** — project status cards from Centre de suivi

### V0.4 — Integrations

- [ ] **Calendar plugin** — Google Calendar upcoming events
- [ ] **AI chat module** — quick prompt → ai-aggregator → answer in overlay

### V1.0 — AI-first dev companion

- [ ] **Self-healing engine** — condition → action rules (YAML config): e.g. CPU > 90% → kill top process
- [ ] **AI script assistant** — natural language → executable shell command (generated + confirmed before run)
- [ ] **Wayland support** — `wlr-layer-shell` native integration
- [ ] **Windows packaging** — NSIS installer, Win32 always-on-top

## Stack

| Layer       | Technology                    |
| ----------- | ----------------------------- |
| Shell / UI  | PySide6 (Qt) — native overlay |
| Core        | Python 3.14 (agent + plugins) |
| HTTP (opt.) | FastAPI (`--serve`)           |
| System info | psutil                        |
| Secrets     | OS keychain (keyring)         |
| AI          | chrysa/ai-aggregator          |
| Tests       | pytest + pytest-qt            |
| Packaging   | PyInstaller                   |

## Security

- No plaintext secrets on disk — OS keychain (`keyring`) mandatory
- OAuth flows handled in-process; tokens never logged
- All AI calls logged (provider + timestamp, no content)
- Agent writes (Notion, etc.) require confirmation or dry-run for sensitive actions

## Related Projects

- [chrysa/ai-aggregator](https://github.com/chrysa/ai-aggregator) — AI routing backend
- [chrysa/lifeos](https://github.com/chrysa/lifeos) — assistant / Jarvis layer (future)

## License

MIT
