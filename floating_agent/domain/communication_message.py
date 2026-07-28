"""Provider-agnostic communication message available from a provider or the local cache."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(frozen=True, slots=True)
class CommunicationMessage:
    """Represent one inspectable communication item."""

    message_id: str
    account_id: str
    workspace: str
    conversation: str
    author: str
    thread_id: str
    content: str
    mentions: tuple[str, ...]
    reactions: tuple[str, ...]
    sent_at: datetime
    fresh_at: datetime
    source: str
    cached: bool
    unread: bool

    def __post_init__(self) -> None:
        if self.sent_at.tzinfo is None or self.fresh_at.tzinfo is None:
            raise ValueError("Communication timestamps must be timezone-aware")
