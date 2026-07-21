import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest

from floating_agent.adapters.local.docker_cli_monitor import DockerCliMonitor, parse_docker_event
from floating_agent.domain.container_event_kind import ContainerEventKind

FIXTURES = Path(__file__).parents[1] / "fixtures" / "docker"


@pytest.mark.parametrize(
    ("fixture", "kind", "exit_code"),
    [
        ("start.json", ContainerEventKind.STARTED, None),
        ("restart.json", ContainerEventKind.RESTARTED, None),
        ("crash.json", ContainerEventKind.CRASHED, 137),
        ("stop.json", ContainerEventKind.STOPPED, 0),
    ],
)
def test_parse_docker_event(fixture: str, kind: ContainerEventKind, exit_code: int | None) -> None:
    event = parse_docker_event((FIXTURES / fixture).read_text())

    assert event.kind is kind
    assert event.exit_code == exit_code
    assert event.container_name == "demo-api"
    assert event.source == "docker"


def test_monitor_rejects_inverted_time_window() -> None:
    monitor = DockerCliMonitor(timeout_seconds=1)
    later = datetime(2026, 7, 21, 13, tzinfo=UTC)
    earlier = datetime(2026, 7, 21, 12, tzinfo=UTC)

    with pytest.raises(ValueError, match="until"):
        monitor.read_events(since=later, until=earlier)


def test_monitor_reports_timeout_as_provider_failure() -> None:
    def timeout_runner(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="docker events", timeout=1)

    monitor = DockerCliMonitor(timeout_seconds=1, runner=timeout_runner)
    earlier = datetime(2026, 7, 21, 12, tzinfo=UTC)
    later = datetime(2026, 7, 21, 13, tzinfo=UTC)

    with pytest.raises(RuntimeError, match="timed out"):
        monitor.read_events(since=earlier, until=later)
