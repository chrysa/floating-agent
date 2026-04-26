"""Pydantic schemas for the daemon API."""

from pydantic import BaseModel


class SystemStats(BaseModel):
    cpu_percent: float
    ram_used_gb: float
    ram_total_gb: float
    ram_percent: float
    disk_used_gb: float
    disk_total_gb: float
    disk_percent: float
