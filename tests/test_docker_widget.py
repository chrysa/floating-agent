from datetime import UTC, datetime

from floating_agent.domain.container_event_kind import ContainerEventKind
from floating_agent.domain.container_lifecycle_event import ContainerLifecycleEvent
from floating_agent.overlay.widgets.docker_widget import DockerWidget


def _event(kind: ContainerEventKind) -> ContainerLifecycleEvent:
    return ContainerLifecycleEvent(
        event_id=kind.value,
        container_id="abc123",
        container_name="demo-api",
        image="demo:latest",
        kind=kind,
        occurred_at=datetime(2026, 7, 21, 12, tzinfo=UTC),
        exit_code=137 if kind is ContainerEventKind.CRASHED else None,
        source="docker",
    )


def test_docker_widget_displays_lifecycle_activity(qtbot) -> None:
    widget = DockerWidget()
    qtbot.addWidget(widget)

    widget.add_events([_event(ContainerEventKind.STARTED), _event(ContainerEventKind.CRASHED)])

    assert "demo-api: crashed" in widget._activity.text()
    assert "demo-api: started" in widget._activity.text()
