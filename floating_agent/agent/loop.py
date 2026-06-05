"""The tool-calling loop: prompt -> (tool calls -> results)* -> final answer."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from floating_agent.agent.client import LLMClient
    from floating_agent.agent.tools import ToolRegistry


class Agent:
    """Drives an LLM client through tool calls until it returns a final answer."""

    MAX_STEPS = 5

    def __init__(self, client: LLMClient, registry: ToolRegistry) -> None:
        self._client = client
        self._registry = registry

    def run(self, user_message: str) -> str:
        """Run the loop for one user message and return the final text."""
        messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]

        for _ in range(self.MAX_STEPS):
            response = self._client.complete(messages, self._registry.specs())

            if not response.tool_calls:
                return response.text or ""

            messages.append(
                {
                    "role": "assistant",
                    "content": response.text or "",
                    "tool_calls": [{"id": c.id, "name": c.name, "arguments": c.arguments} for c in response.tool_calls],
                }
            )
            for call in response.tool_calls:
                result = (
                    self._registry.get(call.name).run(call.arguments)
                    if call.name in self._registry
                    else f"Error: unknown tool '{call.name}'"
                )
                messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

        return "Stopped: reached the maximum number of tool-calling steps."
