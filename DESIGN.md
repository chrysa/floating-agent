# floating-agent — Design contract

> Contract for the native overlay: the floating window, its tray menu and its tray notifications.
> Rule: `standards/rules/design.md` · method and acceptance criteria:
> `shared-standards/docs/DESIGN-CONTRACT.md`. Read it before changing a window, widget, tray entry,
> notification, shortcut or asset, and update it in the same change.
>
> Status: **[implemented]** links the code · **[decided]** names the decision · **[proposed]** is
> not agreed. This file documents the current overlay; it does not redesign it.

## 1. Surface and status

- **Surface:** native overlay app — a PySide6 (Qt) window that is frameless, always on top,
  translucent and fixed at 320 × 420 px, plus a system-tray menu and tray balloon notifications.
  **[implemented]** ([window.py](floating_agent/overlay/window.py),
  [tray.py](floating_agent/overlay/tray.py), [app.py](floating_agent/overlay/app.py)). The optional
  FastAPI layer ([main.py](floating_agent/main.py)) has no human-facing surface.
- **Lifecycle:** prototype. Native PySide6 replaced Electron and React (D-0002, 2026-06-04) and
  PyInstaller packaging is decided (D-0003) — see [DECISIONS.md](DECISIONS.md). **[decided]**
  Linux X11 is in progress; Wayland and Windows are planned ([README.md](README.md)).
- **Detailed specs:** none.

## 2. Users, devices and priority tasks

| User                          | Context and device                                                                        | Priority tasks                                                                                                                                              |
| ----------------------------- | ----------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The owner, at the workstation | Desktop (Linux X11 today), overlay floating above other work, glanced at many times a day | 1. ask the agent a quick question without leaving the current app · 2. glance at CPU, RAM and disk · 3. receive reminders, then hide or recover the overlay |

Primary action: the chat input line at the bottom of the window.

## 3. Journeys and navigation

- **J1 — Ask:** type in the input → Enter → `You: …` is appended → input disabled with the
  placeholder "Thinking…" → `Agent: …` is appended and the input is enabled again. Failure:
  `Agent: [error] <message>` and the input is enabled again. Without `AI_AGGREGATOR_URL` the stub
  client answers that AI routing is not configured. **[implemented]**
  ([chat_widget.py](floating_agent/overlay/widgets/chat_widget.py),
  [async_responder.py](floating_agent/overlay/widgets/async_responder.py),
  [client.py](floating_agent/agent/client.py))
- **J2 — Glance:** three labels refresh every 2 s: `CPU n%`, `RAM used/total GB`, `Disk n%`.
  **[implemented]** ([system_widget.py](floating_agent/overlay/widgets/system_widget.py))
- **J3 — Be reminded:** the reminder scheduler ticks every 30 s and the proactive pulse every
  5 min; due items appear as tray balloons. The pulse stays silent unless AI is configured.
  **[implemented]** ([app.py](floating_agent/overlay/app.py),
  [notifier.py](floating_agent/proactive/notifier.py))
- **J4 — Move, hide, recover:** drag the window body with the left button; the tray menu offers
  "Show / Hide" and "Quit"; closing the window does not quit the app. **[implemented]**
- **Confirm a sensitive action:** tools flagged `requires_confirmation` (today
  `notion_create_task`) are denied because the overlay passes no confirmation callback
  ([loop.py](floating_agent/agent/loop.py), [tools.py](floating_agent/agent/tools.py)). There is no
  confirmation dialog yet. **[implemented]** deny-by-default; the dialog is a gap (§11).
- **Information architecture:** one window with two stacked widgets (system readout above chat);
  one tray menu with two actions. No settings, reminder list or history view.
- **Density:** compact — a fixed small window meant to stay out of the way.

## 4. Identity

No identity has been chosen. The overlay uses default Qt widgets and the platform palette and
font; no stylesheet, palette, font or icon is set anywhere in `floating_agent/`. **[implemented]**
A brand brief, the signature element and the visual direction are open choices (§11).

## 5. Tokens and components (owned elsewhere)

| Concern                 | Source of truth                                                                                                                                               | Rules of use                                                 |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Colour roles and themes | platform Qt palette (none set in code)                                                                                                                        | follow the OS light or dark theme until a palette is decided |
| Typography              | platform default font                                                                                                                                         | no size or weight overrides                                  |
| Window geometry         | [window.py](floating_agent/overlay/window.py) `setFixedSize(320, 420)`                                                                                        | fixed size, no resize                                        |
| Spacing                 | Qt `QVBoxLayout` defaults                                                                                                                                     | no custom margins                                            |
| Timing                  | `POLL_INTERVAL_MS` in [system_widget.py](floating_agent/overlay/widgets/system_widget.py); `_TICK_MS`, `_PULSE_MS` in [app.py](floating_agent/overlay/app.py) | one named constant per interval                              |
| Motion                  | none                                                                                                                                                          | —                                                            |
| Components              | Qt widgets: read-only `QTextEdit` transcript, `QLineEdit`, `QLabel`, `QSystemTrayIcon`, `QMenu`                                                               | native controls; no custom painting                          |

