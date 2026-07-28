from floating_agent.domain.connectivity_state import ConnectivityState
from floating_agent.overlay.widgets.connectivity_widget import ConnectivityWidget


class _FakeMonitor:
    def __init__(self, state: ConnectivityState) -> None:
        self._state = state

    def read_state(self) -> ConnectivityState:
        return self._state


def test_connectivity_widget_renders_state(qtbot) -> None:
    widget = ConnectivityWidget(monitor=_FakeMonitor(ConnectivityState.ONLINE))
    qtbot.addWidget(widget)

    assert "online" in widget._state.text()
    assert "reachable" in widget._state.text()
