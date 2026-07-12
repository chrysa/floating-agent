"""Alert engine — evaluates system metrics against configured thresholds."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

from floating_agent.config import AlertThresholds, load_alert_thresholds

if TYPE_CHECKING:
    from pathlib import Path

    from floating_agent.models import SystemStats


class Alert(BaseModel):
    metric: str
    value: float
    threshold: float


class AlertEngine:
    """Flags metrics that reach or exceed their threshold."""

    def __init__(self, thresholds: AlertThresholds) -> None:
        self._thresholds = thresholds

    @classmethod
    def from_config(cls, path: Path | None = None) -> AlertEngine:
        return cls(load_alert_thresholds(path))

    def evaluate(self, stats: SystemStats) -> list[Alert]:
        pairs = (
            ("cpu_percent", stats.cpu_percent, self._thresholds.cpu_percent),
            ("ram_percent", stats.ram_percent, self._thresholds.ram_percent),
            ("disk_percent", stats.disk_percent, self._thresholds.disk_percent),
        )
        return [
            Alert(metric=metric, value=value, threshold=threshold)
            for metric, value, threshold in pairs
            if value >= threshold
        ]
