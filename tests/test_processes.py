"""Tests for the processes plugin + tools (no real process table)."""

from __future__ import annotations

from floating_agent.agent.tools import build_kill_process_tool, build_top_processes_tool
from floating_agent.plugins.processes import ProcessPlugin, ProcessSample


def _plugin(samples: list[ProcessSample], killed: list[int] | None = None) -> ProcessPlugin:
    sink = killed if killed is not None else []
    return ProcessPlugin(source=lambda: list(samples), killer=sink.append)


_SAMPLES = [
    ProcessSample(pid=1, name="init", cpu_percent=0.5, ram_mb=2.0),
    ProcessSample(pid=42, name="chrome", cpu_percent=88.0, ram_mb=1500.0),
    ProcessSample(pid=7, name="python", cpu_percent=12.0, ram_mb=120.0),
]


def test_top_sorts_by_cpu_desc_and_limits() -> None:
    top = _plugin(_SAMPLES).top(limit=2)
    assert [p.pid for p in top] == [42, 7]
    assert top[0].name == "chrome"
    assert top[0].cpu_percent == 88.0


def test_top_defaults_to_five() -> None:
    top = _plugin(_SAMPLES).top()
    assert len(top) == 3  # fewer than 5 available → returns all


def test_kill_forwards_pid_to_killer() -> None:
    killed: list[int] = []
    _plugin(_SAMPLES, killed).kill(42)
    assert killed == [42]


def test_top_processes_tool_summarizes() -> None:
    out = build_top_processes_tool(_plugin(_SAMPLES)).run({})
    assert "chrome" in out
    assert "88" in out


def test_kill_tool_requires_confirmation_and_kills() -> None:
    killed: list[int] = []
    tool = build_kill_process_tool(_plugin(_SAMPLES, killed))
    assert tool.requires_confirmation is True
    out = tool.run({"pid": 42})
    assert killed == [42]
    assert "42" in out
