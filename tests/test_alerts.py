"""Tests for alert thresholds config loader + engine + tool."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from httpx import ASGITransport, AsyncClient

from floating_agent.agent.tools import build_alerts_tool
from floating_agent.alerts import AlertEngine
from floating_agent.config import AlertThresholds, load_alert_thresholds
from floating_agent.models import SystemStats

if TYPE_CHECKING:
    from pathlib import Path

_QUIET = SystemStats(
    cpu_percent=10.0,
    ram_used_gb=4.0,
    ram_total_gb=16.0,
    ram_percent=25.0,
    disk_used_gb=100.0,
    disk_total_gb=500.0,
    disk_percent=20.0,
)
_HOT = _QUIET.model_copy(update={"cpu_percent": 95.0, "disk_percent": 99.0})


def _engine(**overrides: float) -> AlertEngine:
    base = {"cpu_percent": 90.0, "ram_percent": 90.0, "disk_percent": 90.0}
    return AlertEngine(AlertThresholds(**{**base, **overrides}))


def test_load_thresholds_from_yaml(tmp_path: Path) -> None:
    cfg = tmp_path / "alerts.yaml"
    cfg.write_text("thresholds:\n  cpu_percent: 70\n  ram_percent: 80\n  disk_percent: 85\n", encoding="utf-8")
    thresholds = load_alert_thresholds(cfg)
    assert thresholds.cpu_percent == 70.0
    assert thresholds.disk_percent == 85.0


def test_load_thresholds_from_default_config() -> None:
    thresholds = load_alert_thresholds()  # repo config/alerts.yaml
    assert thresholds.cpu_percent == 90.0


def test_engine_flags_only_breaching_metrics() -> None:
    alerts = _engine().evaluate(_HOT)
    metrics = {a.metric for a in alerts}
    assert metrics == {"cpu_percent", "disk_percent"}
    cpu = next(a for a in alerts if a.metric == "cpu_percent")
    assert cpu.value == 95.0
    assert cpu.threshold == 90.0


def test_engine_quiet_when_under_thresholds() -> None:
    assert _engine().evaluate(_QUIET) == []


def test_engine_from_config_builds_from_file() -> None:
    engine = AlertEngine.from_config()
    assert engine.evaluate(_QUIET) == []


def test_alerts_tool_reports_breaches() -> None:
    tool = build_alerts_tool(engine=_engine(), plugin=_StubSystem(_HOT))
    out = tool.run({})
    assert "cpu_percent" in out
    assert "disk_percent" in out


def test_alerts_tool_quiet() -> None:
    tool = build_alerts_tool(engine=_engine(), plugin=_StubSystem(_QUIET))
    assert "No active alerts" in tool.run({})


class _StubSystem:
    def __init__(self, stats: SystemStats) -> None:
        self._stats = stats

    def get_stats(self) -> SystemStats:
        return self._stats


@pytest.fixture
async def client() -> AsyncClient:
    from floating_agent.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


async def test_alerts_endpoint_returns_list(client: AsyncClient) -> None:
    response = await client.get("/alerts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
