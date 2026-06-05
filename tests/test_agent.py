"""Tests for the agent core: registry, tools, and the tool-calling loop."""

from __future__ import annotations

from typing import Any

from floating_agent.agent.client import LLMResponse, StubClient, ToolCall
from floating_agent.agent.loop import Agent
from floating_agent.agent.tools import ToolRegistry, build_system_tool
from floating_agent.models import SystemStats


class _FakePlugin:
    def get_stats(self) -> SystemStats:
        return SystemStats(
            cpu_percent=10.0,
            ram_used_gb=8.0,
            ram_total_gb=16.0,
            ram_percent=50.0,
            disk_used_gb=250.0,
            disk_total_gb=500.0,
            disk_percent=50.0,
        )


class _ScriptedClient:
    """Returns a queued list of responses, one per ``complete`` call."""

    def __init__(self, responses: list[LLMResponse]) -> None:
        self._responses = list(responses)
        self.calls = 0

    def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> LLMResponse:
        self.calls += 1
        return self._responses.pop(0)


def test_registry_register_get_contains_specs() -> None:
    registry = ToolRegistry()
    tool = build_system_tool(plugin=_FakePlugin())
    registry.register(tool)
    assert "get_system_stats" in registry
    assert registry.get("get_system_stats") is tool
    specs = registry.specs()
    assert specs[0]["name"] == "get_system_stats"
    assert "input_schema" in specs[0]


def test_system_tool_returns_summary() -> None:
    tool = build_system_tool(plugin=_FakePlugin())
    out = tool.run({})
    assert "CPU 10%" in out
    assert "8.0/16.0 GB" in out


def test_loop_returns_text_when_no_tool_calls() -> None:
    client = _ScriptedClient([LLMResponse(text="hello there")])
    agent = Agent(client=client, registry=ToolRegistry())
    assert agent.run("hi") == "hello there"
    assert client.calls == 1


def test_loop_executes_tool_then_returns_final() -> None:
    registry = ToolRegistry()
    registry.register(build_system_tool(plugin=_FakePlugin()))
    client = _ScriptedClient(
        [
            LLMResponse(tool_calls=[ToolCall(id="c1", name="get_system_stats", arguments={})]),
            LLMResponse(text="Your CPU is at 10%."),
        ]
    )
    agent = Agent(client=client, registry=registry)
    assert agent.run("how busy am I?") == "Your CPU is at 10%."
    assert client.calls == 2


def test_loop_handles_unknown_tool() -> None:
    client = _ScriptedClient(
        [
            LLMResponse(tool_calls=[ToolCall(id="c1", name="nope", arguments={})]),
            LLMResponse(text="done"),
        ]
    )
    agent = Agent(client=client, registry=ToolRegistry())
    assert agent.run("x") == "done"


def test_loop_stops_at_max_steps() -> None:
    looping = [LLMResponse(tool_calls=[ToolCall(id="c", name="nope", arguments={})]) for _ in range(10)]
    agent = Agent(client=_ScriptedClient(looping), registry=ToolRegistry())
    assert "maximum" in agent.run("x").lower()


def test_stub_client_echoes_user_text() -> None:
    resp = StubClient().complete([{"role": "user", "content": "ping"}], [])
    assert resp.tool_calls == []
    assert "ping" in (resp.text or "")
