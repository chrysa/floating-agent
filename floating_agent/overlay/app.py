"""Overlay application entry point."""

from __future__ import annotations

import os
import sys
from datetime import datetime

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from floating_agent.agent import build_default_agent
from floating_agent.overlay.tray import build_tray
from floating_agent.overlay.window import OverlayWindow
from floating_agent.plugins.system import SystemPlugin
from floating_agent.proactive.notifier import TrayNotifier
from floating_agent.proactive.pulse import Decider, NullDecider, ProactivePulse, build_snapshot
from floating_agent.proactive.reminders import ReminderStore
from floating_agent.proactive.scheduler import ReminderScheduler

_TICK_MS = 30_000
_PULSE_MS = 300_000


def _build_decider() -> Decider:
    url = os.environ.get("AI_AGGREGATOR_URL")
    if not url:
        return NullDecider()
    from floating_agent.agent.client import AggregatorClient
    from floating_agent.proactive.pulse import LLMDecider

    return LLMDecider(AggregatorClient(base_url=url))


def run() -> int:  # pragma: no cover - starts the Qt event loop
    """Launch the overlay, wire the proactive scheduler, run the Qt event loop."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    store = ReminderStore()
    agent = build_default_agent(reminder_store=store)

    window = OverlayWindow(agent=agent)
    window.show()
    tray = build_tray(app, window)

    notifier = TrayNotifier(tray)
    system_plugin = SystemPlugin()

    scheduler = ReminderScheduler(store, notifier)
    timer = QTimer()
    timer.timeout.connect(lambda: scheduler.tick(datetime.now()))
    timer.start(_TICK_MS)

    # Phase 2: emergent proactivity (silent NullDecider unless AI is configured)
    pulse = ProactivePulse(_build_decider(), notifier)
    pulse_timer = QTimer()
    pulse_timer.timeout.connect(lambda: pulse.pulse(build_snapshot(system_plugin, store), datetime.now()))
    pulse_timer.start(_PULSE_MS)

    return app.exec()
