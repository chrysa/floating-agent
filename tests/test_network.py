"""Tests for the network monitoring plugin + tool (no real sockets)."""

from __future__ import annotations

from floating_agent.agent.tools import build_network_tool
from floating_agent.plugins.network import NetworkPlugin, _IoSnapshot, _rate


class _FakeSampler:
    """Returns queued snapshots on successive calls (mimics two psutil reads)."""

    def __init__(self, snapshots: list[_IoSnapshot]) -> None:
        self._snapshots = list(snapshots)

    def __call__(self) -> _IoSnapshot:
        return self._snapshots.pop(0)


def _plugin(before: _IoSnapshot, after: _IoSnapshot, connections: int = 0) -> NetworkPlugin:
    return NetworkPlugin(
        sampler=_FakeSampler([before, after]),
        conn_counter=lambda: connections,
        sleep=lambda _seconds: None,
    )


def test_rate_computes_mb_per_second() -> None:
    assert _rate(0, 2 * 1024**2, 1.0) == 2.0
    assert _rate(0, 2 * 1024**2, 2.0) == 1.0


def test_rate_zero_interval_is_safe() -> None:
    assert _rate(0, 1024**2, 0.0) == 0.0


def test_rate_clamps_counter_reset() -> None:
    # net_io_counters can wrap/reset; a negative delta must not yield a negative rate.
    assert _rate(5 * 1024**2, 0, 1.0) == 0.0


def test_plugin_get_stats_computes_throughput() -> None:
    before = _IoSnapshot(bytes_sent=0, bytes_recv=0)
    after = _IoSnapshot(bytes_sent=1024**2, bytes_recv=3 * 1024**2)
    stats = _plugin(before, after, connections=7).get_stats(interval=1.0)
    assert stats.sent_mb_s == 1.0
    assert stats.recv_mb_s == 3.0
    assert stats.bytes_sent == 1024**2
    assert stats.bytes_recv == 3 * 1024**2
    assert stats.connections == 7


def test_network_tool_summarizes() -> None:
    before = _IoSnapshot(bytes_sent=0, bytes_recv=0)
    after = _IoSnapshot(bytes_sent=1024**2, bytes_recv=2 * 1024**2)
    out = build_network_tool(_plugin(before, after, connections=4)).run({})
    # The plugin math is covered above; here we assert the tool wires + formats it.
    assert "up" in out
    assert "down" in out
    assert "MB/s" in out
    assert "4 connections" in out
