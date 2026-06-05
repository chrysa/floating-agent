"""Chat widget — sends user input to the agent and shows the conversation.

Note: the responder runs synchronously on the UI thread. That is fine for the
offline StubClient; moving real LLM calls to a worker thread is a follow-up.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QLineEdit, QTextEdit, QVBoxLayout, QWidget

if TYPE_CHECKING:
    from collections.abc import Callable


class ChatWidget(QWidget):
    """Single-line prompt + scrolling transcript, backed by a responder callable."""

    def __init__(self, responder: Callable[[str], str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._responder = responder

        self._transcript = QTextEdit()
        self._transcript.setReadOnly(True)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Ask the agent…")
        self._input.returnPressed.connect(self.submit)

        layout = QVBoxLayout(self)
        layout.addWidget(self._transcript)
        layout.addWidget(self._input)

    def submit(self) -> None:
        """Send the current input to the responder and render the exchange."""
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self._append("You", text)
        self._append("Agent", self._responder(text))

    def _append(self, who: str, message: str) -> None:
        self._transcript.append(f"{who}: {message}")
