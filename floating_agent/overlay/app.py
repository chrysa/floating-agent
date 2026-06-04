"""Overlay application entry point."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from floating_agent.overlay.tray import build_tray
from floating_agent.overlay.window import OverlayWindow


def run() -> int:  # pragma: no cover - starts the Qt event loop
    """Launch the overlay and run the Qt event loop."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = OverlayWindow()
    window.show()
    build_tray(app, window)  # parented to app; kept alive by Qt

    return app.exec()
