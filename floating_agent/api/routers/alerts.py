"""Alerts router — system metrics breaching configured thresholds."""

from fastapi import APIRouter

from floating_agent.alerts import Alert, AlertEngine
from floating_agent.plugins.system import SystemPlugin

router = APIRouter()
_engine = AlertEngine.from_config()
_plugin = SystemPlugin()


@router.get("", response_model=list[Alert])
async def alerts() -> list[Alert]:
    """Return the currently active alerts (empty list when all metrics are nominal)."""
    return _engine.evaluate(_plugin.get_stats())
