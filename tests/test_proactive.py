"""Tests for the proactive engine: reminders, scheduler, reminder tool."""

from __future__ import annotations

from datetime import datetime, timedelta

from floating_agent.agent.tools import build_reminder_tool
from floating_agent.proactive.reminders import Reminder, ReminderStore
from floating_agent.proactive.scheduler import ReminderScheduler

_NOW = datetime(2026, 6, 5, 12, 0, 0)


class _RecordingNotifier:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    def notify(self, title: str, message: str) -> None:
        self.sent.append((title, message))


def _store_with(*reminders: Reminder) -> ReminderStore:
    store = ReminderStore()
    for r in reminders:
        store.add(r)
    return store


def test_store_due_and_pending() -> None:
    past = Reminder(id="a", message="past", due_at=_NOW - timedelta(minutes=1))
    future = Reminder(id="b", message="future", due_at=_NOW + timedelta(minutes=10))
    store = _store_with(past, future)
    assert {r.id for r in store.due(_NOW)} == {"a"}
    assert {r.id for r in store.pending()} == {"a", "b"}


def test_scheduler_fires_due_and_marks_them() -> None:
    due = Reminder(id="a", message="standup", due_at=_NOW - timedelta(seconds=1))
    later = Reminder(id="b", message="lunch", due_at=_NOW + timedelta(hours=1))
    store = _store_with(due, later)
    notifier = _RecordingNotifier()
    scheduler = ReminderScheduler(store, notifier)

    assert scheduler.tick(_NOW) == 1
    assert notifier.sent == [("Reminder", "standup")]
    assert due.fired is True
    # second tick fires nothing new
    assert scheduler.tick(_NOW) == 0


def test_reminder_tool_schedules() -> None:
    store = ReminderStore()
    tool = build_reminder_tool(store, clock=lambda: _NOW)
    out = tool.run({"message": "call mum", "in_minutes": 15})
    assert "call mum" in out
    [reminder] = store.pending()
    assert reminder.message == "call mum"
    assert reminder.due_at == _NOW + timedelta(minutes=15)
