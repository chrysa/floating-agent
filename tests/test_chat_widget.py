"""Tests for the overlay ChatWidget (responder runs on a Qt worker thread)."""

from __future__ import annotations

from floating_agent.overlay.widgets.chat_widget import ChatWidget


def test_chat_widget_renders_exchange(qtbot) -> None:
    widget = ChatWidget(responder=lambda msg: f"echo:{msg}")
    qtbot.addWidget(widget)
    widget._input.setText("hello")
    widget.submit()
    qtbot.waitUntil(lambda: "Agent: echo:hello" in widget._transcript.toPlainText())
    transcript = widget._transcript.toPlainText()
    assert "You: hello" in transcript
    assert widget._input.text() == ""
    assert widget._input.isEnabled()


def test_chat_widget_ignores_empty_input(qtbot) -> None:
    calls: list[str] = []
    widget = ChatWidget(responder=lambda msg: calls.append(msg) or "x")
    qtbot.addWidget(widget)
    widget._input.setText("   ")
    widget.submit()
    assert calls == []


def test_chat_widget_disables_input_while_pending(qtbot) -> None:
    widget = ChatWidget(responder=lambda msg: f"echo:{msg}")
    qtbot.addWidget(widget)
    widget._input.setText("hi")
    widget.submit()
    # Input is disabled synchronously, before the worker thread delivers its answer.
    assert not widget._input.isEnabled()
    qtbot.waitUntil(widget._input.isEnabled)


def test_chat_widget_reports_responder_error(qtbot) -> None:
    def boom(_msg: str) -> str:
        raise RuntimeError("aggregator down")

    widget = ChatWidget(responder=boom)
    qtbot.addWidget(widget)
    widget._input.setText("hello")
    widget.submit()
    qtbot.waitUntil(lambda: "[error] aggregator down" in widget._transcript.toPlainText())
    assert widget._input.isEnabled()
