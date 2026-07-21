"""Provider-agnostic readable mail message."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from floating_agent.domain.mail_attachment import MailAttachment


@dataclass(frozen=True, slots=True)
class MailMessage:
    """Represent mail content available from a provider or the local cache."""

    message_id: str
    account_id: str
    sender: str
    recipients: tuple[str, ...]
    cc: tuple[str, ...]
    sent_at: datetime
    subject: str
    labels: tuple[str, ...]
    attachments: tuple[MailAttachment, ...]
    body_text: str
    body_html: str | None
    fresh_at: datetime
    source: str
    cached: bool

    def __post_init__(self) -> None:
        if self.sent_at.tzinfo is None or self.fresh_at.tzinfo is None:
            raise ValueError("Mail timestamps must be timezone-aware")
