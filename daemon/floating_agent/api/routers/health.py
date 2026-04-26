"""Health check router."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str


@router.get("", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return daemon health status."""
    from floating_agent.main import DAEMON_VERSION

    return HealthResponse(status="ok", version=DAEMON_VERSION)
