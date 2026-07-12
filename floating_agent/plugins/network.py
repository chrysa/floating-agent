"""Network monitoring plugin using psutil.

Bandwidth is a rate, so it is derived from two ``net_io_counters`` reads spaced
by ``interval`` seconds. Samplers, the connection counter and the sleep function
are injectable to keep the plugin testable without real sockets or wall-clock waits.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

import psutil

from floating_agent.models import NetworkStats

if TYPE_CHECKING:
    from collections.abc import Callable

_BYTES_PER_MB = 1024**2


@dataclass(frozen=True)
class _IoSnapshot:
    bytes_sent: int
    bytes_recv: int


def _rate(before: int, after: int, interval: float) -> float:
    """MB/s between two cumulative byte counters; 0.0 on a reset or non-positive interval."""
    if interval <= 0:
        return 0.0
    delta = after - before
    if delta < 0:  # net_io_counters can wrap or reset on interface changes
        return 0.0
    return delta / interval / _BYTES_PER_MB


def _default_sampler() -> _IoSnapshot:
    counters = psutil.net_io_counters()
    return _IoSnapshot(bytes_sent=counters.bytes_sent, bytes_recv=counters.bytes_recv)


def _default_conn_counter() -> int:
    try:
        return len(psutil.net_connections(kind="inet"))
    except (psutil.AccessDenied, PermissionError):  # pragma: no cover - platform-dependent
        return 0


class NetworkPlugin:
    """Collects upload/download throughput and the active connection count."""

    def __init__(
        self,
        sampler: Callable[[], _IoSnapshot] = _default_sampler,
        conn_counter: Callable[[], int] = _default_conn_counter,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._sample = sampler
        self._count_connections = conn_counter
        self._sleep = sleep

    def get_stats(self, interval: float = 0.1) -> NetworkStats:
        before = self._sample()
        self._sleep(interval)
        after = self._sample()
        return NetworkStats(
            sent_mb_s=round(_rate(before.bytes_sent, after.bytes_sent, interval), 3),
            recv_mb_s=round(_rate(before.bytes_recv, after.bytes_recv, interval), 3),
            bytes_sent=after.bytes_sent,
            bytes_recv=after.bytes_recv,
            connections=self._count_connections(),
        )
