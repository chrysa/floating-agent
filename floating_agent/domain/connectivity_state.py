"""Connectivity state exposed to application services and the UI."""

from enum import StrEnum


class ConnectivityState(StrEnum):
    """Describe whether local and remote capabilities are available."""

    OFFLINE = "offline"
    DEGRADED = "degraded"
    ONLINE = "online"
