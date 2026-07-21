"""Durable action record used by the Outbox port."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from floating_agent.domain.outbox_status import OutboxStatus


@dataclass(frozen=True, slots=True)
class OutboxItem:
    """Describe one auditable and idempotent provider action."""

    id: str
    idempotency_key: str
    provider: str
    account_id: str
    resource_type: str
    resource_id: str
    action_type: str
    payload: dict[str, object]
    status: OutboxStatus
    created_at: datetime
    updated_at: datetime
    attempt_count: int
    last_error: str | None
    requires_confirmation: bool
    confirmed_at: datetime | None

    def __post_init__(self) -> None:
        if self.attempt_count < 0:
            raise ValueError("attempt_count cannot be negative")
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("Outbox timestamps must be timezone-aware")
        if self.confirmed_at is not None and self.confirmed_at.tzinfo is None:
            raise ValueError("confirmed_at must be timezone-aware")
