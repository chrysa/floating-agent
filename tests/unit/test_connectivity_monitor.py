from floating_agent.adapters.local.connectivity_monitor import LocalConnectivityMonitor
from floating_agent.domain.connectivity_state import ConnectivityState


def test_connectivity_monitor_reports_offline_when_no_endpoint() -> None:
    monitor = LocalConnectivityMonitor(aggregator_url=None, probe=lambda _url: True)

    assert monitor.read_state() is ConnectivityState.OFFLINE


def test_connectivity_monitor_reports_online_when_probe_succeeds() -> None:
    monitor = LocalConnectivityMonitor(aggregator_url="http://example.test", probe=lambda _url: True)

    assert monitor.read_state() is ConnectivityState.ONLINE


def test_connectivity_monitor_reports_degraded_when_probe_fails() -> None:
    monitor = LocalConnectivityMonitor(aggregator_url="http://example.test", probe=lambda _url: False)

    assert monitor.read_state() is ConnectivityState.DEGRADED
