# DECISIONS — floating-agent

> Repository-local ADRs (Architectural Decision Records). Numbering: D-XXXX.
> Any deviation from [CODE_MANIFEST.md](../../CODE_MANIFEST.md) must be documented here.
> No active deviation → this project follows all chrysa global standards.

---

## D-0001 — Adherence to chrysa global standards

**Date**: 2026-04-29
**Status**: accepted

This project follows all conventions defined in `CODE_MANIFEST.md` (chrysa portfolio standards).
No active deviation is in effect. Any future deviation must be added as a new ADR entry below.

---

## D-0002 — Drop Electron + React; native PySide6 overlay; whole-life agent scope

**Date**: 2026-06-04
**Status**: accepted

**Context.** The shell was Electron (contextIsolation + React renderer) talking to a Python
FastAPI daemon over `127.0.0.1:34001`. Two problems drove a rethink: (1) Electron's weight
(~200 MB bundle, ~150 MB RAM) for a lightweight always-on-top overlay, and (2) the product is
not a passive dashboard but a **proactive whole-life assistant agent** (reads/writes Notion,
sends reminders, acts), which a thin AI-access overlay does not capture.

**Decision.**

1. **Remove Electron and the React UI.** The shell becomes a **native PySide6 (Qt) overlay** in a
   single Python process — cross-OS (Windows + Linux), frameless, always-on-top, transparent.
2. **The Python daemon plugins/models become the reusable core** (`floating_agent/`), called
   directly by the overlay. The FastAPI HTTP layer becomes optional (kept behind a `--serve` flag).
3. **Scope is a whole-life agent**: tool-calling loop + proactive engine (scheduler + OS
   notifications), Notion R/W, proactivity delivered in two phases (explicit reminders → emergent).
4. **Repo restructured**: `daemon/floating_agent` → root `floating_agent/`, `daemon/tests` → root
   `tests/`, `pyproject.toml` at repo root (this also fixes CI: `install-project` runs at root).
5. **Ruff `target-version` pinned to `py313`** — `ruff format` on `py314` strips except-clause
   parens (known bug affecting ~20 chrysa repos).

**Consequences.** The 2026-05-12 Notion arbitrage (floating-agent = overlay only; agents live in
LifeOS) is superseded on the agent-scope point — the floating-agent ↔ LifeOS boundary must be
re-arbitrated. Toolkit choice: PySide6 (LGPL) over PyQt6 (GPL) for licensing.
