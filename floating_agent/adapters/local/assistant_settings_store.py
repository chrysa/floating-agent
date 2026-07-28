"""Local YAML-backed persistence for assistant settings."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from floating_agent.domain.assistant_settings import AssistantSettings


def default_assistant_settings_path() -> Path:
    """Return the per-user assistant settings path."""
    config_home = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return config_home / "floating-agent" / "assistant.yaml"


class AssistantSettingsStore:
    """Load and save assistant settings without involving the UI."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path if path is not None else default_assistant_settings_path()

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> AssistantSettings:
        if not self._path.exists():
            return AssistantSettings()
        loaded = yaml.safe_load(self._path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            return AssistantSettings()
        payload: Any = loaded.get("assistant", loaded)
        if not isinstance(payload, dict):
            return AssistantSettings()
        return AssistantSettings.model_validate(payload)

    def save(self, settings: AssistantSettings) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"assistant": settings.model_dump(mode="python")}
        self._path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

