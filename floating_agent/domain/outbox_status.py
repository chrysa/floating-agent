"""Lifecycle states for durable actions."""

from enum import StrEnum


class OutboxStatus(StrEnum):
    """Represent the canonical lifecycle of an Outbox item."""

    DRAFT = "draft"
    WAITING_CONFIRMATION = "waiting_confirmation"
    QUEUED = "queued"
    EXECUTING = "executing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CONFLICT = "conflict"
    CANCELLED = "cancelled"
