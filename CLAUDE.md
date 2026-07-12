# CLAUDE.md — floating-agent

## Vision

🪄 Floating Multi-OS AI Assistant — an always-on-top overlay running on Windows and Linux
that provides quick access to AI, system monitoring, Notion project status, calendar,
messaging, and productivity tools without leaving your current context.

## Language Rules

- Language: English — all code, comments, documentation, instructions, and configuration files must be in English.

## Architecture

**Single Python process** — native PySide6 (Qt) overlay + agent core. Electron and the React UI
were removed (see [DECISIONS.md](DECISIONS.md) D-0002). The overlay is the surface; the heart is a
tool-calling agent with a proactive engine.

```
floating-agent/
├── floating_agent/        # the whole app (single Python package)
│   ├── __main__.py        # `python -m floating_agent` → launches the overlay
│   ├── main.py            # OPTIONAL FastAPI HTTP layer (`--serve`), port 34001
│   ├── api/               # HTTP routers (only used when --serve)
│   ├── models.py          # Pydantic schemas (SystemStats, …)
│   ├── plugins/           # system (psutil) + notion / calendar / messaging (low-level tools)
│   ├── agent/             # (PR3) tool-calling loop + tool registry + memory  ← THE BRAIN
│   ├── proactive/         # (PR5) scheduler (cron-like) + OS notifier         ← REMINDERS
│   └── overlay/           # (PR2) PySide6 window, widgets, theme, tray        ← THE SURFACE
├── tests/                 # pytest (core) + pytest-qt (widgets)
├── packaging/             # (PR8) PyInstaller specs (.exe + AppImage)
├── pyproject.toml         # at repo ROOT (so install-project / pip find the project)
├── Makefile · cliff.toml · GitVersion.yml · .pre-commit-config.yaml · README.md
```

> Status: PR1 (this) removes Electron/React and restructures to root. `agent/`, `proactive/`,
> `overlay/` land in later PRs — see the Notion project page for the 8-PR plan.

## Key Design Decisions

| Decision    | Choice                                              | Rationale                                  |
| ----------- | --------------------------------------------------- | ------------------------------------------ |
| Shell       | Native PySide6 (Qt), single process                 | Light, cross-OS (Win+Linux), no Chromium   |
| Scope       | Proactive whole-life agent (not a passive overlay)  | Reads/writes Notion, sends reminders, acts |
| Core        | Python plugins called in-process (HTTP optional)    | Reuse chrysa Python stack, psutil, keyring |
| AI          | tool-calling loop via chrysa/ai-aggregator / Claude | Agentic, not a one-shot chat box           |
| Secrets     | OS keychain via `keyring` lib                       | No plaintext secrets                       |
| Overlay     | Frameless · `WindowStaysOnTopHint` · translucent    | Non-intrusive floating behavior            |
| Proactivity | 2 phases: explicit reminders → emergent (Jarvis)    | Reliable base before fuzzy intelligence    |

## Security Rules

- No plaintext secrets on disk — OS keychain (`keyring`) mandatory
- OAuth flows handled in-process; tokens never logged
- All AI calls logged with provider + timestamp (no content in logs)
- **Agent writes (Notion, etc.) require confirmation or dry-run** for sensitive actions

## Plugins / tools (core)

Each integration lives in `floating_agent/plugins/`, exposed to the agent via `agent/tools.py`:

- `system.py` — psutil: CPU, RAM, disk, process list ✅
- `notion.py` — Notion **REST API** R/W (`NOTION_API_KEY`; MCP is unavailable in a packaged app)
- `calendar.py` — Google Calendar (OAuth2)
- `messaging.py` — Gmail summary + Slack status

## Platform Notes

- **Linux**: Qt on Wayland + X11; systemd user service for autostart
- **Windows**: Qt always-on-top; autostart via registry or Task Scheduler
- **Packaging**: PyInstaller — AppImage (Linux) + NSIS/.exe (Windows)
- **CI**: Qt tests run headless via `QT_QPA_PLATFORM=offscreen`

## Makefile Targets

```
make install     — install python deps (pip / uv)
make dev         — run the overlay (python -m floating_agent)
make test        — pytest (+ pytest-qt)
make lint        — ruff
make format      — ruff format
make build       — package via PyInstaller
make clean       — remove build artifacts
```

## Stack

- **Shell/UI**: PySide6 (Qt) — native overlay
- **Python**: 3.14 — FastAPI (optional) — psutil — keyring — httpx — pydantic
- **Testing**: pytest + pytest-qt
- **Linting**: Ruff (`target-version = py313`, see D-0002)
- **CI**: GitHub Actions — ruff + mypy + pytest on every PR
- **Packaging**: PyInstaller · **Versioning**: GitVersion (semver)

## Development Setup

```bash
make install               # install python deps
python -m floating_agent   # launch the overlay
make serve                 # (optional) run the FastAPI HTTP layer on 127.0.0.1:34001
```

## Connections to chrysa ecosystem

- **ai-aggregator**: AI routing — configure URL in `.env`
- **Notion**: read/write project status + reminders (REST API)
- **LifeOS**: agent-orchestration boundary to re-arbitrate (D-0002)
- **os-autonome**: future — OS state and remediation

## Skills

Shared skills from `shared-standards/.claude/skills/`:

- `ui-ux/SKILL.md` — UX/UI/ergonomics across ALL surfaces (web, CLI, VS Code, Discord, desktop, game, agent) + WCAG 2.1 AA + dark mode + i18n FR+EN (load when building any human-facing surface)

<!-- chrysa:standards-import:start -->
@.chrysa/STANDARDS.md
<!-- chrysa:standards-import:end -->

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
