"""Tests for the overlay ChatWidget."""

from __future__ import annotations

from typing import TYPE_CHECKING

from floating_agent.overlay.widgets.chat_widget import ChatWidget

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


def test_chat_widget_renders_exchange(qtbot: QtBot) -> None:
    widget = ChatWidget(responder=lambda msg: f"echo:{msg}")
    qtbot.addWidget(widget)
    widget._input.setText("hello")
    widget.submit()
    transcript = widget._transcript.toPlainText()
    assert "You: hello" in transcript
    assert "Agent: echo:hello" in transcript
    assert widget._input.text() == ""


def test_chat_widget_ignores_empty_input(qtbot: QtBot) -> None:
    calls: list[str] = []

    def responder(msg: str) -> str:
        calls.append(msg)
        return "x"

    widget = ChatWidget(responder=responder)
    qtbot.addWidget(widget)
    widget._input.setText("   ")
    widget.submit()
    assert calls == []
