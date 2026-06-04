"""Frameless, always-on-top, translucent overlay window with drag-to-move."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from floating_agent.overlay.widgets.system_widget import SystemWidget

if TYPE_CHECKING:
    from PySide6.QtCore import QPoint
    from PySide6.QtGui import QMouseEvent


class OverlayWindow(QWidget):
    """The floating overlay. Hosts the module widgets; draggable by its body."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(280, 160)

        layout = QVBoxLayout(self)
        layout.addWidget(SystemWidget())

        self._drag_offset: QPoint | None = None

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802 (Qt override)
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802 (Qt override)
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802 (Qt override)
        self._drag_offset = None
        event.accept()
