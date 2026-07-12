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


class NetworkStats(BaseModel):
    sent_mb_s: float
    recv_mb_s: float
    bytes_sent: int
    bytes_recv: int
    connections: int


class ProcessInfo(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    ram_mb: float
