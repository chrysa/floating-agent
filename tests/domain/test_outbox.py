from dataclasses import replace
from datetime import UTC, datetime

import pytest

from floating_agent.domain.outbox_item import OutboxItem
from floating_agent.domain.outbox_status import OutboxStatus
from floating_agent.domain.outbox_transition import confirm_outbox_item, transition_outbox_item

NOW = datetime(2026, 7, 21, 12, tzinfo=UTC)
LATER = datetime(2026, 7, 21, 13, tzinfo=UTC)


def _item(
    *,
    status: OutboxStatus = OutboxStatus.DRAFT,
    requires_confirmation: bool = True,
    confirmed_at: datetime | None = None,
) -> OutboxItem:
    return OutboxItem(
        id="action-1",
        idempotency_key="stable-key",
        provider="mail",
        account_id="demo-account",
        resource_type="message",
        resource_id="message-1",
        action_type="archive",
        payload={},
        status=status,
        created_at=NOW,
        updated_at=NOW,
        attempt_count=0,
        last_error=None,
        requires_confirmation=requires_confirmation,
        confirmed_at=confirmed_at,
    )


def test_confirm_waiting_action_queues_it() -> None:
    confirmed = confirm_outbox_item(
        _item(status=OutboxStatus.WAITING_CONFIRMATION),
        confirmed_at=LATER,
    )

    assert confirmed.status is OutboxStatus.QUEUED
    assert confirmed.confirmed_at == LATER


def test_action_cannot_be_queued_without_required_confirmation() -> None:
    with pytest.raises(ValueError, match="confirmed_at"):
        transition_outbox_item(_item(), OutboxStatus.QUEUED, changed_at=LATER)


def test_execution_increments_attempt_count_once() -> None:
    executing = transition_outbox_item(
        _item(status=OutboxStatus.QUEUED, confirmed_at=NOW),
        OutboxStatus.EXECUTING,
        changed_at=LATER,
    )

    assert executing.attempt_count == 1


def test_terminal_action_cannot_transition() -> None:
    with pytest.raises(ValueError, match="Invalid Outbox transition"):
        transition_outbox_item(
            _item(status=OutboxStatus.SUCCEEDED, confirmed_at=NOW),
            OutboxStatus.QUEUED,
            changed_at=LATER,
        )


def test_outbox_rejects_naive_timestamps() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        replace(_item(), created_at=datetime(2026, 7, 21, 12))
