"""Tests for the overlay ChatWidget."""

from __future__ import annotations

from floating_agent.overlay.widgets.chat_widget import ChatWidget


def test_chat_widget_renders_exchange(qtbot) -> None:
    widget = ChatWidget(responder=lambda msg: f"echo:{msg}")
    qtbot.addWidget(widget)
    widget._input.setText("hello")
    widget.submit()
    transcript = widget._transcript.toPlainText()
    assert "You: hello" in transcript
    assert "Agent: echo:hello" in transcript
    assert widget._input.text() == ""


def test_chat_widget_ignores_empty_input(qtbot) -> None:
    calls: list[str] = []
    widget = ChatWidget(responder=lambda msg: calls.append(msg) or "x")
    qtbot.addWidget(widget)
    widget._input.setText("   ")
    widget.submit()
    assert calls == []
