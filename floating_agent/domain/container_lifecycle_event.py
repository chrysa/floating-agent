"""Provider-agnostic container lifecycle event."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from floating_agent.domain.container_event_kind import ContainerEventKind


@dataclass(frozen=True, slots=True)
class ContainerLifecycleEvent:
    """Represent one local container start, restart, stop, or crash."""

    event_id: str
    container_id: str
    container_name: str
    image: str
    kind: ContainerEventKind
    occurred_at: datetime
    exit_code: int | None
    source: str

    def __post_init__(self) -> None:
        if self.occurred_at.tzinfo is None:
            raise ValueError("occurred_at must be timezone-aware")
