"""Tests for Phase 2 proactivity (emergent pulse + cooldown)."""

from __future__ import annotations

from datetime import datetime, timedelta

from floating_agent.plugins.system import SystemPlugin
from floating_agent.proactive.pulse import (
    ContextSnapshot,
    NullDecider,
    ProactivePulse,
    build_snapshot,
)
from floating_agent.proactive.reminders import Reminder, ReminderStore

_NOW = datetime(2026, 6, 5, 12, 0, 0)
_SNAP = ContextSnapshot(system_summary="CPU 5%", pending_reminders=0)


class _Notifier:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    def notify(self, title: str, message: str) -> None:
        self.sent.append((title, message))


class _Decider:
    def __init__(self, message: str | None) -> None:
        self._message = message

    def decide(self, snapshot: ContextSnapshot) -> str | None:
        return self._message


def test_null_decider_never_fires() -> None:
    notifier = _Notifier()
    pulse = ProactivePulse(NullDecider(), notifier)
    assert pulse.pulse(_SNAP, _NOW) is False
    assert notifier.sent == []


def test_pulse_fires_when_decider_speaks() -> None:
    notifier = _Notifier()
    pulse = ProactivePulse(_Decider("Your disk is nearly full."), notifier)
    assert pulse.pulse(_SNAP, _NOW) is True
    assert notifier.sent == [("Floating Agent", "Your disk is nearly full.")]


def test_cooldown_suppresses_second_pulse() -> None:
    notifier = _Notifier()
    pulse = ProactivePulse(_Decider("hi"), notifier, cooldown_seconds=1800)
    assert pulse.pulse(_SNAP, _NOW) is True
    assert pulse.pulse(_SNAP, _NOW + timedelta(minutes=10)) is False
    assert pulse.pulse(_SNAP, _NOW + timedelta(minutes=40)) is True
    assert len(notifier.sent) == 2


def test_build_snapshot_counts_pending() -> None:
    store = ReminderStore()
    store.add(Reminder(id="a", message="x", due_at=_NOW))
    snap = build_snapshot(SystemPlugin(), store)
    assert snap.pending_reminders == 1
    assert "CPU" in snap.system_summary
