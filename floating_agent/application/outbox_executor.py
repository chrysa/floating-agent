"""Replay and execute durable Outbox actions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Protocol

from floating_agent.domain.outbox_status import OutboxStatus
from floating_agent.domain.outbox_transition import transition_outbox_item

if TYPE_CHECKING:
    from collections.abc import Sequence

    from floating_agent.domain.outbox_item import OutboxItem
    from floating_agent.ports.outbox import Outbox


class OutboxExecutionError(Exception):
    """Raised when an action fails and should be recorded as failed."""


class OutboxConflictError(OutboxExecutionError):
    """Raised when an action hits a conflict and needs manual resolution."""


class OutboxActionHandler(Protocol):
    """Execute one Outbox item against its provider or local adapter."""

    def execute(self, item: OutboxItem) -> None:
        """Perform the action. Raise to record failure/conflict."""
        ...


@dataclass(slots=True)
class OutboxExecutor:
    """Recover and execute durable Outbox actions with controlled backoff."""

    outbox: Outbox
    handler: OutboxActionHandler
    retry_base_seconds: float = 5.0
    retry_max_seconds: float = 300.0

    def recover_incomplete(self, *, now: datetime) -> int:
        """Return executing items to queued after a crash or shutdown."""
        self._validate_now(now)
        recovered = 0
        for item in self.outbox.list_by_status({OutboxStatus.EXECUTING}):
            self.outbox.save(transition_outbox_item(item, OutboxStatus.QUEUED, changed_at=now))
            recovered += 1
        return recovered

    def tick(self, *, now: datetime) -> int:
        """Recover, then execute ready queued or retryable failed actions."""
        self._validate_now(now)
        processed = 0
        processed += self.recover_incomplete(now=now)
        for item in self._ready_items(now):
            self._execute_one(item, now=now)
            processed += 1
        return processed

    def _ready_items(self, now: datetime) -> Sequence[OutboxItem]:
        ready = []
        for item in self.outbox.list_by_status({OutboxStatus.QUEUED, OutboxStatus.FAILED}):
            if item.status is OutboxStatus.QUEUED or self._backoff_elapsed(item, now):
                ready.append(item)
        return ready

    def _execute_one(self, item: OutboxItem, *, now: datetime) -> None:
        if item.status is OutboxStatus.FAILED:
            item = transition_outbox_item(item, OutboxStatus.QUEUED, changed_at=now)
        executing = transition_outbox_item(item, OutboxStatus.EXECUTING, changed_at=now)
        self.outbox.save(executing)
        try:
            self.handler.execute(executing)
        except OutboxConflictError as error:
            self.outbox.save(
                transition_outbox_item(
                    executing,
                    OutboxStatus.CONFLICT,
                    changed_at=now,
                    last_error=_error_message(error),
                )
            )
        except Exception as error:  # noqa: BLE001 - recorded as durable failure for replay
            self.outbox.save(
                transition_outbox_item(executing, OutboxStatus.FAILED, changed_at=now, last_error=_error_message(error))
            )
        else:
            self.outbox.save(transition_outbox_item(executing, OutboxStatus.SUCCEEDED, changed_at=now))

    def _backoff_elapsed(self, item: OutboxItem, now: datetime) -> bool:
        if item.status is not OutboxStatus.FAILED:
            return False
        delay = min(self.retry_base_seconds * (2 ** max(item.attempt_count - 1, 0)), self.retry_max_seconds)
        return now - item.updated_at >= timedelta(seconds=delay)

    @staticmethod
    def _validate_now(now: datetime) -> None:
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")


def _error_message(error: Exception) -> str:
    message = f"{type(error).__name__}: {error}"
    return message[:500]
