"""System tray icon with show/hide + quit, so the overlay is never lost."""

from __future__ import annotations

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMenu, QStyle, QSystemTrayIcon, QWidget


def _toggle(window: QWidget) -> None:
    if window.isVisible():
        window.hide()
    else:
        window.show()
        window.raise_()
        window.activateWindow()


def _activate(window: QWidget, reason: QSystemTrayIcon.ActivationReason) -> None:
    if reason in {
        QSystemTrayIcon.ActivationReason.Trigger,
        QSystemTrayIcon.ActivationReason.DoubleClick,
    }:
        _toggle(window)


def build_tray(app: QApplication, window: QWidget) -> QSystemTrayIcon:
    """Create and show a tray icon controlling the given window.

    The tray is parented to ``app`` so Qt keeps it alive without a Python ref.
    """
    fallback = window.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
    icon = QIcon.fromTheme("preferences-system-notifications", fallback)
    tray = QSystemTrayIcon(icon, app)
    tray.setToolTip("floating-agent — monitoring local activity")

    menu = QMenu()
    menu.addAction("Show / Hide").triggered.connect(lambda: _toggle(window))
    menu.addAction("Quit").triggered.connect(app.quit)
    tray.setContextMenu(menu)
    tray.activated.connect(lambda reason: _activate(window, reason))

    tray.show()
    return tray
