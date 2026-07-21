"""Local container lifecycle monitoring contract."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import datetime

    from floating_agent.domain.container_lifecycle_event import ContainerLifecycleEvent


class ContainerEventMonitor(Protocol):
    """Read local container lifecycle events without exposing a vendor SDK."""

    def read_events(self, *, since: datetime, until: datetime) -> Sequence[ContainerLifecycleEvent]:
        """Return relevant events for the requested closed time window."""
        ...
