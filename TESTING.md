# TESTING — floating-agent

> Tags: FACT / INFERENCE / UNKNOWN. Grounded in `Makefile`, `Dockerfile.test`,
> `pyproject.toml`, `tests/`.

## How to run (FACT — `Makefile`)

| Command | Effect |
| --- | --- |
| `make test` | Build `Dockerfile.test` and run pytest in Docker (chrysa standard) |
| `make docker-test` | Alias of `make test` |
| `make test-cov` | `pytest --cov=floating_agent --cov-report=term-missing --cov-report=xml` (host) |
| `make lint` | Ruff |

**FACT.** `Dockerfile.test` uses `python:3.14-slim`, installs Qt runtime libs for headless
PySide6, installs `-e ".[dev]"`, runs as non-root `appuser`, sets `QT_QPA_PLATFORM=offscreen`,
and defaults to `pytest --tb=short -q`.

## Pytest configuration (FACT — `pyproject.toml`)

- `addopts = "-p no:django -p no:query_optimizer --cov=floating_agent --cov-report=xml
  --cov-report=term-missing --cov-fail-under=85"`.
- **Coverage gate: 85% minimum** (`--cov-fail-under=85`).
- `pytest-asyncio` and `pytest-qt` are dev dependencies (Qt widget tests supported).

## Test inventory (FACT — `grep -c "def test_"`)

| File | Test count |
| --- | --- |
| `tests/test_agent.py` | 9 |
| `tests/test_notion.py` | 6 |
| `tests/test_calendar_messaging.py` | 5 |
| `tests/test_pulse.py` | 4 |
| `tests/test_chat_widget.py` | 4 |
| `tests/test_overlay.py` | 4 |
| `tests/test_secret_store.py` | 4 |
| `tests/test_proactive.py` | 3 |
| `tests/test_system.py` | 2 |
| `tests/test_health.py` | 1 |
| **Total** | **42** |

## Coverage strategy (INFERENCE)

Live-network methods (Notion/calendar/messaging clients) and Qt-live paths carry
`# pragma: no cover`, so the 85% gate is met against the offline/logic surface. Tests fake the
LLM client (`StubClient`) and plugin clients.

## Not verified

**UNKNOWN.** This documentation task did not execute the suite (docs-only mission). The
pass/fail state and actual coverage number are not confirmed here.
