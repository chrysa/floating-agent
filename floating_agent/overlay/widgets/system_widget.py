"""System monitoring widget — polls the SystemPlugin and renders CPU/RAM/disk."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from floating_agent.plugins.system import SystemPlugin

if TYPE_CHECKING:
    from floating_agent.models import SystemStats


class StatsProvider(Protocol):
    """Anything that can return system stats (SystemPlugin, or a fake in tests)."""

    def get_stats(self) -> SystemStats: ...


class SystemWidget(QWidget):
    """Live CPU / RAM / disk readout, refreshed on a timer."""

    POLL_INTERVAL_MS = 2000

    def __init__(self, plugin: StatsProvider | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._plugin: StatsProvider = plugin if plugin is not None else SystemPlugin()

        self._cpu = QLabel()
        self._ram = QLabel()
        self._disk = QLabel()

        layout = QVBoxLayout(self)
        for label in (self._cpu, self._ram, self._disk):
            layout.addWidget(label)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(self.POLL_INTERVAL_MS)
        self.refresh()

    def refresh(self) -> None:
        """Pull fresh stats and update the labels."""
        stats = self._plugin.get_stats()
        self._cpu.setText(f"CPU {stats.cpu_percent:.0f}%")
        self._ram.setText(f"RAM {stats.ram_used_gb:.1f}/{stats.ram_total_gb:.1f} GB")
        self._disk.setText(f"Disk {stats.disk_percent:.0f}%")
