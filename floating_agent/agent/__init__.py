"""Agent core — the brain: a tool-calling loop over a pluggable LLM client."""

from __future__ import annotations

import os

from floating_agent.agent.client import LLMClient, StubClient
from floating_agent.agent.loop import Agent
from floating_agent.agent.tools import ToolRegistry, build_system_tool


def build_default_registry() -> ToolRegistry:
    """Registry with the built-in tools available out of the box."""
    registry = ToolRegistry()
    registry.register(build_system_tool())
    return registry


def build_default_agent(client: LLMClient | None = None) -> Agent:
    """Build the default agent.

    Without a configured ``AI_AGGREGATOR_URL`` (and no explicit client), falls back
    to a StubClient so the overlay stays usable before AI routing is wired up.
    """
    if client is None:
        url = os.environ.get("AI_AGGREGATOR_URL")
        client = _build_aggregator_client(url) if url else StubClient()
    return Agent(client=client, registry=build_default_registry())


def _build_aggregator_client(url: str) -> LLMClient:  # pragma: no cover - needs ai-aggregator
    from floating_agent.agent.client import AggregatorClient

    return AggregatorClient(base_url=url)


__all__ = ["Agent", "ToolRegistry", "build_default_agent", "build_default_registry"]
