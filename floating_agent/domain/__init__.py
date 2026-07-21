"""Pure offline-first domain models and rules."""

from floating_agent.domain.calendar_event import CalendarEvent
from floating_agent.domain.communication_message import CommunicationMessage
from floating_agent.domain.connectivity_state import ConnectivityState
from floating_agent.domain.container_event_kind import ContainerEventKind
from floating_agent.domain.container_lifecycle_event import ContainerLifecycleEvent
from floating_agent.domain.idempotency import build_idempotency_key
from floating_agent.domain.mail_attachment import MailAttachment
from floating_agent.domain.mail_message import MailMessage
from floating_agent.domain.outbox_item import OutboxItem
from floating_agent.domain.outbox_status import OutboxStatus
from floating_agent.domain.outbox_transition import (
    confirm_outbox_item,
    transition_outbox_item,
)
from floating_agent.domain.search_result import SearchResult

__all__ = [
    "CalendarEvent",
    "CommunicationMessage",
    "ConnectivityState",
    "ContainerEventKind",
    "ContainerLifecycleEvent",
    "MailAttachment",
    "MailMessage",
    "OutboxItem",
    "OutboxStatus",
    "SearchResult",
    "build_idempotency_key",
    "confirm_outbox_item",
    "transition_outbox_item",
]
