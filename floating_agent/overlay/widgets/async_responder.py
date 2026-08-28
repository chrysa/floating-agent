"""Run a blocking responder off the Qt UI thread and deliver the result via signals.

A real LLM call (``AggregatorClient``) does a blocking HTTP request up to its timeout.
Calling it directly inside ``ChatWidget.submit`` would freeze the always-on-top overlay
for the whole request. ``ResponderTask`` wraps the responder in a ``QThreadPool`` task
that runs on a worker thread and emits the answer (or the error) back on the UI thread.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QRunnable, Signal

if TYPE_CHECKING:
    from collections.abc import Callable


class ResponderSignals(QObject):
    """Signals emitted by a :class:`ResponderTask` (a ``QRunnable`` cannot own signals)."""

    failed = Signal(str)
    succeeded = Signal(str)


class ResponderTask(QRunnable):
    """Runs ``responder(prompt)`` in a worker thread, emitting the result on the UI thread."""

    def __init__(self, responder: Callable[[str], str], prompt: str) -> None:
        super().__init__()
        self._prompt = prompt
        self._responder = responder
        self.signals = ResponderSignals()

    def run(self) -> None:
        """Execute the responder; forward its answer or any failure to the UI thread."""
        try:
            answer = self._responder(self._prompt)
        except Exception as exc:  # thread boundary: forward failure to the UI, never crash the pool
            self.signals.failed.emit(str(exc))
            return
        self.signals.succeeded.emit(answer)
