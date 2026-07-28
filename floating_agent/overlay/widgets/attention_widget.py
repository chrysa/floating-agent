"""Unified attention surface for locally cached content."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

if TYPE_CHECKING:
    from floating_agent.domain.calendar_event import CalendarEvent
    from floating_agent.domain.communication_message import CommunicationMessage
    from floating_agent.domain.mail_message import MailMessage
    from floating_agent.ports.local_store import LocalStore


class AttentionWidget(QWidget):
    """Show locally cached mail, calendar, and communication activity."""

    def __init__(self, store: LocalStore | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._store = store
        self._title = QLabel("Attention")
        self._summary = QLabel()
        self._summary.setWordWrap(True)
        self._detail = QLabel()
        self._detail.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self._title)
        layout.addWidget(self._summary)
        layout.addWidget(self._detail)

        self.refresh()

    def refresh(self) -> None:
        """Refresh the visible summary from the local store."""
        if self._store is None:
            self._summary.setText("No local content store configured.")
            self._detail.setText("Offline content will appear here once a store is wired in.")
            return

        mails = list(self._store.list_mail())
        calendar_events = list(self._store.list_calendar_events())
        communications = list(self._store.list_communications())
        self._summary.setText(
            f"Mail {len(mails)} | Calendar {len(calendar_events)} | Communications {len(communications)}"
        )
        self._detail.setText(
            "\n".join(
                part
                for part in (
                    _latest_mail(mails),
                    _latest_event(calendar_events),
                    _latest_communication(communications),
                )
                if part
            )
            or "No local content imported yet."
        )


def _latest_mail(mails: list[MailMessage]) -> str:
    if not mails:
        return ""
    latest = mails[0]
    return f"Mail: {latest.subject} from {latest.sender} ({latest.source})"


def _latest_event(events: list[CalendarEvent]) -> str:
    if not events:
        return ""
    latest = events[0]
    return f"Calendar: {latest.title} at {latest.start_at.isoformat()} ({latest.source})"


def _latest_communication(messages: list[CommunicationMessage]) -> str:
    if not messages:
        return ""
    latest = messages[0]
    return f"Comms: {latest.conversation} by {latest.author} ({latest.source})"
