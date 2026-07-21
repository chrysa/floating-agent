"""Durable Outbox persistence contract."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence

    from floating_agent.domain.outbox_item import OutboxItem
    from floating_agent.domain.outbox_status import OutboxStatus


class Outbox(Protocol):
    """Persist actions before any remote execution."""

    def add(self, item: OutboxItem) -> OutboxItem:
        """Insert an action or return the existing idempotent action."""
        ...

    def get(self, item_id: str) -> OutboxItem | None:
        """Return one action by identifier."""
        ...

    def save(self, item: OutboxItem) -> None:
        """Persist a state transition for an existing action."""
        ...

    def list_by_status(self, statuses: set[OutboxStatus]) -> Sequence[OutboxItem]:
        """Return actions in creation order for the requested states."""
        ...
