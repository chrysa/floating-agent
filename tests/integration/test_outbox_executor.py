from datetime import UTC, datetime, timedelta
from pathlib import Path

from floating_agent.adapters.local.sqlite_outbox import SqliteOutbox
from floating_agent.application.outbox_executor import OutboxConflictError, OutboxExecutor
from floating_agent.domain.outbox_item import OutboxItem
from floating_agent.domain.outbox_status import OutboxStatus
from floating_agent.domain.outbox_transition import confirm_outbox_item

NOW = datetime(2026, 7, 21, 12, tzinfo=UTC)
LATER = NOW + timedelta(seconds=10)


def _item(
    *,
    item_id: str = "action-1",
    key: str = "stable-key",
    status: OutboxStatus = OutboxStatus.WAITING_CONFIRMATION,
    confirmed_at: datetime | None = None,
    attempt_count: int = 0,
    updated_at: datetime = NOW,
) -> OutboxItem:
    return OutboxItem(
        id=item_id,
        idempotency_key=key,
        provider="mail",
        account_id="demo-account",
        resource_type="message",
        resource_id="message-1",
        action_type="archive",
        payload={"source": "fixture"},
        status=status,
        created_at=NOW,
        updated_at=updated_at,
        attempt_count=attempt_count,
        last_error=None,
        requires_confirmation=True,
        confirmed_at=confirmed_at,
    )


class _RecordingHandler:
    def __init__(self, *, fail_once: bool = False, conflict_once: bool = False) -> None:
        self.calls: list[str] = []
        self._fail_once = fail_once
        self._conflict_once = conflict_once

    def execute(self, item: OutboxItem) -> None:
        self.calls.append(item.idempotency_key)
        if self._conflict_once:
            self._conflict_once = False
            raise OutboxConflictError("calendar conflict")
        if self._fail_once:
            self._fail_once = False
            raise RuntimeError("temporary failure")


def test_executor_completes_queued_action(tmp_path: Path) -> None:
    outbox = SqliteOutbox(tmp_path / "outbox.sqlite3")
    item = confirm_outbox_item(_item(status=OutboxStatus.WAITING_CONFIRMATION), confirmed_at=NOW)
    outbox.add(item)
    handler = _RecordingHandler()

    processed = OutboxExecutor(outbox, handler).tick(now=NOW)

    assert processed == 1
    assert handler.calls == ["stable-key"]
    persisted = outbox.get("action-1")
    assert persisted is not None
    assert persisted.status is OutboxStatus.SUCCEEDED


def test_executor_recovers_executing_item_after_restart(tmp_path: Path) -> None:
    outbox = SqliteOutbox(tmp_path / "outbox.sqlite3")
    outbox.add(_item(status=OutboxStatus.EXECUTING, confirmed_at=NOW, attempt_count=1, updated_at=NOW))
    handler = _RecordingHandler()

    executor = OutboxExecutor(outbox, handler)
    recovered = executor.recover_incomplete(now=LATER)

    assert recovered == 1
    item = outbox.get("action-1")
    assert item is not None
    assert item.status is OutboxStatus.QUEUED

    executor.tick(now=LATER)

    assert handler.calls == ["stable-key"]
    item = outbox.get("action-1")
    assert item is not None
    assert item.status is OutboxStatus.SUCCEEDED


def test_executor_applies_backoff_after_failure(tmp_path: Path) -> None:
    outbox = SqliteOutbox(tmp_path / "outbox.sqlite3")
    outbox.add(confirm_outbox_item(_item(status=OutboxStatus.WAITING_CONFIRMATION), confirmed_at=NOW))
    handler = _RecordingHandler(fail_once=True)
    executor = OutboxExecutor(outbox, handler, retry_base_seconds=10.0)

    executor.tick(now=NOW)
    item = outbox.get("action-1")
    assert item is not None
    assert item.status is OutboxStatus.FAILED

    executor.tick(now=NOW + timedelta(seconds=5))
    assert handler.calls == ["stable-key"]
    item = outbox.get("action-1")
    assert item is not None
    assert item.status is OutboxStatus.FAILED

    executor.tick(now=NOW + timedelta(seconds=12))
    assert handler.calls == ["stable-key", "stable-key"]
    item = outbox.get("action-1")
    assert item is not None
    assert item.status is OutboxStatus.SUCCEEDED


def test_executor_marks_conflict(tmp_path: Path) -> None:
    outbox = SqliteOutbox(tmp_path / "outbox.sqlite3")
    outbox.add(confirm_outbox_item(_item(status=OutboxStatus.WAITING_CONFIRMATION), confirmed_at=NOW))
    executor = OutboxExecutor(outbox, _RecordingHandler(conflict_once=True))

    executor.tick(now=NOW)

    item = outbox.get("action-1")
    assert item is not None
    assert item.status is OutboxStatus.CONFLICT
    assert item.last_error is not None
    assert "calendar conflict" in item.last_error
