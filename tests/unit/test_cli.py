from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING

import floating_agent.cli as cli

if TYPE_CHECKING:
    import pytest


def test_main_toggles_when_instance_is_reachable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "_parse_args", lambda argv: SimpleNamespace(toggle=True, doctor=False))
    monkeypatch.setattr(cli, "_request_toggle", lambda: True)
    called = {"run": False}

    def _run() -> int:
        called["run"] = True
        return 7

    monkeypatch.setattr(cli, "run", _run)

    assert cli.main([]) == 0
    assert not called["run"]


def test_main_launches_when_toggle_target_is_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "_parse_args", lambda argv: SimpleNamespace(toggle=True, doctor=False))
    monkeypatch.setattr(cli, "_request_toggle", lambda: False)
    monkeypatch.setattr(cli, "run", lambda: 11)

    assert cli.main([]) == 11


def test_doctor_reports_failure_when_uv_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(cli, "which", lambda name: None)
    monkeypatch.setattr(cli, "_check_pyside6", lambda: ("PASS", "available"))
    monkeypatch.setattr(cli, "_tray_detail", lambda: "available")
    monkeypatch.setattr(cli, "_parse_args", lambda argv: SimpleNamespace(toggle=False, doctor=True))

    assert cli.main([]) == 1
    captured = capsys.readouterr().out
    assert "DOCTOR|FAIL|uv|uv not found" in captured
