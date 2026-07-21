from datetime import UTC, datetime

import pytest

from floating_agent.adapters.local.sqlite_outbox import SqliteOutbox
from floating_agent.domain.outbox_item import OutboxItem
from floating_agent.domain.outbox_status import OutboxStatus
from floating_agent.domain.outbox_transition import confirm_outbox_item

NOW = datetime(2026, 7, 21, 12, tzinfo=UTC)


def _item(*, item_id: str = "action-1", key: str = "stable-key") -> OutboxItem:
    return OutboxItem(
        id=item_id,
        idempotency_key=key,
        provider="mail",
        account_id="demo-account",
        resource_type="message",
        resource_id="message-1",
        action_type="archive",
        payload={"source": "fixture"},
        status=OutboxStatus.WAITING_CONFIRMATION,
        created_at=NOW,
        updated_at=NOW,
        attempt_count=0,
        last_error=None,
        requires_confirmation=True,
        confirmed_at=None,
    )


def test_outbox_survives_adapter_restart(tmp_path) -> None:
    database = tmp_path / "store.sqlite3"
    SqliteOutbox(database).add(_item())

    restored = SqliteOutbox(database).get("action-1")

    assert restored == _item()


def test_duplicate_idempotency_key_returns_original_item(tmp_path) -> None:
    outbox = SqliteOutbox(tmp_path / "store.sqlite3")
    original = outbox.add(_item())

    duplicate = outbox.add(_item(item_id="action-2"))

    assert duplicate == original
    assert outbox.get("action-2") is None


def test_confirmed_state_is_persisted(tmp_path) -> None:
    outbox = SqliteOutbox(tmp_path / "store.sqlite3")
    outbox.add(_item())
    confirmed = confirm_outbox_item(_item(), confirmed_at=NOW)

    outbox.save(confirmed)

    assert outbox.list_by_status({OutboxStatus.QUEUED}) == [confirmed]


def test_save_rejects_unknown_item(tmp_path) -> None:
    with pytest.raises(KeyError, match="missing"):
        SqliteOutbox(tmp_path / "store.sqlite3").save(_item(item_id="missing"))
