# Tests

**Role.** This folder contains unit, integration, and Qt tests for floating-agent.

## Structure

- `test_agent.py` and related modules cover the application core and adapters.
- `test_overlay.py` and `test_chat_widget.py` cover the PySide6 interface.

## Running tests

Use `make test` for the canonical containerized suite or `make test-cov` for a
local coverage report through the locked `uv` environment.
