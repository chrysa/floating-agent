# 🪄 Floating Multi-OS AI Assistant

[![CI](https://github.com/chrysa/floating-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/chrysa/floating-agent/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/chrysa/floating-agent?sort=semver&label=release)](https://github.com/chrysa/floating-agent/releases/latest)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An open-source floating multi-OS AI assistant that runs on **Windows** and **Linux**.
Always-on-top overlay providing quick access to AI, system monitoring, Notion project status, calendar, messaging, and productivity tools — without leaving your current context.

---

## Architecture

```
┌─────────────────────────────────────────────┐
│  Electron Shell (main process)              │
│  ┌──────────────────────────────────────┐   │
│  │  React UI (renderer)                 │   │
│  │  ┌────────┐ ┌────────┐ ┌──────────┐  │   │
│  │  │ System │ │ Notion │ │ Calendar │  │   │
│  │  └────────┘ └────────┘ └──────────┘  │   │
│  │  ┌────────┐ ┌──────────────────────┐  │   │
│  │  │  Chat  │ │     Messaging        │  │   │
│  │  └────────┘ └──────────────────────┘  │   │
│  └──────────────────────────────────────┘   │
└────────────────────┬────────────────────────┘
                     │ IPC (contextBridge)
┌────────────────────▼────────────────────────┐
│  Python Daemon  127.0.0.1:34001             │
│  ┌──────┐ ┌────────┐ ┌──────────┐ ┌──────┐  │
│  │psutil│ │Notion  │ │Calendar  │ │ AI   │  │
│  │plugin│ │plugin  │ │plugin    │ │router│  │
│  └──────┘ └────────┘ └──────────┘ └──┬───┘  │
└─────────────────────────────────────-│------┘
                                        │ HTTP
                             ┌──────────▼──────┐
                             │ ai-aggregator   │
                             └─────────────────┘
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
make install    # Install all dependencies (npm + pip)
make dev        # Start in development mode (hot reload)
make test       # Run all tests
make lint       # Lint all code
make build      # Build for production
make package    # Package for current OS
```

## Platform Support

| Platform        | Status         | Overlay method    |
| --------------- | -------------- | ----------------- |
| Linux (X11)     | 🚧 In progress | `alwaysOnTop`     |
| Linux (Wayland) | 📋 Planned     | `wlr-layer-shell` |
| Windows 10/11   | 📋 Planned     | Win32 API         |

## Stack

| Layer       | Technology                       |
| ----------- | -------------------------------- |
| Shell       | Electron 32+                     |
| UI          | React 19 + Vite 7 + TypeScript 5 |
| Daemon      | Python 3.12 + FastAPI            |
| System info | psutil                           |
| Secrets     | OS keychain (keyring)            |
| AI          | chrysa/ai-aggregator             |
| Tests       | Vitest + pytest                  |
| Packaging   | electron-builder                 |

## Security

- `nodeIntegration: false` — renderer has no direct Node access
- `contextIsolation: true` — secure IPC bridge via `contextBridge`
- No plaintext secrets on disk — OS keychain mandatory
- All OAuth flows handled in daemon process
- All AI calls logged (provider + timestamp, no content)

## Related Projects

- [chrysa/ai-aggregator](https://github.com/chrysa/ai-aggregator) — AI routing backend
- [chrysa/lifeos](https://github.com/chrysa/lifeos) — assistant / Jarvis layer (future)

## License

MIT
