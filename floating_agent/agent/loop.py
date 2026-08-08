"""The tool-calling loop: prompt -> (tool calls -> results)* -> final answer."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

    from floating_agent.agent.client import LLMClient
    from floating_agent.agent.tools import Tool, ToolRegistry

    ConfirmCallback = Callable[[Tool, dict[str, Any]], bool]


class Agent:
    """Drives an LLM client through tool calls until it returns a final answer."""

    MAX_STEPS = 5

    def __init__(
        self,
        client: LLMClient,
        registry: ToolRegistry,
        confirm: ConfirmCallback | None = None,
    ) -> None:
        self._client = client
        self._registry = registry
        # Confirmation gate for tools flagged ``requires_confirmation`` (sensitive
        # writes). When no callback is wired, such tools are denied by default so a
        # model tool-call can never trigger a real write without an explicit approval.
        self._confirm = confirm

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
            messages.extend(
                {"role": "tool", "tool_call_id": call.id, "content": self._run_call(call)}
                for call in response.tool_calls
            )

        return "Stopped: reached the maximum number of tool-calling steps."

    def _run_call(self, call: Any) -> str:
        """Execute one tool call, enforcing the confirmation gate on sensitive tools."""
        if call.name not in self._registry:
            return f"Error: unknown tool '{call.name}'"
        tool = self._registry.get(call.name)
        if tool.requires_confirmation and not self._is_confirmed(tool, call.arguments):
            return f"Confirmation required: '{tool.name}' is a sensitive action and was not executed without approval."
        return tool.run(call.arguments)

    def _is_confirmed(self, tool: Tool, arguments: dict[str, Any]) -> bool:
        """Deny sensitive tools by default; approve only when a callback opts in."""
        return self._confirm is not None and self._confirm(tool, arguments)
