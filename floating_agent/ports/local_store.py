"""Local cached content persistence contract."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence

    from floating_agent.domain.calendar_event import CalendarEvent
    from floating_agent.domain.communication_message import CommunicationMessage
    from floating_agent.domain.mail_message import MailMessage


class LocalStore(Protocol):
    """Persist imported local content without leaking storage details."""

    def save_mail(self, message: MailMessage) -> MailMessage:
        """Insert or replace one cached mail message."""
        ...

    def save_calendar_event(self, event: CalendarEvent) -> CalendarEvent:
        """Insert or replace one cached calendar event."""
        ...

    def save_communication(self, message: CommunicationMessage) -> CommunicationMessage:
        """Insert or replace one cached communication message."""
        ...

    def list_mail(self, account_id: str | None = None) -> Sequence[MailMessage]:
        """Return cached mail messages sorted from freshest to oldest."""
        ...

    def list_calendar_events(self, account_id: str | None = None) -> Sequence[CalendarEvent]:
        """Return cached calendar events sorted from freshest to oldest."""
        ...

    def list_communications(self, account_id: str | None = None) -> Sequence[CommunicationMessage]:
        """Return cached communication messages sorted from freshest to oldest."""
        ...

    def clear(self) -> None:
        """Remove all cached local content."""
        ...
