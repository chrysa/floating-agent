"""Phase 2 proactivity: the agent decides *when* to interrupt you.

A pulse periodically builds a context snapshot and asks a Decider whether to say
something. Anti-noise guardrail: a cooldown between proactive notifications.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from datetime import datetime

    from floating_agent.agent.client import LLMClient
    from floating_agent.plugins.system import SystemPlugin
    from floating_agent.proactive.notifier import Notifier
    from floating_agent.proactive.reminders import ReminderStore


@dataclass(frozen=True)
class ContextSnapshot:
    """What the decider reasons over to decide whether to interrupt."""

    system_summary: str
    pending_reminders: int


class Decider(Protocol):
    """Returns a short message to surface, or None to stay quiet."""

    def decide(self, snapshot: ContextSnapshot) -> str | None: ...


class NullDecider:
    """Never interrupts. Default until emergent AI proactivity is configured."""

    def decide(self, snapshot: ContextSnapshot) -> str | None:
        return None


class ProactivePulse:
    """Drives the decider on each pulse, enforcing an anti-noise cooldown."""

    def __init__(self, decider: Decider, notifier: Notifier, cooldown_seconds: float = 1800.0) -> None:
        self._decider = decider
        self._notifier = notifier
        self._cooldown_seconds = cooldown_seconds
        self._last_fired: datetime | None = None

    def pulse(self, snapshot: ContextSnapshot, now: datetime) -> bool:
        """Maybe interrupt. Returns True if a notification was fired."""
        if self._last_fired is not None:
            elapsed = (now - self._last_fired).total_seconds()
            if elapsed < self._cooldown_seconds:
                return False

        message = self._decider.decide(snapshot)
        if not message:
            return False

        self._notifier.notify("Floating Agent", message)
        self._last_fired = now
        return True


class LLMDecider:  # pragma: no cover - needs a live LLM
    """Asks the LLM whether the current context warrants interrupting the user."""

    def __init__(self, client: LLMClient) -> None:
        self._client = client

    def decide(self, snapshot: ContextSnapshot) -> str | None:
        prompt = (
            "You are a proactive assistant. Given this context, decide if anything "
            "needs the user's attention right now. Reply with ONE short sentence, or "
            "exactly NONE if not.\n"
            f"System: {snapshot.system_summary}\n"
            f"Pending reminders: {snapshot.pending_reminders}"
        )
        response = self._client.complete([{"role": "user", "content": prompt}], [])
        text = (response.text or "").strip()
        if not text or text.upper() == "NONE":
            return None
        return text


def build_snapshot(system_plugin: SystemPlugin, store: ReminderStore) -> ContextSnapshot:
    """Assemble the context the decider reasons over."""
    stats = system_plugin.get_stats()
    summary = f"CPU {stats.cpu_percent:.0f}%, RAM {stats.ram_percent:.0f}%, disk {stats.disk_percent:.0f}%"
    return ContextSnapshot(system_summary=summary, pending_reminders=len(store.pending()))
