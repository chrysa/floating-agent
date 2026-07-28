from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from floating_agent.adapters.local.ollama_client import OllamaClient
from floating_agent.domain.assistant_settings import AssistantSettings

if TYPE_CHECKING:
    import pytest


def test_ollama_client_completes_and_parses_tool_calls(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_post(url: str, json: dict[str, object], timeout: float) -> httpx.Response:
        captured["url"] = url
        captured["payload"] = json
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={
                "message": {
                    "role": "assistant",
                    "content": "ready",
                    "tool_calls": [
                        {"function": {"name": "get_system_stats", "arguments": {"limit": 2}}}
                    ],
                }
            },
        )

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OllamaClient(AssistantSettings())
    response = client.complete(
        [{"role": "user", "content": "status"}],
        [{"name": "get_system_stats", "description": "stats", "input_schema": {"type": "object"}}],
    )

    assert str(captured["url"]).endswith("/api/chat")
    payload = captured["payload"]
    assert isinstance(payload, dict)
    assert payload["model"] == "llama3.2"
    assert payload["messages"][0]["content"] == "status"
    assert response.text == "ready"
    assert response.tool_calls[0].name == "get_system_stats"
    assert response.tool_calls[0].arguments == {"limit": 2}
