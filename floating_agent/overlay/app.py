"""Overlay application entry point."""

from __future__ import annotations

import os
import sys
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer
from PySide6.QtNetwork import QLocalServer
from PySide6.QtWidgets import QApplication

from floating_agent.adapters.local.docker_cli_monitor import DockerCliMonitor
from floating_agent.adapters.local.sqlite_local_search_index import SqliteLocalSearchIndex
from floating_agent.adapters.local.sqlite_local_store import SqliteLocalStore
from floating_agent.adapters.local.sqlite_outbox import SqliteOutbox
from floating_agent.agent import build_default_agent
from floating_agent.domain.container_event_kind import ContainerEventKind
from floating_agent.overlay.tray import build_tray
from floating_agent.overlay.window import OverlayWindow
from floating_agent.plugins.system import SystemPlugin
from floating_agent.proactive.notifier import TrayNotifier
from floating_agent.proactive.pulse import Decider, NullDecider, ProactivePulse, build_snapshot
from floating_agent.proactive.reminders import ReminderStore
from floating_agent.proactive.scheduler import ReminderScheduler

if TYPE_CHECKING:
    from floating_agent.domain.container_lifecycle_event import ContainerLifecycleEvent

_TICK_MS = 30_000
_PULSE_MS = 300_000
_DOCKER_POLL_MS = 30_000
_DOCKER_TIMEOUT_SECONDS = 5.0
_IPC_SERVER_NAME = "floating-agent-overlay"


def _build_decider() -> Decider:
    url = os.environ.get("AI_AGGREGATOR_URL")
    if not url:
        return NullDecider()
    from floating_agent.agent.client import AggregatorClient
    from floating_agent.proactive.pulse import LLMDecider

    return LLMDecider(AggregatorClient(base_url=url))


def run() -> int:  # pragma: no cover - starts the Qt event loop
    """Launch the overlay, wire the proactive scheduler, run the Qt event loop."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    store = ReminderStore()
    agent = build_default_agent(reminder_store=store)
    local_store = _build_local_store()
    local_search = _build_local_search_index()
    outbox = _build_outbox()

    window = OverlayWindow(agent=agent, local_store=local_store, local_search=local_search, outbox=outbox)
    window.show()
    _install_ipc_server(app, window)
    tray = build_tray(app, window)

    notifier = TrayNotifier(tray)
    system_plugin = SystemPlugin()

    docker_monitor = DockerCliMonitor(timeout_seconds=_DOCKER_TIMEOUT_SECONDS)
    docker_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="docker-events")
    last_docker_check = datetime.now(UTC)
    docker_future: Future[list[ContainerLifecycleEvent]] | None = None

    def poll_docker() -> None:
        nonlocal docker_future, last_docker_check
        if docker_future is not None and not docker_future.done():
            return
        if docker_future is not None:
            try:
                events = docker_future.result()
            except RuntimeError as error:
                tray.setToolTip(f"floating-agent — Docker degraded: {error}")
            else:
                window.docker_widget.add_events(events)
                _notify_docker_events(events, notifier)
                tray.setToolTip("floating-agent — Docker monitoring online")
        until = datetime.now(UTC)
        since = last_docker_check
        last_docker_check = until
        docker_future = docker_executor.submit(lambda: list(docker_monitor.read_events(since=since, until=until)))

    poll_docker()
    docker_timer = QTimer()
    docker_timer.timeout.connect(poll_docker)
    docker_timer.start(_DOCKER_POLL_MS)
    app.aboutToQuit.connect(lambda: docker_executor.shutdown(wait=False, cancel_futures=True))

    scheduler = ReminderScheduler(store, notifier)
    timer = QTimer()
    timer.timeout.connect(lambda: scheduler.tick(datetime.now()))
    timer.start(_TICK_MS)

    # Phase 2: emergent proactivity (silent NullDecider unless AI is configured)
    pulse = ProactivePulse(_build_decider(), notifier)
    pulse_timer = QTimer()
    pulse_timer.timeout.connect(lambda: pulse.pulse(build_snapshot(system_plugin, store), datetime.now()))
    pulse_timer.start(_PULSE_MS)

    return app.exec()


def _install_ipc_server(app: QApplication, window: OverlayWindow) -> None:
    QLocalServer.removeServer(_IPC_SERVER_NAME)
    server = QLocalServer(app)
    if not server.listen(_IPC_SERVER_NAME):
        return
    server.newConnection.connect(lambda: _handle_ipc_connections(server, window))


def _handle_ipc_connections(server: QLocalServer, window: OverlayWindow) -> None:
    while server.hasPendingConnections():
        socket = server.nextPendingConnection()
        if socket is None:
            continue
        if socket.waitForReadyRead(100):
            payload = bytes(socket.readAll().data()).decode("utf-8", errors="ignore").strip().lower()
        else:
            payload = ""
        if payload == "toggle":
            _toggle_window(window)
        socket.write(b"ok\n")
        socket.flush()
        socket.disconnectFromServer()
        socket.waitForDisconnected(100)


def _toggle_window(window: OverlayWindow) -> None:
    if window.isVisible():
        window.hide()
        return
    window.show()
    window.raise_()
    window.activateWindow()


def _notify_docker_events(events: list[ContainerLifecycleEvent], notifier: TrayNotifier) -> None:
    for event in events:
        if event.kind in {ContainerEventKind.STARTED, ContainerEventKind.RESTARTED, ContainerEventKind.CRASHED}:
            notifier.notify("Docker activity", f"{event.container_name}: {event.kind.value}")


def _build_local_store() -> SqliteLocalStore:
    return SqliteLocalStore(_local_store_path())


def _build_local_search_index() -> SqliteLocalSearchIndex:
    return SqliteLocalSearchIndex(_local_store_path())


def _local_store_path() -> Path:
    override = os.environ.get("FLOATING_AGENT_LOCAL_STORE")
    if override:
        return Path(override)
    base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    return base / "floating-agent" / "local-store.sqlite3"


def _build_outbox() -> SqliteOutbox:
    override = os.environ.get("FLOATING_AGENT_OUTBOX")
    if override:
        return SqliteOutbox(Path(override))
    base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state"))
    return SqliteOutbox(base / "floating-agent" / "outbox.sqlite3")
