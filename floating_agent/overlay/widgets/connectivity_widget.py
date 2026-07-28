"""Compact connectivity indicator for the Attention surface."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from floating_agent.adapters.local.connectivity_monitor import LocalConnectivityMonitor
from floating_agent.domain.connectivity_state import ConnectivityState

if TYPE_CHECKING:
    from floating_agent.ports.connectivity import ConnectivityMonitor

_STATE_LABELS = {
    ConnectivityState.OFFLINE: ("offline", "No remote providers configured"),
    ConnectivityState.DEGRADED: ("degraded", "Remote provider unavailable"),
    ConnectivityState.ONLINE: ("online", "Remote provider reachable"),
}


class ConnectivityWidget(QWidget):
    """Show a concise global state for the offline/online surface."""

    POLL_INTERVAL_MS = 15_000

    def __init__(self, monitor: ConnectivityMonitor | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._monitor = monitor if monitor is not None else LocalConnectivityMonitor()
        self._title = QLabel("Connectivity")
        self._state = QLabel()
        self._state.setObjectName("connectivityState")
        self._state.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self._title)
        layout.addWidget(self._state)

        self.refresh()

    def refresh(self) -> None:
        """Update the visible state from the configured monitor."""
        state = self._monitor.read_state()
        label, description = _STATE_LABELS[state]
        self._state.setText(f"{label}: {description}")
