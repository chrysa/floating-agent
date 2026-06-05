"""Reminder model + in-memory store (Phase 1: explicit reminders)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass
class Reminder:
    """A one-shot reminder fired once its due time has passed."""

    id: str
    message: str
    due_at: datetime
    fired: bool = False


@dataclass
class ReminderStore:
    """Holds reminders and reports which are due. Notion-backed persistence later."""

    _items: list[Reminder] = field(default_factory=list)

    def add(self, reminder: Reminder) -> None:
        self._items.append(reminder)

    def pending(self) -> list[Reminder]:
        return [r for r in self._items if not r.fired]

    def due(self, now: datetime) -> list[Reminder]:
        return [r for r in self._items if not r.fired and r.due_at <= now]

    def mark_fired(self, reminder: Reminder) -> None:
        reminder.fired = True
