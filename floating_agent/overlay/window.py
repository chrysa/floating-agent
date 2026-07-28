"""Frameless, always-on-top, translucent overlay window with drag-to-move."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from floating_agent.adapters.local.assistant_settings_store import AssistantSettingsStore
from floating_agent.agent import build_default_agent
from floating_agent.overlay.widgets.agent_icon_button import AgentIconButton
from floating_agent.overlay.widgets.assistant_config_widget import AssistantConfigWidget
from floating_agent.overlay.widgets.attention_widget import AttentionWidget
from floating_agent.overlay.widgets.chat_widget import ChatWidget
from floating_agent.overlay.widgets.connectivity_widget import ConnectivityWidget
from floating_agent.overlay.widgets.docker_widget import DockerWidget
from floating_agent.overlay.widgets.outbox_widget import OutboxWidget
from floating_agent.overlay.widgets.search_widget import SearchWidget
from floating_agent.overlay.widgets.system_widget import SystemWidget

if TYPE_CHECKING:
    from PySide6.QtCore import QPoint
    from PySide6.QtGui import QMouseEvent

    from floating_agent.agent.loop import Agent
    from floating_agent.ports.local_search import LocalSearchIndex
    from floating_agent.ports.local_store import LocalStore
    from floating_agent.ports.outbox import Outbox


class OverlayWindow(QWidget):
    """The floating overlay. Hosts the module widgets; draggable by its body."""

    def __init__(
        self,
        agent: Agent | None = None,
        local_store: LocalStore | None = None,
        local_search: LocalSearchIndex | None = None,
        outbox: Outbox | None = None,
    ) -> None:
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._collapsed_width = 52
        self._collapsed_height = 52
        self._expanded_width = 360
        self._expanded_height = 660
        self.setFixedSize(self._collapsed_width, self._collapsed_height)

        resolved_agent = agent if agent is not None else build_default_agent()
        self._assistant_settings_store = AssistantSettingsStore()
        self._assistant_agent = resolved_agent
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(0)
        self.agent_icon = AgentIconButton()
        layout.addWidget(self.agent_icon)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        layout.addWidget(self.scroll_area)

        content = QWidget()
        self.scroll_area.setWidget(content)
        content_layout = QVBoxLayout(content)
        self.config_widget = AssistantConfigWidget(
            store=self._assistant_settings_store,
            on_saved=self._on_assistant_settings_saved,
        )
        content_layout.addWidget(self.config_widget)
        self.connectivity_widget = ConnectivityWidget()
        content_layout.addWidget(self.connectivity_widget)
        self.search_widget = SearchWidget(search_index=local_search)
        content_layout.addWidget(self.search_widget)
        self.attention_widget = AttentionWidget(store=local_store)
        content_layout.addWidget(self.attention_widget)
        self.outbox_widget = OutboxWidget(outbox=outbox)
        content_layout.addWidget(self.outbox_widget)
        content_layout.addWidget(SystemWidget())
        self.docker_widget = DockerWidget()
        content_layout.addWidget(self.docker_widget)
        self.chat_widget = ChatWidget(responder=resolved_agent.run)
        content_layout.addWidget(self.chat_widget)

        self.agent_icon.toggled.connect(self._set_expanded)
        self._set_expanded(False)

        self._drag_offset: QPoint | None = None

    def _set_expanded(self, expanded: bool) -> None:
        self.scroll_area.setVisible(expanded)
        self.docker_widget.setVisible(expanded)
        self.setFixedSize(
            self._expanded_width if expanded else self._collapsed_width,
            self._expanded_height if expanded else self._collapsed_height,
        )
        if self.agent_icon.isChecked() != expanded:
            self.agent_icon.blockSignals(True)
            self.agent_icon.setChecked(expanded)
            self.agent_icon.blockSignals(False)

    def _on_assistant_settings_saved(self, _settings: object) -> None:
        self._assistant_agent = build_default_agent()
        self.chat_widget.set_responder(self._assistant_agent.run)

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
