---
name: pytest-qt-widgets
description: 'Use when writing or reviewing widget tests under tests/ that need pytest-qt (qtbot fixture) instead of plain pytest, e.g. testing floating_agent/overlay/ components.'
---

# pytest-qt widget tests — floating-agent

## When to invoke
Auto-invoke when: adding a test for a `QWidget`/`QMainWindow` subclass,
reviewing a test that imports `qtbot`, or a test needs to simulate a click/
keypress/signal on a Qt widget.

## Required env

Every widget test run — locally and in CI — needs:

```bash
QT_QPA_PLATFORM=offscreen pytest tests/ -k widget
```

`make test` already exports this; running `pytest` directly on the host
without it will hang or fail to create a `QApplication` on a machine with no
display server.

## `qtbot` basics

```python
def test_overlay_toggle_visibility(qtbot):
    widget = OverlayWindow()
    qtbot.addWidget(widget)  # ensures teardown/close after the test

    assert not widget.isVisible()
    widget.show()
    qtbot.waitExposed(widget)
    assert widget.isVisible()
```

- `qtbot.addWidget(widget)` is mandatory — without it Qt objects leak between
  tests and later tests intermittently segfault.
- `qtbot.waitExposed(widget)` / `qtbot.waitUntil(callback)` over a bare
  `time.sleep()` — event-loop-aware waiting, no flaky fixed delays.
- `qtbot.mouseClick(widget, Qt.MouseButton.LeftButton)` and
  `qtbot.keyClicks(widget, "text")` to simulate input instead of calling the
  widget's internal slot directly — exercises the real signal/slot wiring.

## Signals

```python
def test_agent_reply_updates_label(qtbot):
    widget = OverlayWindow()
    with qtbot.waitSignal(widget.reply_received, timeout=1000):
        widget.on_agent_reply("hello")
    assert widget.reply_label.text() == "hello"
```

Use `qtbot.waitSignal` to assert a signal actually fires, not just that the
slot's side effect happened — catches wiring regressions a pure state
assertion misses.

## Scope

- Core agent-loop logic (non-Qt) stays in plain pytest — don't pull `qtbot`
  into tests that don't touch a widget.
- One `QApplication` per test session (pytest-qt provides this automatically
  via its `qapp` fixture) — never construct `QApplication` manually in a test.
