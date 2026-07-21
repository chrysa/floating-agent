"""Pure offline-first domain models and rules."""

from floating_agent.domain.connectivity_state import ConnectivityState
from floating_agent.domain.idempotency import build_idempotency_key
from floating_agent.domain.outbox_item import OutboxItem
from floating_agent.domain.outbox_status import OutboxStatus
from floating_agent.domain.outbox_transition import confirm_outbox_item, transition_outbox_item

__all__ = [
    "ConnectivityState",
    "OutboxItem",
    "OutboxStatus",
    "build_idempotency_key",
    "confirm_outbox_item",
    "transition_outbox_item",
]
