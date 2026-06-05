"""Agent core — the brain: a tool-calling loop over a pluggable LLM client."""

from __future__ import annotations

import os

from floating_agent.agent.client import LLMClient, StubClient
from floating_agent.agent.loop import Agent
from floating_agent.agent.tools import (
    ToolRegistry,
    build_notion_tools,
    build_reminder_tool,
    build_system_tool,
)
from floating_agent.proactive.reminders import ReminderStore


def build_default_registry(reminder_store: ReminderStore | None = None) -> ToolRegistry:
    """Registry with the built-in tools available out of the box.

    A reminder tool is added when a ReminderStore is provided. Notion tools are
    added when NOTION_API_KEY is set; the write tool only when NOTION_TASKS_DB_ID is too.
    """
    registry = ToolRegistry()
    registry.register(build_system_tool())

    if reminder_store is not None:
        registry.register(build_reminder_tool(reminder_store))

    notion_key = os.environ.get("NOTION_API_KEY")
    if notion_key:  # pragma: no cover - wiring requires real credentials
        from floating_agent.plugins.notion import NotionClient

        client = NotionClient(api_key=notion_key)
        for tool in build_notion_tools(client, os.environ.get("NOTION_TASKS_DB_ID")):
            registry.register(tool)

    return registry


def build_default_agent(client: LLMClient | None = None, reminder_store: ReminderStore | None = None) -> Agent:
    """Build the default agent.

    Without a configured ``AI_AGGREGATOR_URL`` (and no explicit client), falls back
    to a StubClient so the overlay stays usable before AI routing is wired up.
    """
    if client is None:
        url = os.environ.get("AI_AGGREGATOR_URL")
        client = _build_aggregator_client(url) if url else StubClient()
    return Agent(client=client, registry=build_default_registry(reminder_store))


def _build_aggregator_client(url: str) -> LLMClient:  # pragma: no cover - needs ai-aggregator
    from floating_agent.agent.client import AggregatorClient

    return AggregatorClient(base_url=url)


__all__ = [
    "Agent",
    "ReminderStore",
    "ToolRegistry",
    "build_default_agent",
    "build_default_registry",
]
