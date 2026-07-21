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

# chrysa — Transverse Standards

These conventions are identical across every chrysa repo. Repo-specific rules live in the
local `CLAUDE.md`; this file is the shared baseline imported by it.

## Cross-cutting stack (settled ADRs — do not relitigate)

| Layer          | Decision                                                       |
| -------------- | -------------------------------------------------------------- |
| Python         | 3.14 target (CI matrix 3.12 + 3.14)                            |
| FastAPI        | >= 0.115 + Pydantic v2                                         |
| Frontend       | React 19 + TypeScript 7 + Vite 8                               |
| UI             | shadcn/ui + Tailwind CSS                                       |
| State          | TanStack Query + Zustand                                       |
| DB             | PostgreSQL 16 + Redis 7                                        |
| ORM            | SQLAlchemy 2.0 async + Alembic                                 |
| Auth           | 4 modes: Google OAuth2 · local (bcrypt) · LDAP · VCS OAuth     |
| i18n           | react-i18next + fastapi-babel · FR + EN from V1                |
| Monorepo       | Turborepo + pnpm workspaces                                    |
| Versioning     | GitVersion (semantic auto — never bump manually)               |
| Quality CI     | SonarCloud (0 hotspot · rating A)                              |
| Linting        | Ruff + Mypy (Python) · ESLint (TS)                             |
| Pre-commit     | detect-secrets + ruff + mypy + commitlint                      |
| Error handling | withErrorHandling() → auto GitHub Issue on failure             |
| Hosting        | Kimsufi · Docker Compose (local) · Nginx · Certbot · Tailscale |
| Monitoring     | Sentry + Uptime Kuma (self-hosted)                             |
| Agents         | Claude API (primary) · Ollama (fallback)                       |
| Orchestration  | LangGraph (stateful) · PydanticAI (structured outputs)         |

## Non-negotiable conventions

- **Language**: English — all code, comments, docs, instructions, and config files.
- **Commits**: Conventional Commits (`feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`).
- **Branches**: `feature/`, `bugfix/`, `chore/`, `hotfix/`, `release/` · default branch `develop`.
- **Merge**: squash merge only · force push forbidden · auto-merge requires CI + owner.
- **One PR per issue**, scoped tight. Every PR references an issue (`Closes/Fixes/Refs #N`).
  Exception: label `hotfix`. The `enforce-issue-link` workflow is a blocking status check.
- **Tests: pytest only** — assert-style test functions and `pytest-mock` (`mocker`
  fixture: `mocker.patch`, `mocker.AsyncMock`) for all mocking. The stdlib **`unittest`
  framework (`unittest.TestCase`) and `unittest.mock` imports are forbidden** — no
  `import unittest`, no `from unittest.mock import …`. See the `testing-pytest` skill.
- **Dark mode** mandatory from V1. **Accessibility** WCAG 2.1 AA.
- **UI state survives reload & focus** — human-facing surfaces persist their navigation
  and view state (active tab/section, selected sub-view, active context/filters) so a
  **manual reload keeps the current page** — the user lands exactly where they were, never
  reset to a default. Persist to `localStorage` (or the URL for shareable state), guarded
  by a validator that discards stale/removed values. Interface or state changes must
  **propagate across the app's own tabs/windows and on refocus/reload**: listen to the
  browser `storage` event and re-read on `window` `focus`, so a view opened while hidden
  never shows stale state after the user comes back. A reload that loses the user's place,
  or a change that fails to propagate on focus/reload, is a bug.
- **Notion logging**: every advancement and modification (progress, decisions, state
  changes) is logged in Notion — the single source of truth. Run `@notion-sync` after any
  state change; in case of conflict between local docs and Notion, Notion wins.
- **No hardcoded constants** in code — neither backend (Python) nor frontend (TS).
  All constants and config values (thresholds, business rules, labels, URLs, magic
  numbers) live in **external YAML files** and are loaded at runtime. Code reads them
  through a typed loader (Pydantic Settings backend · generated typed module frontend),
  never as inline literals. Only language-level enums (e.g. `status.HTTP_*`) are exempt.
