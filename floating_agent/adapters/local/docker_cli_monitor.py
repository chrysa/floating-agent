"""Docker CLI adapter for local container lifecycle events."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from floating_agent.domain.container_event_kind import ContainerEventKind
from floating_agent.domain.container_lifecycle_event import ContainerLifecycleEvent

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

_DOCKER_SOURCE = "docker"
_RELEVANT_ACTIONS = ("start", "restart", "die", "oom")


class DockerCliMonitor:
    """Read bounded Docker event windows without polling container logs."""

    def __init__(
        self,
        *,
        timeout_seconds: float,
        runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    ) -> None:
        self._timeout_seconds = timeout_seconds
        self._runner = runner

    def read_events(self, *, since: datetime, until: datetime) -> Sequence[ContainerLifecycleEvent]:
        """Return lifecycle events emitted by the local Docker daemon."""
        if since.tzinfo is None or until.tzinfo is None:
            raise ValueError("Docker event window must be timezone-aware")
        if until < since:
            raise ValueError("until must not be earlier than since")

        command = self._command(since, until)
        try:
            result = self._runner(  # noqa: S603 - fixed local Docker CLI command, no shell
                command,
                capture_output=True,
                check=False,
                text=True,
                timeout=self._timeout_seconds,
            )
        except subprocess.TimeoutExpired as error:
            raise RuntimeError("Docker event query timed out") from error
        except OSError as error:
            raise RuntimeError(f"Docker CLI unavailable: {error}") from error
        if result.returncode != 0:
            message = result.stderr.strip() or "Docker event command failed"
            raise RuntimeError(message)
        return [parse_docker_event(line) for line in result.stdout.splitlines() if line.strip()]

    @staticmethod
    def _command(since: datetime, until: datetime) -> list[str]:
        command = [
            "docker",
            "events",
            "--since",
            since.astimezone(UTC).isoformat(),
            "--until",
            until.astimezone(UTC).isoformat(),
            "--filter",
            "type=container",
        ]
        for action in _RELEVANT_ACTIONS:
            command.extend(("--filter", f"event={action}"))
        command.extend(("--format", "{{json .}}"))
        return command


def parse_docker_event(raw_event: str) -> ContainerLifecycleEvent:
    """Translate one Docker JSON event into the provider-agnostic domain model."""
    data: dict[str, Any] = json.loads(raw_event)
    action = str(data.get("Action", data.get("status", ""))).lower()
    attributes = data.get("Actor", {}).get("Attributes", {})
    exit_code = _exit_code(attributes)
    occurred_at = datetime.fromtimestamp(int(data["time"]), tz=UTC)
    container_id = str(data.get("id", data.get("Actor", {}).get("ID", "")))
    event_identity = f"{container_id}:{action}:{data.get('timeNano', data['time'])}"
    return ContainerLifecycleEvent(
        event_id=hashlib.sha256(event_identity.encode()).hexdigest(),
        container_id=container_id,
        container_name=str(attributes.get("name", container_id[:12])),
        image=str(data.get("from", attributes.get("image", "unknown"))),
        kind=_event_kind(action, exit_code),
        occurred_at=occurred_at,
        exit_code=exit_code,
        source=_DOCKER_SOURCE,
    )


def _exit_code(attributes: dict[str, Any]) -> int | None:
    value = attributes.get("exitCode")
    return None if value is None else int(value)


def _event_kind(action: str, exit_code: int | None) -> ContainerEventKind:
    if action == "start":
        return ContainerEventKind.STARTED
    if action == "restart":
        return ContainerEventKind.RESTARTED
    if action == "oom" or (action == "die" and exit_code not in {None, 0}):
        return ContainerEventKind.CRASHED
    if action == "die":
        return ContainerEventKind.STOPPED
    raise ValueError(f"Unsupported Docker event action: {action}")
