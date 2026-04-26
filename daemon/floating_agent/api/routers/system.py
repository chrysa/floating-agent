"""System monitoring router — CPU, RAM, disk."""

from fastapi import APIRouter

from floating_agent.models import SystemStats
from floating_agent.plugins.system import SystemPlugin

router = APIRouter()
_plugin = SystemPlugin()


@router.get("", response_model=SystemStats)
async def system_stats() -> SystemStats:
    """Return current system resource usage."""
    return _plugin.get_stats()
