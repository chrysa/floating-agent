"""Read-only Outbox surface for durable local actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget

from floating_agent.domain.outbox_status import OutboxStatus

if TYPE_CHECKING:
    from floating_agent.domain.outbox_item import OutboxItem
    from floating_agent.ports.outbox import Outbox


class OutboxWidget(QWidget):
    """Show the current durable action backlog and recent statuses."""

    def __init__(self, outbox: Outbox | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._outbox = outbox
        self._title = QLabel("Outbox")
        self._summary = QLabel()
        self._summary.setWordWrap(True)
        self._details = QTextEdit()
        self._details.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self._title)
        layout.addWidget(self._summary)
        layout.addWidget(self._details)

        self.refresh()

    def refresh(self) -> None:
        """Refresh the visible backlog state from the persisted Outbox."""
        if self._outbox is None:
            self._summary.setText("No local outbox configured.")
            self._details.setText("Durable actions will appear here once the store is wired in.")
            return

        items = list(self._outbox.list_by_status(set(OutboxStatus)))
        counts = dict.fromkeys(OutboxStatus, 0)
        for item in items:
            counts[item.status] += 1
        self._summary.setText(
            " | ".join(f"{status.value} {counts[status]}" for status in OutboxStatus)
        )
        self._details.setText(
            "\n".join(_format_item(item) for item in items[:5]) or "No pending durable actions."
        )


def _format_item(item: OutboxItem) -> str:
    error = "" if item.last_error is None else f" · {item.last_error}"
    return (
        f"{item.status.value}: {item.provider}/{item.action_type} on {item.resource_type}:{item.resource_id}"
        f" (attempts {item.attempt_count}){error}"
    )
