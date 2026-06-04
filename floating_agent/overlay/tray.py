"""System tray icon with show/hide + quit, so the overlay is never lost."""

from __future__ import annotations

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon, QWidget


def _toggle(window: QWidget) -> None:
    if window.isVisible():
        window.hide()
    else:
        window.show()


def build_tray(app: QApplication, window: QWidget) -> QSystemTrayIcon:
    """Create and show a tray icon controlling the given window.

    The tray is parented to ``app`` so Qt keeps it alive without a Python ref.
    """
    tray = QSystemTrayIcon(QIcon(), app)
    tray.setToolTip("Floating Agent")

    menu = QMenu()
    menu.addAction("Show / Hide").triggered.connect(lambda: _toggle(window))
    menu.addAction("Quit").triggered.connect(app.quit)
    tray.setContextMenu(menu)

    tray.show()
    return tray
