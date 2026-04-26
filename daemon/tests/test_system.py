"""Tests for system monitoring endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from floating_agent.main import app


@pytest.fixture
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


async def test_system_stats_shape(client: AsyncClient) -> None:
    response = await client.get("/system")
    assert response.status_code == 200
    data = response.json()
    assert "cpu_percent" in data
    assert "ram_used_gb" in data
    assert "ram_total_gb" in data
    assert "ram_percent" in data
    assert "disk_used_gb" in data
    assert "disk_total_gb" in data
    assert "disk_percent" in data


async def test_system_cpu_in_range(client: AsyncClient) -> None:
    response = await client.get("/system")
    data = response.json()
    assert 0.0 <= data["cpu_percent"] <= 100.0
    assert 0.0 <= data["ram_percent"] <= 100.0
    assert 0.0 <= data["disk_percent"] <= 100.0
