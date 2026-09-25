# PRD — floating-agent

> Tags: FACT / INFERENCE / UNKNOWN / PROPOSAL. Grounded in `README.md`, `DECISIONS.md`, code.

## Product vision (FACT)

An open-source **floating multi-OS AI assistant** for Windows and Linux: a proactive
**whole-life agent** behind an always-on-top overlay. It reads/writes the user's Notion, sends
reminders, and acts across system monitoring, calendar, and messaging — without the user
leaving their current context.

## Positioning (FACT — README "Related Projects", DECISIONS D-0002)

- Depends on `chrysa/ai-aggregator` (AI routing backend).
- Boundary with `chrysa/lifeos` (assistant / "Jarvis" layer) is explicitly noted as needing
  reconciliation: D-0002 supersedes a prior "overlay only; agents live in LifeOS" arbitrage on
  the agent-scope point. **UNKNOWN**: the final, reconciled boundary.

## Product requirements (REQ-PROD)

| ID | Requirement | Status (verifiable?) | Evidence |
| --- | --- | --- | --- |
| REQ-PROD-001 | Always-on-top overlay surfacing chat + reminders | INFERENCE (code present; runtime unverified) | `overlay/window.py`, `overlay/widgets/` |
| REQ-PROD-002 | Read/write user's Notion (search + create task) | FACT (client + tools present) | `plugins/notion.py`, `agent/tools.py` |
| REQ-PROD-003 | Proactive reminders scheduled and delivered as notifications | INFERENCE | `proactive/scheduler.py`, `proactive/notifier.py` |
| REQ-PROD-004 | System monitoring (CPU/RAM/disk) surfaced in overlay | FACT (plugin + widget + model) | `plugins/system.py`, `models.py`, `overlay/widgets/system_widget.py` |
| REQ-PROD-005 | Calendar (upcoming events) + messaging (unread email) awareness | FACT (clients + tools) | `plugins/calendar.py`, `plugins/messaging.py` |
| REQ-PROD-006 | Emergent proactivity ("pulse") beyond explicit reminders | FACT (present, gated on AI config) | `proactive/pulse.py`, `overlay/app.py` |
| REQ-PROD-007 | Cross-OS (Windows + Linux) | PARTIAL / PLANNED | README platform table (Linux X11 in progress; rest planned) |
| REQ-PROD-008 | Agent writes require user confirmation | FACT | `agent/loop.py` confirmation gate |

## Non-goals / constraints (FACT)

- Not a passive dashboard — it is an acting agent (D-0002).
- The FastAPI HTTP layer is optional and localhost-only, not a public API.

## Success metrics

**UNKNOWN** — no metrics/telemetry definitions found in the repo.
