"""Agent core — the brain: a tool-calling loop over a pluggable LLM client."""

from __future__ import annotations

import os

from floating_agent.adapters.local.assistant_settings_store import AssistantSettingsStore
from floating_agent.agent.client import LLMClient, StubClient
from floating_agent.agent.loop import Agent
from floating_agent.agent.tools import (
    ToolRegistry,
    build_alerts_tool,
    build_calendar_tool,
    build_kill_process_tool,
    build_messaging_tool,
    build_network_tool,
    build_notion_tools,
    build_reminder_tool,
    build_system_tool,
    build_top_processes_tool,
)
from floating_agent.proactive.reminders import ReminderStore


def build_default_registry(reminder_store: ReminderStore | None = None) -> ToolRegistry:
    """Registry with the built-in tools available out of the box.

    A reminder tool is added when a ReminderStore is provided. Notion tools are
    added when NOTION_API_KEY is set; the write tool only when NOTION_TASKS_DB_ID is too.
    """
    registry = ToolRegistry()
    registry.register(build_system_tool())
    registry.register(build_network_tool())
    registry.register(build_top_processes_tool())
    registry.register(build_kill_process_tool())
    registry.register(build_alerts_tool())

    if reminder_store is not None:
        registry.register(build_reminder_tool(reminder_store))

    notion_key = os.environ.get("NOTION_API_KEY")
    if notion_key:  # pragma: no cover - wiring requires real credentials
        from floating_agent.plugins.notion import NotionClient

        client = NotionClient(api_key=notion_key)
        for tool in build_notion_tools(client, os.environ.get("NOTION_TASKS_DB_ID")):
            registry.register(tool)

    calendar_token = os.environ.get("CALENDAR_ACCESS_TOKEN")
    if calendar_token:  # pragma: no cover - wiring requires real credentials
        from floating_agent.plugins.calendar import CalendarClient

        registry.register(build_calendar_tool(CalendarClient(access_token=calendar_token)))

    gmail_token = os.environ.get("GMAIL_ACCESS_TOKEN")
    if gmail_token:  # pragma: no cover - wiring requires real credentials
        from floating_agent.plugins.messaging import GmailClient

        registry.register(build_messaging_tool(GmailClient(access_token=gmail_token)))

    return registry


def build_default_agent(client: LLMClient | None = None, reminder_store: ReminderStore | None = None) -> Agent:
    """Build the default agent.

    The default client is the local Ollama backend, configured from the user-level
    assistant settings file. An explicit client still wins for tests or overrides.
    """
    if client is None:
        from floating_agent.adapters.local.ollama_client import OllamaClient

        settings = AssistantSettingsStore().load()
        client = StubClient() if settings.provider == "stub" else OllamaClient(settings)
    return Agent(client=client, registry=build_default_registry(reminder_store))


__all__ = [
    "Agent",
    "ReminderStore",
    "ToolRegistry",
    "build_default_agent",
    "build_default_registry",
]
