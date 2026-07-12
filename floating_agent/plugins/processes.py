"""Process monitoring plugin using psutil.

The process source and the killer are injectable so the plugin is testable
without touching the real process table. ``ProcessSample`` is the neutral shape
the plugin sorts and formats; the default source adapts psutil to it.
"""

from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

import psutil

from floating_agent.models import ProcessInfo

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

_BYTES_PER_MB = 1024**2
_DEFAULT_LIMIT = 5


@dataclass(frozen=True)
class ProcessSample:
    pid: int
    name: str
    cpu_percent: float
    ram_mb: float


def _default_source() -> Iterable[ProcessSample]:
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
        info = proc.info
        mem = info.get("memory_info")
        yield ProcessSample(
            pid=info["pid"],
            name=info.get("name") or "?",
            cpu_percent=info.get("cpu_percent") or 0.0,
            ram_mb=round((mem.rss if mem else 0) / _BYTES_PER_MB, 1),
        )


def _default_killer(pid: int) -> None:
    with contextlib.suppress(psutil.NoSuchProcess):  # pragma: no cover - race with the OS
        psutil.Process(pid).terminate()


class ProcessPlugin:
    """Ranks running processes by CPU and terminates one on request."""

    def __init__(
        self,
        source: Callable[[], Iterable[ProcessSample]] = _default_source,
        killer: Callable[[int], None] = _default_killer,
    ) -> None:
        self._source = source
        self._kill = killer

    def kill(self, pid: int) -> None:
        self._kill(pid)

    def top(self, limit: int = _DEFAULT_LIMIT) -> list[ProcessInfo]:
        ranked = sorted(self._source(), key=lambda p: p.cpu_percent, reverse=True)
        return [
            ProcessInfo(pid=p.pid, name=p.name, cpu_percent=p.cpu_percent, ram_mb=p.ram_mb) for p in ranked[:limit]
        ]
