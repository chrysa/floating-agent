"""Tests for the PySide6 overlay (run headless via QT_QPA_PLATFORM=offscreen)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QWidget

from floating_agent.models import SystemStats
from floating_agent.overlay.tray import build_tray
from floating_agent.overlay.widgets.system_widget import SystemWidget
from floating_agent.overlay.window import OverlayWindow

if TYPE_CHECKING:
    from pytestqt.qtbot import QtBot


class _FakePlugin:
    def get_stats(self) -> SystemStats:
        return SystemStats(
            cpu_percent=12.0,
            ram_used_gb=4.0,
            ram_total_gb=16.0,
            ram_percent=25.0,
            disk_used_gb=100.0,
            disk_total_gb=500.0,
            disk_percent=20.0,
        )


def _press(button: Qt.MouseButton, x: float = 5.0, y: float = 5.0) -> QMouseEvent:
    pos = QPointF(x, y)
    return QMouseEvent(QEvent.Type.MouseButtonPress, pos, pos, button, button, Qt.KeyboardModifier.NoModifier)


def _move(x: float, y: float) -> QMouseEvent:
    pos = QPointF(x, y)
    return QMouseEvent(
        QEvent.Type.MouseMove,
        pos,
        pos,
        Qt.MouseButton.NoButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )


def test_system_widget_renders_stats(qtbot: QtBot) -> None:
    widget = SystemWidget(plugin=_FakePlugin())
    qtbot.addWidget(widget)
    assert "12%" in widget._cpu.text()
    assert "4.0/16.0 GB" in widget._ram.text()
    assert "20%" in widget._disk.text()


def test_overlay_window_flags(qtbot: QtBot) -> None:
    window = OverlayWindow()
    qtbot.addWidget(window)
    flags = window.windowFlags()
    assert flags & Qt.WindowType.FramelessWindowHint
    assert flags & Qt.WindowType.WindowStaysOnTopHint
    assert window.width() <= 60
    assert window.height() <= 60


def test_overlay_window_drag_moves(qtbot: QtBot) -> None:
    window = OverlayWindow()
    qtbot.addWidget(window)
    window.move(0, 0)
    window.mousePressEvent(_press(Qt.MouseButton.LeftButton))
    window.mouseMoveEvent(_move(50, 40))
    window.mouseReleaseEvent(_press(Qt.MouseButton.LeftButton))
    assert window._drag_offset is None


def test_tray_toggle_hides_and_shows(qtbot: QtBot) -> None:
    app = QApplication.instance() or QApplication([])
    window = QWidget()
    qtbot.addWidget(window)
    window.show()
    tray = build_tray(app, window)  # type: ignore[arg-type]
    actions = tray.contextMenu().actions()
    toggle = actions[0]
    toggle.trigger()
    assert not window.isVisible()
    toggle.trigger()
    assert window.isVisible()


def test_tray_icon_click_toggles_window(qtbot: QtBot) -> None:
    app = QApplication.instance() or QApplication([])
    window = QWidget()
    qtbot.addWidget(window)
    window.show()
    tray = build_tray(app, window)  # type: ignore[arg-type]

    assert not tray.icon().isNull()
    assert "monitoring" in tray.toolTip()
    tray.activated.emit(QSystemTrayIcon.ActivationReason.Trigger)

    assert not window.isVisible()
