"""Tool abstraction + registry exposed to the agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable

    from floating_agent.plugins.notion import NotionPage

from floating_agent.plugins.system import SystemPlugin


@dataclass(frozen=True)
class Tool:
    """A callable the agent can invoke, described by a JSON-schema input."""

    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[[dict[str, Any]], str]
    requires_confirmation: bool = False

    def run(self, arguments: dict[str, Any]) -> str:
        return self.handler(arguments)


@dataclass
class ToolRegistry:
    """Holds the tools available to the agent and renders their specs."""

    _tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self._tools[name]

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def specs(self) -> list[dict[str, Any]]:
        """Anthropic-style tool specs."""
        return [
            {"name": t.name, "description": t.description, "input_schema": t.parameters} for t in self._tools.values()
        ]


def build_system_tool(plugin: SystemPlugin | None = None) -> Tool:
    """Tool returning a one-line CPU/RAM/disk summary."""
    resolved = plugin if plugin is not None else SystemPlugin()

    def handler(_arguments: dict[str, Any]) -> str:
        stats = resolved.get_stats()
        return (
            f"CPU {stats.cpu_percent:.0f}%, "
            f"RAM {stats.ram_percent:.0f}% "
            f"({stats.ram_used_gb:.1f}/{stats.ram_total_gb:.1f} GB), "
            f"disk {stats.disk_percent:.0f}%"
        )

    return Tool(
        name="get_system_stats",
        description="Get the current CPU, RAM and disk usage of this machine.",
        parameters={"type": "object", "properties": {}},
        handler=handler,
    )


class NotionLike(Protocol):
    """Subset of NotionClient the agent tools need (kept fake-able in tests)."""

    def search(self, query: str) -> list[NotionPage]: ...

    def create_task(self, database_id: str, title: str) -> NotionPage: ...


def build_notion_tools(client: NotionLike, database_id: str | None = None) -> list[Tool]:
    """Read tool (search) and, if a database is configured, a write tool (create task)."""

    def search_handler(arguments: dict[str, Any]) -> str:
        query = str(arguments.get("query", ""))
        results = client.search(query)
        if not results:
            return "No matching Notion pages."
        return "\n".join(f"- {p.title} ({p.url})" for p in results)

    tools = [
        Tool(
            name="notion_search",
            description="Search the user's Notion workspace for pages matching a query.",
            parameters={
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
            handler=search_handler,
        )
    ]

    if database_id is not None:

        def create_handler(arguments: dict[str, Any]) -> str:
            page = client.create_task(database_id, str(arguments["title"]))
            return f"Created task '{page.title}' ({page.url})"

        tools.append(
            Tool(
                name="notion_create_task",
                description="Create a new task in the user's Notion tasks database.",
                parameters={
                    "type": "object",
                    "properties": {"title": {"type": "string"}},
                    "required": ["title"],
                },
                handler=create_handler,
                requires_confirmation=True,
            )
        )

    return tools
