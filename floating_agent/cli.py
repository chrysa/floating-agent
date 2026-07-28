"""Command-line entrypoint and local diagnostics for the desktop overlay."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from shutil import which

import httpx
from PySide6.QtNetwork import QLocalSocket
from PySide6.QtWidgets import QApplication

from floating_agent.adapters.local.assistant_settings_store import AssistantSettingsStore
from floating_agent.overlay.app import run

_IPC_SERVER_NAME = "floating-agent-overlay"


@dataclass(frozen=True)
class DoctorCheck:
    """A single diagnostic result."""

    name: str
    status: str
    detail: str


def main(argv: list[str] | None = None) -> int:
    """Launch the overlay or perform maintenance commands."""
    args = _parse_args(argv)
    if args.doctor:
        return _run_doctor()
    if args.toggle and _request_toggle():
        return 0
    return run()


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="floating-agent")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--toggle", action="store_true", help="Toggle the existing overlay or launch it.")
    mode.add_argument("--doctor", action="store_true", help="Check the local installation and runtime.")
    return parser.parse_args(list(argv) if argv is not None else None)


def _request_toggle() -> bool:
    socket = QLocalSocket()
    socket.connectToServer(_IPC_SERVER_NAME)
    if not socket.waitForConnected(100):
        return False
    socket.write(b"toggle\n")
    socket.flush()
    socket.waitForBytesWritten(100)
    socket.waitForReadyRead(100)
    socket.disconnectFromServer()
    socket.waitForDisconnected(100)
    return True


def _run_doctor() -> int:
    checks = _doctor_checks()
    for check in checks:
        print(f"DOCTOR|{check.status}|{check.name}|{check.detail}")
    passed = all(check.status != "FAIL" for check in checks)
    print("OVERALL_RESULT|PASS" if passed else "OVERALL_RESULT|FAIL")
    return 0 if passed else 1


def _doctor_checks() -> list[DoctorCheck]:
    assistant_settings = AssistantSettingsStore().load()
    checks = [
        DoctorCheck("python", _python_status(), sys.version.split()[0]),
        DoctorCheck("uv", "PASS" if which("uv") else "FAIL", which("uv") or "uv not found"),
        DoctorCheck("ollama", *_check_ollama(assistant_settings.ollama_base_url, assistant_settings.ollama_model)),
        DoctorCheck("pyside6", *_check_pyside6()),
    ]
    checks.append(DoctorCheck("tray", "INFO", _tray_detail()))
    return checks


def _python_status() -> str:
    return "PASS" if sys.version_info >= (3, 14) else "FAIL"


def _check_pyside6() -> tuple[str, str]:
    try:
        import PySide6  # noqa: F401
    except Exception as exc:  # pragma: no cover - import failure is environment specific
        return "FAIL", f"unavailable: {exc}"
    return "PASS", "available"


def _check_ollama(base_url: str, model: str) -> tuple[str, str]:
    try:
        response = httpx.get(f"{base_url.rstrip('/')}/api/tags", timeout=2.0)
        response.raise_for_status()
        models = response.json().get("models", [])
        available = any(item.get("name") == model for item in models if isinstance(item, dict))
        if available:
            return "PASS", f"{model} available at {base_url}"
        return "INFO", f"running at {base_url} but {model} not listed"
    except httpx.HTTPError as exc:
        return "FAIL", f"unavailable at {base_url}: {exc}"


def _tray_detail() -> str:
    try:
        if QApplication.instance() is None:
            QApplication([])
        from PySide6.QtWidgets import QSystemTrayIcon

        return "available" if QSystemTrayIcon.isSystemTrayAvailable() else "unavailable"
    except Exception as exc:  # pragma: no cover - GUI environment specific
        return f"unavailable: {exc}"
