# CLAUDE.md — floating-agent

## Vision

🪄 Floating Multi-OS AI Assistant — an always-on-top overlay running on Windows and Linux
that provides quick access to AI, system monitoring, Notion project status, calendar,
messaging, and productivity tools without leaving your current context.

## Architecture

**Option A (preferred)**: Electron shell + React UI (renderer) + Python daemon (sidecar)

```
floating-agent/
├── electron/          # Electron main + preload (TypeScript)
│   ├── src/
│   │   ├── main.ts       # Main process — window management, IPC, tray
│   │   ├── preload.ts    # Secure IPC bridge (contextIsolation)
│   │   └── overlay.ts    # Floating window config (always-on-top, frameless)
│   ├── package.json
│   └── tsconfig.json
├── ui/                # React renderer (Vite + TypeScript + SCSS Modules)
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   ├── hooks/
│   │   └── modules/
│   │       ├── system/      # CPU/RAM/disk widgets
│   │       ├── notion/      # Project status cards
│   │       ├── calendar/    # Upcoming events
│   │       ├── messaging/   # Gmail/Slack quick-view
│   │       └── ai/          # Chat / quick AI input
│   ├── package.json
│   └── vite.config.ts
├── daemon/            # Python FastAPI sidecar (port 34001)
│   ├── floating_agent/
│   │   ├── main.py       # FastAPI app entry
│   │   ├── api/          # HTTP routers
│   │   ├── plugins/      # System, Notion, Calendar, Messaging plugins
│   │   └── models/       # Pydantic schemas
│   ├── tests/
│   └── pyproject.toml
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── release.yml
├── Makefile
├── cliff.toml
├── GitVersion.yml
├── .pre-commit-config.yaml
└── README.md
```

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Shell | Electron (contextIsolation + nodeIntegration=false) | Cross-platform, rich ecosystem |
| UI | React 19 + Vite + TypeScript | Familiar stack, fast HMR |
| Daemon | Python FastAPI (async) | Reuse chrysa Python stack, psutil, keyring |
| AI routing | chrysa/ai-aggregator HTTP API | Centralized provider management |
| Secrets | OS keychain via `keyring` lib | No plaintext secrets |
| Overlay | `alwaysOnTop: true`, frameless, transparent bg | Non-intrusive floating behavior |
| IPC | contextBridge → preload → renderer | Security best practice |

## Security Rules

- `nodeIntegration: false` in all renderer windows (mandatory)
- `contextIsolation: true` in all renderer windows (mandatory)
- No plaintext secrets on disk — OS keychain (`keyring`) mandatory
- OAuth flows handled by daemon, tokens never exposed to renderer
- All AI calls logged with provider + timestamp (no content in logs)

## Plugins System (daemon)

Each integration lives in `daemon/floating_agent/plugins/`:
- `system.py` — psutil: CPU, RAM, disk, process list
- `notion.py` — Notion MCP or REST API client
- `calendar.py` — Google Calendar (OAuth2)
- `messaging.py` — Gmail summary + Slack status
- `ai_router.py` — HTTP client → ai-aggregator

## Platform Notes

- **Linux**: Wayland (`_NET_WM_STATE_ABOVE`) + X11 fallback, systemd user service
- **Windows**: `alwaysOnTop` via Win32 API, startup via registry or Task Scheduler
- **Packaging**: `electron-builder` — AppImage + deb for Linux, NSIS installer for Windows

## Makefile Targets

```
make install     — install all dependencies (npm + pip)
make dev         — start Electron dev (hot reload)
make test        — run all tests (vitest + pytest)
make lint        — lint all (eslint + ruff)
make format      — format all (prettier + ruff format)
make build       — build distributable
make package     — package for current OS
make clean       — remove build artifacts
```

## Stack

- **Electron**: 32+ (latest stable)
- **React**: 19 + TypeScript 5 (strict)
- **Vite**: 7 (renderer bundler)
- **Python**: 3.12+ — FastAPI — psutil — keyring — httpx
- **Testing**: Vitest (UI) + pytest (daemon)
- **Linting**: ESLint 9 + Ruff
- **CI**: GitHub Actions — lint + test + build on every PR
- **Packaging**: electron-builder
- **Versioning**: GitVersion (semver)

## Development Setup

```bash
make install     # install all deps
make dev         # start in dev mode
```

Daemon starts automatically as subprocess of Electron main process.
Daemon listens on `127.0.0.1:34001` (localhost only, not exposed).

## Connections to chrysa ecosystem

- **ai-aggregator**: AI routing — configure URL in `daemon/.env`
- **Notion**: read project status from Centre de suivi
- **LifeOS**: future — assistant / Jarvis layer
- **os-autonome**: future — OS state and remediation
