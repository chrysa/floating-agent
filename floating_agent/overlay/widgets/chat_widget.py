"""Chat widget — sends user input to the agent and shows the conversation.

The responder runs on a Qt worker thread (see :mod:`async_responder`) so a blocking
real LLM call never freezes the always-on-top overlay. Input is disabled while a
response is pending and re-enabled when the answer (or an error) comes back.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QThreadPool
from PySide6.QtWidgets import QLineEdit, QTextEdit, QVBoxLayout, QWidget

from floating_agent.overlay.widgets.async_responder import ResponderTask

if TYPE_CHECKING:
    from collections.abc import Callable

_IDLE_PLACEHOLDER = "Ask the agent…"
_PENDING_PLACEHOLDER = "Thinking…"


class ChatWidget(QWidget):
    """Single-line prompt + scrolling transcript, backed by a responder callable."""

    def __init__(self, responder: Callable[[str], str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._responder = responder
        self._pool = QThreadPool.globalInstance()

        self._transcript = QTextEdit()
        self._transcript.setReadOnly(True)

        self._input = QLineEdit()
        self._input.setPlaceholderText(_IDLE_PLACEHOLDER)
        self._input.returnPressed.connect(self.submit)

        layout = QVBoxLayout(self)
        layout.addWidget(self._transcript)
        layout.addWidget(self._input)

    def submit(self) -> None:
        """Send the current input to the responder on a worker thread and render it."""
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self._append("You", text)
        self._set_pending(True)

        task = ResponderTask(self._responder, text)
        task.signals.succeeded.connect(self._on_answer)
        task.signals.failed.connect(self._on_error)
        self._pool.start(task)

    def _append(self, who: str, message: str) -> None:
        self._transcript.append(f"{who}: {message}")

    def _on_answer(self, answer: str) -> None:
        self._append("Agent", answer)
        self._set_pending(False)

    def _on_error(self, message: str) -> None:
        self._append("Agent", f"[error] {message}")
        self._set_pending(False)

    def _set_pending(self, pending: bool) -> None:
        self._input.setEnabled(not pending)
        self._input.setPlaceholderText(_PENDING_PLACEHOLDER if pending else _IDLE_PLACEHOLDER)
