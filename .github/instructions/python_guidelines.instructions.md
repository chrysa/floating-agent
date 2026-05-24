---
applyTo: "**/*.py"
description: "Python coding guidelines"
---
# Python Guidelines

## Structure Rules (from Notion Engineering Standards 2026-05-21)

- **One class per file.** Each class lives in its own module (e.g. `models/user.py` contains only `User`).
- **Domain-driven structure.** Organise by domain (`connectors/`, `services/`, `schemas/`) — not by layer.
- **No `print()` in production.** Use `structlog` or `logging` with JSON formatter.