- **Semantic URLs & code** — URLs are resource-oriented and human-readable: lowercase,
  hyphenated, plural-noun collections, no verbs or actions in the path (`GET /invoices/42`,
  never `/getInvoice?id=42`); REST shapes follow the `api-design` skill. Code is
  self-describing: intention-revealing names over comments, semantic HTML elements
  (`<nav>`, `<button>`, `<main>`, `<header>`…) never a `<div>` wired as a control, and
  ARIA used only to fill gaps native semantics cannot express.
- **URL-addressable frontend navigation — mandatory.** Every navigable view/route/tab/
  detail is a **real, semantic URL** (`/projects/42/settings`, not `/#` or a modal with no
  address). Navigating **must change the URL** via the router (History API `pushState`), so:
  1. the change is **recorded in browser history** — Back/Forward move between views, never
     trap or reload the app;
  2. a link is **right-clickable / middle-clickable / ⌘-clickable → open in a new tab**, which
     means it is a genuine `<a href>` (or the router's `<Link>`), **never** a `<div>`/`<button>`
     with an `onClick` that only mutates state;
  3. the URL is **deep-linkable & shareable** — pasting it in a fresh tab lands on the exact
     same view (route params + query for filters/selection/pagination), reproducible without
     prior in-app state.
     Ephemeral UI (transient toasts, open/closed of a purely local menu) may stay stateless, but
     anything a user would bookmark, share, or reload into is a route. This complements
     _UI state survives reload & focus_: persisted view-state that has an addressable identity
     belongs in the URL, not only `localStorage`.
- **No virtualenv in a repo — ever.** `venv/`, `.venv/`, `env/` are **forbidden** inside a
  project tree. Python runs in the Docker image (deps baked into the image layer, or a named
  volume for editable installs). A committed or on-disk virtualenv is a bug, not a setup step.
  The only sanctioned local Python is a **uv/pipx tool env stored outside the repo** (e.g.
  `~/.local`, `$UV_CACHE_DIR`), never a folder living next to the source.
- **Tool caches & deps never touch the project tree.** `__pycache__`, `.pytest_cache`,
  `.ruff_cache`, `.mypy_cache`, `.benchmarks`, `node_modules`, and pip/npm/uv download caches
  are regenerable machine artifacts — they must be **invisible in the repo working copy**.
  Enforcement is three-layered and all three are mandatory:
  1. **`.gitignore`** carries the managed canonical block (`templates/gitignore.canonical`) so
     they are never tracked. Appended, not hand-maintained.
  2. **Docker caches live in named volumes**, and every cache-dir env var points **outside**
     the bind mount so nothing is written back into the mounted source:
     ```yaml
     # docker-compose: a container that bind-mounts the repo
     services:
       tests:
         user: "${UID:-1000}:${GID:-1000}" # host UID — NEVER `user: root`
         environment:
           PYTHONPYCACHEPREFIX: /caches/pycache
           RUFF_CACHE_DIR: /caches/ruff
           MYPY_CACHE_DIR: /caches/mypy
           PYTEST_ADDOPTS: -p no:cacheprovider # or PYTEST_CACHE_DIR under /caches
           npm_config_cache: /caches/npm
         volumes:
           - .:/code
           - tool-caches:/caches # named volume, persists across runs
           - node-modules:/code/node_modules # deps in a volume, shadowing the mount
     volumes:
       tool-caches:
       node-modules:
     ```
  3. **Any container that bind-mounts a repo runs as the host UID** (`user: "${UID}:${GID}"`),
     **never `user: root`** — root-owned artifacts written into a bind mount are unremovable
     without `sudo` and are treated as a defect. Root user is allowed only for containers with
     **no** repo bind mount (e.g. `.:/code` absent).
     Regenerable artifacts already in a repo are purged with `scripts/purge-artifacts.sh`.
- **Dockerfiles are multi-stage, with a `production` and a `dev` stage — mandatory.** Every
  application Dockerfile uses named build stages so a single file yields both runtime and
  developer images (`docker build --target production` / `--target dev`). Minimum stages:
  a shared `base` (interpreter + OS deps), a `builder`/`deps` (compiles/installs dependencies),
  a **`production`** target (slim runtime — no dev tooling, non-root `USER`, only the built
  artifact), and a **`dev`** target (production + test/lint/debug tooling, editable install,
  live-reload). A single-stage Dockerfile, or one missing either `production` or `dev`, is a
  defect. Compose services select the target explicitly (`build.target: production|dev|tests`).
  Canonical shape + Python 3.14 example: the `dockerfile-multistage` skill.
  _Exemption — container-collection repos:_ a repo whose product **is** a set of standalone
  utility/tool container images (e.g. `usefull-containers`), not one application, is exempt from the
  `production`+`dev` two-stage rule per image — each image is single-purpose. Such images still must
  not embed a reverse proxy and still run as non-root where they bind-mount host paths.
- **App containers ship the app only — the platform layer is the owner's responsibility.** An
  application image/container **never embeds a reverse proxy** (nginx/Traefik/Caddy/HAProxy as a
  TLS-terminating or routing front). The app container exposes its own port and speaks plain HTTP;
  routing, TLS, virtual hosts, and load-balancing live in the **platform layer** (the owner's
  Nginx/Traefik + Certbot on the host, or `deploy/k8s/` ingress), out of the app image. A static
  frontend may use a minimal internal web server to serve its own built assets, but it does **not**
  proxy other services. Baking a reverse proxy into an app container is a defect (couples the app to
  infra, duplicates the platform, and breaks the ownership boundary).
- **Dev stage must hot-reload.** The `dev` target/service provides live auto-reload so a source edit
  is reflected without a manual rebuild/restart: backend `uvicorn --reload` (or the framework's
  autoreload), frontend the dev server with HMR (`vite`/`npm run dev`), watched via the compose
  `develop.watch` sync or a source bind mount. A `dev` image identical to `production` (no reload) is
  not a dev image.

## Quality gates

- Test coverage **>= 85%** by default. A repo may override upward, never below 80%.
- Lint warnings: **0**. Mypy clean. SonarCloud rating **A**, 0 security hotspot.
- Max function lines 50 · max file lines 500 · cyclomatic complexity heuristic <= 10.

## Makefile targets

- **Referential**: `Forge-Stack-Workshop/base-makefile` (`Makefile.basic`, `Makefile.python`,
  `Makefile.with-sub-folder`) is the single source of truth for target names and behaviour.
- **Canonical naming** — follow base-makefile verbatim, one word where it is one word:
  `typecheck` (**never** `type-check`), `test-cov`, `format-check`, `quality-gate-verify`,
  `docker-test`, `ci`. Renaming or aliasing a canonical target is forbidden.
- **Mandatory socle** — every application repo MUST expose, with these exact names and intent:
  `help install install-dev lint format format-check typecheck test test-cov pre-commit clean
ci quality-gate-baseline quality-gate-verify`. Non-applicative repos (pure infra/Helm/Terraform,
  config-only, docs) are exempt from the language-specific targets (`typecheck`, `test-cov`) but
  still expose `help lint pre-commit clean`.
- **Docs must match** — every `make <target>` cited in `CLAUDE.md` or `README.md` MUST exist in
  the Makefile (no `make type-check` when the target is `typecheck`).
- **Recipe style** — prefix every recipe line with `@`; add `## Description` after each target so
  it appears in `make help`.

## Shared skills (load on demand from shared-standards/.claude/skills/)

- `testing-pytest` — pytest DDD + pytest-mock + constants (writing tests)
- `dockerfile-multistage` — 4-stage Python 3.14 containers (editing Dockerfile)
- `api-design` — REST standards + FastAPI patterns (designing endpoints)
- `async-patterns` — async FastAPI + SQLAlchemy async sessions (async code)
- `clean-architecture` — FastAPI module/layer structure (adding a feature)
- `error-handling` — FastAPI errors + Sentry + logging (handling errors)
- `contract-testing` — library contract / breaking-change tests (@chrysa/\* releases)
- `agent-patterns` — LangGraph + PydanticAI + Claude API (building agents)
- `ui-ux` — UX/UI/ergonomics + WCAG 2.1 AA + dark mode + i18n (human-facing surfaces)

## Error handling pattern (all automations)

```text
try:    fn()
except: gh issue create --title "[chrysa] failure" --label "chrysa-error"
```

## Observability — Sentry → GitHub issues (norm)

Every status:dev repo ships a Sentry project, and **a new Sentry issue automatically opens a
GitHub issue** via Sentry's native GitHub integration. No relay, no PAT in the repo — the
integration owns the link, so a Sentry issue maps to exactly one GitHub issue (no duplicates).

Mechanism: a per-project Sentry **issue alert rule** with
condition `FirstSeenEventCondition` (a new issue is created) and action
`GitHubCreateTicketAction` targeting `chrysa/<repo>`, labels `sentry`, `bug`.
Provision it across all projects with
`shared-standards/scripts/sentry-github-issues.sh` (idempotent, `--dry-run` first).

Per-project activation checklist:

1. Org GitHub integration installed once in Sentry (Settings → Integrations → GitHub) with
   access to the chrysa repos.
2. The repo has a Sentry project whose slug matches the repo name.
3. The auto-issue alert rule exists (run the provisioning script, or add it in
   Alerts → Create Alert → Issues → action "Create a GitHub issue").
4. The GitHub repo has a `sentry` label (CI label sync provides it).

## Governance — strategic pillars & ADR format

Five non-negotiables hold across every chrysa project, whatever the stack. Breaking one
requires an ADR with a kill-test, not a shrug.

1. **LLM-provider independence** — no vendor SDK in business code; inference goes through a
   local port with **≥2 real, tested adapters** (e.g. Claude + a local model). A prompt that
   only works on one vendor is a bug, not a feature.
2. **GAFAM independence** — every managed-cloud dependency has a documented self-hosted exit
   path; the cloud SDK stays confined to an adapter (`BlobStore`, not `S3Client`).
3. **Portable personalisation data** — all user/personal data is exportable to an open format
   (JSON/SQLite) by a documented command; `export → import → export` is idempotent (tested).
   A stored-but-unexportable field needs an ADR.
4. **k8s config in-project** — manifests live in `deploy/k8s/` of the repo; nothing exists
   only inside a running cluster.
5. **Adaptation layer** — no third-party lib/API/service is imported by the domain directly;
   it goes through an adapter whose port is written in the domain's language, not the vendor's.

**ADR format (refutable).** Any structural decision — new external dependency, LLM/cloud
provider choice, breaking public-API change, data-model change, or a pillar exception — gets
one ADR under `docs/adr/` (series named in the local `CLAUDE.md`). Beyond the classic fields,
every chrysa ADR carries three that make it falsifiable:

- **Fatal hypothesis** — the single, falsifiable belief whose falsity invalidates the decision.
  One only; about the real world (cost, latency, a third party), not an internal intention.
- **Kill-test** — the observable, dated signal that proves it wrong: what to measure, which
  threshold, when checked, what happens on breach. Mechanised as a test where possible.
- **Validation gate** — the pre-agreed condition that unlocks the next step, written _before_
  building.

`Killed` is a valid ADR status: the kill-test fired and the hypothesis was false. A corpus with
no `Killed` entry has kill-tests that are too lax. Scaffold a new record with `/adr-new`.

<!-- chrysa:standards:end -->
