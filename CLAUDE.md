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


<!-- chrysa:standards:start · managed by distribute-standards.sh · DO NOT EDIT -->
# chrysa — Transverse Standards (core)

> The **slim always-on core**. The canonical, tool-agnostic source of truth is `standards/STANDARDS.chrysa.md`; the normative annexes live under `standards/annexes/`. Each rule below is a one-line pointer — its full text lives in the per-domain file named beside the heading (`standards/rules/<domain>.md`), read on demand.

**Where an annexe and the canon disagree, the canon wins.**

### Governance, language & compliance · `standards/rules/governance.md`
- Normative annexes
- Language
- Compliance targets
- Governance — strategic pillars & ADR format

### Cross-cutting stack · `standards/rules/stack.md`
- Cross-cutting stack (settled ADRs — do not relitigate)

### SCM — branches, commits & pull requests · `standards/rules/scm.md`
- Commits
- Branches
- Branch model — `main` is production, `develop` is the workspace
- Merge
- One PR per issue
- Issues and PRs are type-driven

### Architecture, decoupling & portability · `standards/rules/architecture.md`
- Repo provenance — every code repo depends on `project-init`
- Every repo declares its profile and DDD level
- Projects talk through versioned contracts only
- Everything is machine-agnostic and portable — no rule, repo, or script is bound to one machine
- Every external server the service talks to is addressed through the environment — never hardcoded
- Every tracked file and folder must earn its place — a repo holds only what is useful to it now
- The repository architecture is legible to an agent — optimised for Claude, not only for humans
- Deferred work is a governed job, not a fire-and-forget

### Testing · `standards/rules/testing.md`
- Tests: pytest only
- Frontend tests: Vitest + Testing Library + MSW — from the scaffold, not later

### Frontend & web semantics · `standards/rules/frontend.md`
- TypeScript is strict by contract
- The JS/TS package manager is `pnpm` — `npm` and `yarn` are forbidden
- React is a presentation layer, not the domain
- The frontend says when the backend is unreachable or unstable
- The frontend is reactive and real-time by default
- UI state survives reload & focus
- Everything is semantic — the markup, the data, and the URLs
- URL-addressable frontend navigation — mandatory

### APIs, contracts & real-time · `standards/rules/api.md`
- A real-time backend has channel contracts and never blocks
- APIs, SDKs & public contracts follow the `STD-API-001` contract

### Accessibility · `standards/rules/accessibility.md`
- Dark mode
- Every site is usable by the majority of disabilities — not only the screen-reader case

### Documentation & session state · `standards/rules/docs.md`
- Notion logging
- Documentation and Notion are maintained in lockstep with the code — a change that leaves them stale is unfinished
- Session lifecycle (primer + memory + hindsight)

### AI agents & features · `standards/rules/agents.md`
- Agent actions are governed
- An AI feature is evaluated, not just shipped
- An agent writes only where the owner owns

### Security, identity & sessions · `standards/rules/security.md`
- Per-person data implies a user account — no exceptions dressed up as simplicity
- Identity goes through the cluster SSO first
- A session is secured and it expires
- Every form is a hostile input surface — validate on the server, always

### Code quality & anti-patterns · `standards/rules/code-quality.md`
- No hardcoded constants
- No literal HTTP status codes — use the constants the framework already ships
- No code duplication — the second occurrence is an extraction order
- Raised errors are typed
- Failures are contained, and observable
- Prefer a lookup table to a state machine
- Decompose into small, independently unit-testable methods
- Code is read far more often than it is written — optimise for the reader, and standardise the form
- Avoid lambdas and anonymous constructs — a named function is the default
- Basic optimisations and known anti-patterns are caught in review and in CI
- A cache is a correctness contract, not a sprinkle of speed
- Quality gates
- Error handling pattern (all automations)

### Backend Python · `standards/rules/backend-python.md`
- Python packaging — `pyproject.toml` is the single source of truth
- Python is written object-oriented, one class per file
- Import the item, not the module — `from x import y; y()`
- Functions and methods are called with named arguments — positional call sites are the exception, not the rule

### Data, persistence & migrations · `standards/rules/data.md`
- Data, persistence & migrations follow the `STD-DATA-001` contract

### Observability & operations · `standards/rules/observability.md`
- Observability & production readiness follow the `STD-OPS-001` contract
- The container is versioned separately from the application it hosts, and an admin can see what is actually deployed
- Observability — error-tracking → GitHub issues (norm)

### Containers & compose · `standards/rules/containers.md`
- Everything runs in a container — the only exception is the slice of a repo genuinely bound to the host OS
- External dependencies are installed in containers, never on the host
- No virtualenv in a repo — ever
- Tool caches & deps never touch the project tree
- Dockerfiles are multi-stage, with a `production` and a `dev` stage — mandatory
- App containers ship the app only — the platform layer is the owner's responsibility
- Only a publicly useful port is published — everything else stays on the container network
- A compose file is minimal — declare only what the stack needs, default the rest
- Dev stage must hot-reload
- Local dev runs the code in-container, live, in debug mode — never the production server
- `.dockerignore` mandatory & exhaustive
- Container-runtime policy

### Product surfaces · `standards/rules/product.md`
- Setup wizard & config panel
- A game is DRM-free and fully playable solo offline
- Every product that is operated ships a management backoffice
- If a user can supply a file, the product accepts an upload
- A floating assistant where it earns its place — never as decoration

### Design system · `standards/rules/design.md`
- Design system

### Developer loop & tooling · `standards/rules/dev-loop.md`
- Makefile targets
- Shared skills (load on demand from shared-standards/.claude/skills/)

### CI/CD, pre-commit & release · `standards/rules/ci-cd.md`
- Release & changelog config (canonical)
- GitHub Actions (reuse first · custom actions centralised · thin workflows)
- Pre-commit & git hooks (native, via pre-commit.com — never wrapped in make)
<!-- chrysa:standards:end -->
