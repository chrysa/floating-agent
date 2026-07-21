"""Frameless, always-on-top, translucent overlay window with drag-to-move."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from floating_agent.agent import build_default_agent
from floating_agent.overlay.widgets.chat_widget import ChatWidget
from floating_agent.overlay.widgets.docker_widget import DockerWidget
from floating_agent.overlay.widgets.system_widget import SystemWidget

if TYPE_CHECKING:
    from PySide6.QtCore import QPoint
    from PySide6.QtGui import QMouseEvent

    from floating_agent.agent.loop import Agent


class OverlayWindow(QWidget):
    """The floating overlay. Hosts the module widgets; draggable by its body."""

    def __init__(self, agent: Agent | None = None) -> None:
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(320, 520)

        resolved_agent = agent if agent is not None else build_default_agent()
        layout = QVBoxLayout(self)
        layout.addWidget(SystemWidget())
        self.docker_widget = DockerWidget()
        layout.addWidget(self.docker_widget)
        layout.addWidget(ChatWidget(responder=resolved_agent.run))

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
