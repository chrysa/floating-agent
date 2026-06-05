"""Cron-like in-process scheduler: fires due reminders through a notifier."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from floating_agent.proactive.notifier import Notifier
    from floating_agent.proactive.reminders import ReminderStore


class ReminderScheduler:
    """On each tick, notifies for every reminder now due and marks it fired."""

    def __init__(self, store: ReminderStore, notifier: Notifier) -> None:
        self._store = store
        self._notifier = notifier

    def tick(self, now: datetime) -> int:
        """Fire all reminders due at ``now``. Returns how many fired."""
        due = self._store.due(now)
        for reminder in due:
            self._notifier.notify("Reminder", reminder.message)
            self._store.mark_fired(reminder)
        return len(due)
