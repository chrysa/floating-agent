# Architecture — floating-agent

> Floating Multi-OS AI Assistant. Grounded in the repository's manifests and source;
> where README and `pyproject.toml` disagree, the manifest wins (noted inline).

## Purpose

An open-source, always-on-top floating AI assistant for **Windows** and **Linux**. It runs
as a single Python process: a native PySide6 (Qt) overlay over a tool-calling agent core.
A proactive engine (scheduler + notifier) can wake the agent to surface reminders. Tools
reach Notion (read/write), system metrics, calendar and messaging, and AI via the
`chrysa/ai-aggregator` backend. An optional FastAPI HTTP layer exposes the agent to other
chrysa tools. (An earlier Electron/React UI was removed — see `DECISIONS.md`.)

## Stack

- **Language/runtime:** Python (`requires-python >=3.14`; README's "Python 3.14" agrees).
- **UI shell:** PySide6 (Qt) ≥6.8 — native overlay.
- **HTTP (optional):** FastAPI ≥0.115 + Uvicorn (`--serve`).
- **System info:** psutil ≥6.0. **HTTP client:** httpx. **Models:** Pydantic v2 + pydantic-settings.
- **Secrets:** `keyring` (OS keychain) with env-var fallback.
- **Tests:** pytest + pytest-qt (+ pytest-asyncio, pytest-cov). **Lint/type:** Ruff, mypy (strict).
- **Packaging:** PyInstaller (spec at `packaging/floating-agent.spec`).
- **Build backend:** setuptools (`build-system` in `pyproject.toml`).

## Layout

- `floating_agent/` — application package.
  - `__main__.py` — `python -m floating_agent` entry; calls `overlay.app.run()`.
  - `main.py` — optional FastAPI app (`--serve`), localhost `127.0.0.1:34001`.
  - `models.py`, `secret_store.py` — shared models and `SecretStore` (keyring/env).
  - `overlay/` — `app.py`, `window.py`, `tray.py`, and `widgets/` (chat, system, async responder).
  - `agent/` — `loop.py` (tool-call loop), `tools.py`, `client.py`.
  - `plugins/` — `notion.py`, `system.py`, `calendar.py`, `messaging.py`.
  - `proactive/` — `scheduler.py`, `pulse.py`, `notifier.py`, `reminders.py`.
  - `api/routers/` — `health.py`, `system.py`.
- `tests/` — pytest suite (agent, overlay, plugins, proactive, secret store, health, ...).
- `scripts/` — `quality_gate.py`, `gen_context_files.py`.
- `packaging/` — PyInstaller spec. `makefiles/` — Makefile includes. `docs/`, `standards/`.

## Entrypoints

- **Overlay (primary):** `python -m floating_agent` → `floating_agent/overlay/app.py:run()`.
- **HTTP layer (optional):** FastAPI `app` in `floating_agent/main.py`, served via Uvicorn
  on `127.0.0.1:34001` (localhost only). Routers: `/health`, `/system`; docs at `/docs`.
- No `[project.scripts]` console entrypoint is declared in `pyproject.toml`.

## Data / External dependencies

- **AI:** `chrysa/ai-aggregator` (HTTP) via the agent client — provider AI routing backend.
- **Notion:** read/write through the Notion plugin; a Notion MCP server is configured in `.mcp.json`.
- **System:** local host metrics via psutil.
- **Calendar / Messaging:** plugin integrations (see `plugins/`).
- **Secrets:** OS keychain via `keyring` (`SecretStore`), env-var fallback for headless/CI.
- Agent writes flagged `requires_confirmation` are denied unless an explicit confirmation
  callback approves them. Persistent database: N/A — not present in repo.

## Build & test (real commands)

Targets are defined in the `Makefile`:

```bash
make install     # install python deps + pre-commit hooks
make dev         # launch the PySide6 overlay (python -m floating_agent)
make serve       # (optional) FastAPI HTTP layer on 127.0.0.1:34001
make test        # run tests in Docker (alias: make docker-test)
make test-cov    # tests with coverage report
make lint        # Ruff
make typecheck   # mypy (strict)
make build       # PyInstaller standalone binary for current OS
make pre-commit  # run all pre-commit hooks
make ci          # lint + typecheck + test
```

Coverage gate: `--cov-fail-under=85` (see `[tool.pytest.ini_options]` in `pyproject.toml`).
A container test image is defined in `Dockerfile.test`.
