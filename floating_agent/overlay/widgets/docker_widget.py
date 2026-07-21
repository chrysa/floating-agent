"""Compact local Docker lifecycle activity view."""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from floating_agent.domain.container_event_kind import ContainerEventKind

if TYPE_CHECKING:
    from collections.abc import Iterable

    from floating_agent.domain.container_lifecycle_event import ContainerLifecycleEvent

_MAX_VISIBLE_EVENTS = 5
_EVENT_LABELS = {
    ContainerEventKind.STARTED: "started",
    ContainerEventKind.RESTARTED: "restarted",
    ContainerEventKind.STOPPED: "stopped",
    ContainerEventKind.CRASHED: "crashed",
}


class DockerWidget(QWidget):
    """Display recent Docker starts, restarts, stops, and crashes."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._events: deque[ContainerLifecycleEvent] = deque(maxlen=_MAX_VISIBLE_EVENTS)
        self._title = QLabel("Docker activity")
        self._activity = QLabel("No recent lifecycle event")
        self._activity.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self._title)
        layout.addWidget(self._activity)

    def add_events(self, events: Iterable[ContainerLifecycleEvent]) -> None:
        """Append lifecycle events and refresh the compact history."""
        self._events.extend(events)
        if not self._events:
            return
        lines = [f"{event.container_name}: {_EVENT_LABELS[event.kind]}" for event in reversed(self._events)]
        self._activity.setText("\n".join(lines))
