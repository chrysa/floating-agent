"""Pure Outbox lifecycle transition rules."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from floating_agent.domain.outbox_status import OutboxStatus

if TYPE_CHECKING:
    from datetime import datetime

    from floating_agent.domain.outbox_item import OutboxItem

_ALLOWED_TRANSITIONS = {
    OutboxStatus.DRAFT: {
        OutboxStatus.WAITING_CONFIRMATION,
        OutboxStatus.QUEUED,
        OutboxStatus.CANCELLED,
    },
    OutboxStatus.WAITING_CONFIRMATION: {OutboxStatus.QUEUED, OutboxStatus.CANCELLED},
    OutboxStatus.QUEUED: {OutboxStatus.EXECUTING, OutboxStatus.CANCELLED},
    OutboxStatus.EXECUTING: {
        OutboxStatus.QUEUED,
        OutboxStatus.SUCCEEDED,
        OutboxStatus.FAILED,
        OutboxStatus.CONFLICT,
    },
    OutboxStatus.FAILED: {OutboxStatus.QUEUED, OutboxStatus.CANCELLED},
    OutboxStatus.CONFLICT: {OutboxStatus.QUEUED, OutboxStatus.CANCELLED},
    OutboxStatus.SUCCEEDED: set(),
    OutboxStatus.CANCELLED: set(),
}


def transition_outbox_item(
    item: OutboxItem,
    target: OutboxStatus,
    *,
    changed_at: datetime,
    last_error: str | None = None,
) -> OutboxItem:
    """Return an updated item when the requested lifecycle transition is valid."""
    if changed_at.tzinfo is None:
        raise ValueError("changed_at must be timezone-aware")
    if target not in _ALLOWED_TRANSITIONS[item.status]:
        raise ValueError(f"Invalid Outbox transition: {item.status} -> {target}")
    if target is OutboxStatus.QUEUED and item.requires_confirmation and item.confirmed_at is None:
        raise ValueError("A confirmed_at timestamp is required before queueing")

    attempt_count = item.attempt_count + int(target is OutboxStatus.EXECUTING)
    return replace(
        item,
        status=target,
        updated_at=changed_at,
        attempt_count=attempt_count,
        last_error=last_error,
    )


def confirm_outbox_item(item: OutboxItem, *, confirmed_at: datetime) -> OutboxItem:
    """Confirm a waiting action and make it eligible for execution."""
    if confirmed_at.tzinfo is None:
        raise ValueError("confirmed_at must be timezone-aware")
    if item.status is not OutboxStatus.WAITING_CONFIRMATION:
        raise ValueError("Only waiting_confirmation actions can be confirmed")
    return replace(
        item,
        status=OutboxStatus.QUEUED,
        updated_at=confirmed_at,
        confirmed_at=confirmed_at,
    )
