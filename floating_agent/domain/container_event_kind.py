"""Canonical local container lifecycle event kinds."""

from enum import StrEnum


class ContainerEventKind(StrEnum):
    """Describe user-relevant container lifecycle changes."""

    STARTED = "started"
    RESTARTED = "restarted"
    STOPPED = "stopped"
    CRASHED = "crashed"
