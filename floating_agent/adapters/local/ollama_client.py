"""Local Ollama adapter for the default assistant model."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import httpx

from floating_agent.agent.client import LLMResponse, ToolCall

if TYPE_CHECKING:
    from floating_agent.domain.assistant_settings import AssistantSettings


class OllamaClient:
    """Use a local Ollama server as the default assistant backend."""

    def __init__(self, settings: AssistantSettings, timeout: float = 30.0) -> None:
        self._settings = settings
        self._timeout = timeout

    def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> LLMResponse:
        payload = {
            "model": self._settings.ollama_model,
            "messages": messages,
            "tools": [_to_ollama_tool(tool) for tool in tools],
            "stream": False,
            "keep_alive": self._settings.ollama_keep_alive,
            "options": {"temperature": self._settings.ollama_temperature},
        }
        try:
            response = httpx.post(
                f"{self._settings.ollama_base_url.rstrip('/')}/api/chat",
                json=payload,
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            return LLMResponse(text=f"Local Ollama unavailable at {self._settings.ollama_base_url}: {exc}")

        data = response.json()
        message = data.get("message") or {}
        tool_calls = []
        for index, call in enumerate(message.get("tool_calls", []), start=1):
            function = call.get("function", {})
            name = function.get("name")
            if not name:
                continue
            tool_calls.append(
                ToolCall(
                    id=str(index),
                    name=name,
                    arguments=_coerce_arguments(function.get("arguments", {})),
                )
            )
        return LLMResponse(text=message.get("content"), tool_calls=tool_calls)


def _to_ollama_tool(tool: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool.get("description", ""),
            "parameters": tool.get("input_schema", {"type": "object", "properties": {}}),
        },
    }


def _coerce_arguments(arguments: Any) -> dict[str, Any]:
    if isinstance(arguments, dict):
        return arguments
    return {}
