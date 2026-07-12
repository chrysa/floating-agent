"""Tool abstraction + registry exposed to the agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Protocol
from uuid import uuid4

from floating_agent.proactive.reminders import Reminder

if TYPE_CHECKING:
    from collections.abc import Callable

    from floating_agent.plugins.calendar import CalendarEvent
    from floating_agent.plugins.notion import NotionPage
    from floating_agent.proactive.reminders import ReminderStore

from floating_agent.alerts import AlertEngine
from floating_agent.plugins.network import NetworkPlugin
from floating_agent.plugins.processes import ProcessPlugin
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


def build_network_tool(plugin: NetworkPlugin | None = None) -> Tool:
    """Tool returning a one-line network throughput + connection-count summary."""
    resolved = plugin if plugin is not None else NetworkPlugin()

    def handler(_arguments: dict[str, Any]) -> str:
        stats = resolved.get_stats()
        return (
            f"Network up {stats.sent_mb_s:.2f} MB/s, "
            f"down {stats.recv_mb_s:.2f} MB/s, "
            f"{stats.connections} connections"
        )

    return Tool(
        name="get_network_stats",
        description="Get the current network upload/download throughput and active connection count.",
        parameters={"type": "object", "properties": {}},
        handler=handler,
    )


def build_top_processes_tool(plugin: ProcessPlugin | None = None) -> Tool:
    """Tool listing the top processes by CPU usage."""
    resolved = plugin if plugin is not None else ProcessPlugin()

    def handler(arguments: dict[str, Any]) -> str:
        limit = int(arguments.get("limit", 5))
        procs = resolved.top(limit=limit)
        if not procs:
            return "No processes found."
        return "\n".join(f"- {p.name} (pid {p.pid}): CPU {p.cpu_percent:.0f}%, RAM {p.ram_mb:.0f} MB" for p in procs)

    return Tool(
        name="get_top_processes",
        description="List the top processes by CPU usage (default 5).",
        parameters={
            "type": "object",
            "properties": {"limit": {"type": "integer", "description": "How many processes to return."}},
        },
        handler=handler,
    )


def build_kill_process_tool(plugin: ProcessPlugin | None = None) -> Tool:
    """Tool terminating a process by pid. Destructive → requires confirmation."""
    resolved = plugin if plugin is not None else ProcessPlugin()

    def handler(arguments: dict[str, Any]) -> str:
        pid = int(arguments["pid"])
        resolved.kill(pid)
        return f"Sent terminate signal to process {pid}."

    return Tool(
        name="kill_process",
        description="Terminate a process by its pid. This is destructive.",
        parameters={
            "type": "object",
            "properties": {"pid": {"type": "integer", "description": "The pid of the process to terminate."}},
            "required": ["pid"],
        },
        handler=handler,
        requires_confirmation=True,
    )


def build_alerts_tool(engine: AlertEngine | None = None, plugin: SystemPlugin | None = None) -> Tool:
    """Tool reporting system metrics that breach their configured thresholds."""
    resolved_engine = engine if engine is not None else AlertEngine.from_config()
    resolved_plugin = plugin if plugin is not None else SystemPlugin()

    def handler(_arguments: dict[str, Any]) -> str:
        alerts = resolved_engine.evaluate(resolved_plugin.get_stats())
        if not alerts:
            return "No active alerts."
        return "\n".join(f"ALERT {a.metric} {a.value:.0f}% >= {a.threshold:.0f}%" for a in alerts)

    return Tool(
        name="get_alerts",
        description="List system metrics currently breaching their configured alert thresholds.",
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


def build_reminder_tool(store: ReminderStore, clock: Callable[[], datetime] = datetime.now) -> Tool:
    """Tool letting the agent schedule a reminder N minutes from now."""

    def handler(arguments: dict[str, Any]) -> str:
        message = str(arguments["message"])
        minutes = float(arguments.get("in_minutes", 0))
        due_at = clock() + timedelta(minutes=minutes)
        store.add(Reminder(id=uuid4().hex, message=message, due_at=due_at))
        return f"Reminder set for {due_at:%Y-%m-%d %H:%M}: {message}"

    return Tool(
        name="create_reminder",
        description="Schedule a reminder to fire after a number of minutes.",
        parameters={
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "in_minutes": {"type": "number"},
            },
            "required": ["message", "in_minutes"],
        },
        handler=handler,
    )


class CalendarLike(Protocol):
    def upcoming(self, max_results: int = 5) -> list[CalendarEvent]: ...


class GmailLike(Protocol):
    def unread_count(self) -> int: ...


def build_calendar_tool(client: CalendarLike) -> Tool:
    """Read tool: list the user's upcoming calendar events."""

    def handler(_arguments: dict[str, Any]) -> str:
        events = client.upcoming()
        if not events:
            return "No upcoming events."
        return "\n".join(f"- {e.start}: {e.summary}" for e in events)

    return Tool(
        name="calendar_upcoming",
        description="List the user's upcoming calendar events.",
        parameters={"type": "object", "properties": {}},
        handler=handler,
    )


def build_messaging_tool(client: GmailLike) -> Tool:
    """Read tool: summarise the user's unread Gmail count."""

    def handler(_arguments: dict[str, Any]) -> str:
        return f"You have {client.unread_count()} unread email(s)."

    return Tool(
        name="gmail_summary",
        description="Summarise the user's unread email count.",
        parameters={"type": "object", "properties": {}},
        handler=handler,
    )
