"""Provider-agnostic calendar event available from a provider or the local cache."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(frozen=True, slots=True)
class CalendarEvent:
    """Represent one inspectable calendar event."""

    event_id: str
    account_id: str
    calendar_id: str
    title: str
    start_at: datetime
    end_at: datetime
    timezone: str
    location: str
    description: str
    organizer: str
    participants: tuple[str, ...]
    response_status: str
    reminders: tuple[str, ...]
    recurrence: tuple[str, ...]
    conflicts: tuple[str, ...]
    fresh_at: datetime
    source: str
    cached: bool

    def __post_init__(self) -> None:
        if self.start_at.tzinfo is None or self.end_at.tzinfo is None or self.fresh_at.tzinfo is None:
            raise ValueError("Calendar timestamps must be timezone-aware")
        if self.end_at < self.start_at:
            raise ValueError("end_at cannot be earlier than start_at")