- **Shared contract:** `contract.css` and `@chrysa/ui` do not apply to a Qt surface.
- **Design debt and drift:** the README describes a whole-life agent (Notion writes, reminders,
  calendar); the overlay shows only chat and system stats, with no reminder view and no
  confirmation dialog.

## 6. Interaction and states

- **Component states:** native Qt focus and disabled states; the input is disabled while a
  response is pending. **[implemented]**
- **Action feedback:** the "Thinking…" placeholder while pending; `[error]` prefix on failure.
- **Forms:** one line; empty input is ignored. The input is cleared on submit, so after an error
  the text survives only in the transcript, not in the field.
- **Data states:**

  | State                         | Where it appears | Behaviour                                                                              |
  | ----------------------------- | ---------------- | -------------------------------------------------------------------------------------- |
  | Loading                       | chat             | input disabled, placeholder "Thinking…"                                                |
  | Empty                         | chat             | empty transcript; only the placeholder "Ask the agent…" guides                         |
  | Error                         | chat             | `[error]` plus the raw exception text, which may not say what to do                    |
  | Error                         | system readout   | none: a failing stats call is not caught in the timer slot                             |
  | Offline / backend unreachable | chat             | stub reply when AI is not configured; otherwise an error line; no persistent indicator |
  | Stale data                    | system readout   | no timestamp or age                                                                    |
  | Reconnect                     | —                | none                                                                                   |

- **Real-time:** the system labels update in place every 2 s in a separate widget from the chat,
  so typing is not interrupted. Transcript scroll behaviour on append is not verified.
- **Motion:** none, no entrance for the window or new transcript lines (FE-053). When motion is
  added it uses Qt property animation on opacity or position and honours the OS reduce-motion
  setting. **[proposed]**

## 7. Responsive and support conventions

Frameless `Tool` window: no taskbar entry, always on top, moved by dragging, not resizable.
Position is not remembered between runs. Multi-monitor, HiDPI scaling and Wayland behaviour are not
tested; Wayland needs `wlr-layer-shell` (planned). Keep native Qt controls and the platform tray;
do not impose browser layouts or web-only criteria.

## 8. Accessibility

- **Target:** the platform accessibility API through Qt Accessibility (AT-SPI on Linux, UI
  Automation on Windows) — not web WCAG certification.
- **Keyboard:** Enter submits; there is no global shortcut to show, hide or focus the overlay, and
  the window can only be moved with the mouse. Keyboard focus for a frameless `Tool` window is not
  verified on each window manager.
- **Perception:** stats are text, not colour. Readability of the translucent window over light and
  dark desktops is not verified.
- **Assistive technology:** no accessible names are set on widgets; new answers are not announced.

## 9. Assets

| Asset             | Source or generator                                                                                        | Author | Licence and attribution | Permitted use | Formats and variants | Location |
| ----------------- | ---------------------------------------------------------------------------------------------------------- | ------ | ----------------------- | ------------- | -------------------- | -------- |
| Tray and app icon | none: `QIcon()` is empty ([tray.py](floating_agent/overlay/tray.py)); the PyInstaller spec bundles no data | —      | —                       | —             | —                    | —        |

No fonts or images ship. PySide6 (LGPL, D-0002) is a runtime dependency, not an asset.

## 10. Acceptance criteria and evidence

- **Criteria:** the overlay can always be recovered from the tray; it does not steal focus when it
  shows or notifies; chat pending, answer and error are visible and the input works by keyboard
  alone; text stays readable on light and dark desktops; the window stays on screen after a move.
- **Existing tests:** pytest-qt checks window flags, drag, tray toggle, stats rendering and chat
  pending, empty and error paths ([test_overlay.py](tests/test_overlay.py),
  [test_chat_widget.py](tests/test_chat_widget.py)).
- **Evidence log:**

  | Date       | Change                         | Checks run                                                               | Result             | Not run, and why                                                                |
  | ---------- | ------------------------------ | ------------------------------------------------------------------------ | ------------------ | ------------------------------------------------------------------------------- |
  | 2026-11-08 | contract written from the code | source review of `floating_agent/overlay` and `floating_agent/proactive` | gaps listed in §11 | no browser run: documentation-only change (the overlay was not launched either) |

## 11. Open choices, known gaps and maintenance

- **Open choices:**
  - Choose an identity with a brand brief, then hold its palette and fonts in one Qt stylesheet
    module. Rationale: a translucent window needs explicit contrast. **[proposed]**
  - Add a confirmation dialog for `requires_confirmation` tools, showing the tool and its
    arguments with explicit accept and decline. Rationale: today such tools can never run.
    **[proposed]**
  - Add a global show/hide shortcut and remember the window position. **[proposed]**
- **Known gaps:**
  - Empty tray icon: on some desktops the tray entry is invisible, so a hidden overlay can be lost.
  - Translucent background with no painted surface: contrast depends on the desktop behind it.
  - Raw exception text in chat errors; no persistent offline or AI-unconfigured indicator.
  - System readout has no error handling and no stale indicator.
  - No accessible names, no keyboard move, no entrance motion.
  - Input text is cleared before the answer, so it cannot be edited and resent after an error.
- **Maintenance:** owner chrysa. Update this file with every change to the overlay, tray,
  notifications or assets; review it when Windows or Wayland support lands.
