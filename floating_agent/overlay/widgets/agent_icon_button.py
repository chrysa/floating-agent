"""Interactive in-window agent icon used when no system tray is available."""

from __future__ import annotations

from PySide6.QtWidgets import QToolButton, QWidget


class AgentIconButton(QToolButton):
    """Expose the assistant panel through a compact keyboard-focusable icon."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setText("●")
        self.setAccessibleName("Toggle assistant panel")
        self.setToolTip("Show or hide the assistant panel")
        self.setCheckable(True)
        self.setChecked(False)
        self.setFixedSize(28, 28)
