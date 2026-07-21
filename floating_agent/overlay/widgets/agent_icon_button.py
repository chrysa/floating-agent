"""Interactive in-window agent icon used when no system tray is available."""

from __future__ import annotations

from PySide6.QtWidgets import QToolButton, QWidget


class AgentIconButton(QToolButton):
    """Expose the Attention area through a compact keyboard-focusable icon."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setText("✦")
        self.setAccessibleName("Toggle Attention view")
        self.setToolTip("Show or hide local Attention activity")
        self.setCheckable(True)
        self.setChecked(True)
        self.setFixedSize(36, 36)
