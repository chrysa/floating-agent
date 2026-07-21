from floating_agent.overlay.widgets.agent_icon_button import AgentIconButton
from floating_agent.overlay.window import OverlayWindow


def test_agent_icon_is_accessible_and_interactive(qtbot) -> None:
    window = OverlayWindow()
    qtbot.addWidget(window)

    assert isinstance(window.agent_icon, AgentIconButton)
    assert window.agent_icon.accessibleName() == "Toggle Attention view"
    assert window.docker_widget.isVisibleTo(window)

    window.agent_icon.click()

    assert not window.docker_widget.isVisibleTo(window)
