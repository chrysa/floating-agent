"""LLM client abstraction for the agent loop.

The loop depends only on the ``LLMClient`` protocol, so it can run against the
real ai-aggregator (`AggregatorClient`), a canned `StubClient`, or a fake in tests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class ToolCall:
    """A tool invocation requested by the model."""

    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class LLMResponse:
    """One model turn: free text and/or tool calls to execute."""

    text: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)


class LLMClient(Protocol):
    """Anything that can turn a message history + tool specs into a response."""

    def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> LLMResponse: ...


class StubClient:
    """Offline fallback: echoes a helpful message, never calls tools.

    Used until ``AI_AGGREGATOR_URL`` is configured, so the overlay stays usable.
    """

    def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> LLMResponse:
        last = next((m for m in reversed(messages) if m.get("role") == "user"), None)
        text = last["content"] if last else ""
        return LLMResponse(text=(f'AI routing is not configured yet (set AI_AGGREGATOR_URL). You said: "{text}".'))


class AggregatorClient:  # pragma: no cover - exercised only against a live ai-aggregator
    """Routes completions through chrysa/ai-aggregator over HTTP."""

    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> LLMResponse:
        import httpx

        response = httpx.post(
            f"{self._base_url}/v1/messages",
            json={"messages": messages, "tools": tools},
            timeout=self._timeout,
        )
        response.raise_for_status()
        data = response.json()
        calls = [
            ToolCall(id=c["id"], name=c["name"], arguments=c.get("arguments", {})) for c in data.get("tool_calls", [])
        ]
        return LLMResponse(text=data.get("text"), tool_calls=calls)
