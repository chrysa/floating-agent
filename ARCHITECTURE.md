# ARCHITECTURE — floating-agent

> Tags: FACT (verified in code/config), INFERENCE (reasoned from evidence),
> UNKNOWN (not determinable from the repo). Never promote INFERENCE to FACT.

## Overview

**FACT.** floating-agent is a single-process Python application: a native **PySide6 (Qt)**
always-on-top overlay driving a **tool-calling agent core**, plus a **proactive engine**
(scheduler + notifier). An **optional FastAPI HTTP layer** (behind `--serve`) exposes system
monitoring to other chrysa tools. Electron + React were removed (see `DECISIONS.md` D-0002).

Evidence: `README.md`, `floating_agent/overlay/app.py`, `floating_agent/main.py`, `DECISIONS.md`.

## Component map (FACT)

| Layer | Module | Responsibility |
| --- | --- | --- |
| Entrypoint | `floating_agent/__main__.py`, `overlay/app.py` (`run()`) | Boots QApplication, wires agent + scheduler + pulse, runs Qt event loop |
| Overlay UI | `overlay/window.py`, `overlay/tray.py`, `overlay/widgets/` (`chat_widget.py`, `system_widget.py`, `async_responder.py`) | Always-on-top window, system tray, chat + system widgets |
| Agent core | `agent/loop.py` | Tool-calling loop: `prompt → (tool calls → results)* → final answer`; confirmation gate |
| LLM client | `agent/client.py` | `AggregatorClient` (HTTP → ai-aggregator `/v1/messages`), `StubClient` offline fallback |
| Tools | `agent/tools.py` | Tool registry + specs; system / Notion / reminder / calendar / messaging tools |
| Plugins | `plugins/system.py`, `plugins/notion.py`, `plugins/calendar.py`, `plugins/messaging.py` | Integrations: psutil stats, Notion REST R/W, Google Calendar, Gmail unread |
| Proactive | `proactive/scheduler.py`, `proactive/reminders.py`, `proactive/pulse.py`, `proactive/notifier.py` | Reminder store + scheduler tick, emergent "pulse" decider, OS notifications |
| Secrets | `secret_store.py` | `SecretStore`: OS keychain (keyring) first, env var fallback |
| HTTP (opt.) | `main.py`, `api/routers/health.py`, `api/routers/system.py` | FastAPI app on `127.0.0.1:34001`, localhost-only |
| API schemas | `models.py` | Pydantic `SystemStats` and related response models |

## Runtime wiring (FACT — from `overlay/app.py::run()`)

1. `QApplication` created; `setQuitOnLastWindowClosed(False)` (lives in tray).
2. `ReminderStore` + `build_default_agent(reminder_store=...)` constructed.
3. `OverlayWindow(agent=...)` shown; tray built; `TrayNotifier` wraps the tray.
4. `ReminderScheduler` ticked by a `QTimer` (`_TICK_MS`) via `scheduler.tick(datetime.now())`.
5. Phase-2 emergent proactivity: `ProactivePulse(_build_decider(), notifier)` ticked by a
   second `QTimer` (`_PULSE_MS`) over `build_snapshot(system_plugin, store)`.
6. `_build_decider()` returns `NullDecider` unless `AI_AGGREGATOR_URL` is set, then `LLMDecider`.

## Agent loop (FACT — `agent/loop.py`)

- Bounded by `MAX_STEPS`; returns a "reached the maximum number of tool-calling steps" message
  if exceeded.
- A tool with `requires_confirmation=True` is **denied by default**; it runs only when a
  confirmation callback (`_confirm`) approves it. Unknown tool names return an error string.
- `LLMClient` is a Protocol (`complete(messages, tools) -> LLMResponse`). Implementations:
  `AggregatorClient` (HTTP) and `StubClient` (offline echo until `AI_AGGREGATOR_URL` is set).

## Data flow (INFERENCE)

Overlay chat input → `AgentLoop.run(user_message)` → `LLMClient.complete()` → optional tool
calls executed against plugins → final text rendered in the overlay. Proactive path: timers →
scheduler/pulse → `Notifier` → OS/tray notification. No local database observed; `ReminderStore`
appears in-memory (UNKNOWN whether persisted — no persistence layer found in the read modules).

## External integrations (FACT)

| Integration | Transport | Secret (via `SecretStore`) |
| --- | --- | --- |
| ai-aggregator | HTTP `POST {AI_AGGREGATOR_URL}/v1/messages` | `AI_AGGREGATOR_URL` |
| Notion | REST `https://api.notion.com/v1` (version `2022-06-28`) | `NOTION_API_KEY`, `NOTION_TASKS_DB_ID` |
| Google Calendar | HTTP (client in `plugins/calendar.py`) | `CALENDAR_ACCESS_TOKEN` |
| Gmail | HTTP (client in `plugins/messaging.py`) | `GMAIL_ACCESS_TOKEN` |

Network methods in the Notion/calendar/messaging clients are integration-only
(`# pragma: no cover`).

## Optional HTTP layer (FACT — `main.py`)

- FastAPI app `Floating Agent Daemon` v`0.1.0`, port `34001`, `docs_url=/docs`.
- CORS restricted to `http://localhost:5173`, credentials off, methods `GET`/`POST`.
- Routers: `/health`, `/system`.
- Comment states it is "never exposed externally" (localhost only).

## Platform support (FACT — README, "🚧/📋" status)

Linux X11 in progress; Linux Wayland (`wlr-layer-shell`) and Windows 10/11 (Win32) planned.
