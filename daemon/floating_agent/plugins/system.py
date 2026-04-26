"""System monitoring plugin using psutil."""

import psutil

from floating_agent.models import SystemStats


class SystemPlugin:
    """Collects CPU, RAM and disk metrics from the local machine."""

    def get_stats(self) -> SystemStats:
        cpu = psutil.cpu_percent(interval=0.1)

        mem = psutil.virtual_memory()
        ram_used_gb = mem.used / 1024**3
        ram_total_gb = mem.total / 1024**3

        disk = psutil.disk_usage("/")
        disk_used_gb = disk.used / 1024**3
        disk_total_gb = disk.total / 1024**3

        return SystemStats(
            cpu_percent=round(cpu, 1),
            ram_used_gb=round(ram_used_gb, 2),
            ram_total_gb=round(ram_total_gb, 2),
            ram_percent=round(mem.percent, 1),
            disk_used_gb=round(disk_used_gb, 2),
            disk_total_gb=round(disk_total_gb, 2),
            disk_percent=round(disk.percent, 1),
        )
