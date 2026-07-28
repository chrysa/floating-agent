"""Local connectivity monitoring contract."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from floating_agent.domain.connectivity_state import ConnectivityState


class ConnectivityMonitor(Protocol):
    """Report the current connectivity state without leaking transport details."""

    def read_state(self) -> ConnectivityState:
        """Return the current app-level connectivity state."""
        ...
