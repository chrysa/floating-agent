"""Overlay application entry point."""

from __future__ import annotations

import sys
from datetime import datetime

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from floating_agent.agent import build_default_agent
from floating_agent.overlay.tray import build_tray
from floating_agent.overlay.window import OverlayWindow
from floating_agent.proactive.notifier import TrayNotifier
from floating_agent.proactive.reminders import ReminderStore
from floating_agent.proactive.scheduler import ReminderScheduler

_TICK_MS = 30_000


def run() -> int:  # pragma: no cover - starts the Qt event loop
    """Launch the overlay, wire the proactive scheduler, run the Qt event loop."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    store = ReminderStore()
    agent = build_default_agent(reminder_store=store)

    window = OverlayWindow(agent=agent)
    window.show()
    tray = build_tray(app, window)

    scheduler = ReminderScheduler(store, TrayNotifier(tray))
    timer = QTimer()
    timer.timeout.connect(lambda: scheduler.tick(datetime.now()))
    timer.start(_TICK_MS)

    return app.exec()
