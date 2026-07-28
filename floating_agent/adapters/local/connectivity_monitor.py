"""Local connectivity monitor."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import httpx

from floating_agent.domain.connectivity_state import ConnectivityState

if TYPE_CHECKING:
    from collections.abc import Callable


class LocalConnectivityMonitor:
    """Derive the global connectivity state from the configured AI endpoint."""

    def __init__(
        self,
        *,
        aggregator_url: str | None = None,
        probe: Callable[[str], bool] | None = None,
    ) -> None:
        self._aggregator_url = aggregator_url if aggregator_url is not None else os.environ.get("AI_AGGREGATOR_URL")
        self._probe = probe if probe is not None else _probe_aggregator

    def read_state(self) -> ConnectivityState:
        """Return offline when no endpoint exists, degraded on failures, online on success."""
        if not self._aggregator_url:
            return ConnectivityState.OFFLINE
        if self._probe(self._aggregator_url):
            return ConnectivityState.ONLINE
        return ConnectivityState.DEGRADED


def _probe_aggregator(url: str) -> bool:
    response = httpx.get(f"{url.rstrip('/')}/health", timeout=1.5)
    response.raise_for_status()
    return True
