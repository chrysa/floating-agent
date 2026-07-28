from pytestqt.qtbot import QtBot

from floating_agent.overlay.widgets.agent_icon_button import AgentIconButton
from floating_agent.overlay.window import OverlayWindow


def test_agent_icon_is_accessible_and_interactive(qtbot: QtBot) -> None:
    window = OverlayWindow()
    qtbot.addWidget(window)
    window.show()

    assert isinstance(window.agent_icon, AgentIconButton)
    assert window.agent_icon.accessibleName() == "Toggle assistant panel"
    assert not window.scroll_area.isVisible()
    assert window.agent_icon.text() == "●"

    window.agent_icon.click()

    assert window.scroll_area.isVisibleTo(window)
    assert window.docker_widget.isVisible()
