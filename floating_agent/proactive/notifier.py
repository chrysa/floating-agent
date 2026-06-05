"""Notification sinks for proactive events."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from PySide6.QtWidgets import QSystemTrayIcon


class Notifier(Protocol):
    """Anything that can surface a notification to the user."""

    def notify(self, title: str, message: str) -> None: ...


class TrayNotifier:  # pragma: no cover - needs a live Qt tray
    """Shows OS notifications via the system tray balloon."""

    def __init__(self, tray: QSystemTrayIcon) -> None:
        self._tray = tray

    def notify(self, title: str, message: str) -> None:
        self._tray.showMessage(title, message)
