"""Typed runtime configuration loaded from external YAML.

Per the chrysa "no hardcoded constants" standard, thresholds and other tunables
live in ``config/*.yaml`` and are read through this typed loader, never inlined.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel

_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


class AlertThresholds(BaseModel):
    cpu_percent: float
    ram_percent: float
    disk_percent: float


def _read_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"expected a top-level mapping in {path}")
    return loaded


def load_alert_thresholds(path: Path | None = None) -> AlertThresholds:
    resolved = path if path is not None else _CONFIG_DIR / "alerts.yaml"
    data = _read_yaml(resolved)
    return AlertThresholds.model_validate(data["thresholds"])
