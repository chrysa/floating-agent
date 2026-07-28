from __future__ import annotations

from typing import TYPE_CHECKING

from floating_agent.adapters.local.assistant_settings_store import AssistantSettingsStore
from floating_agent.domain.assistant_settings import AssistantSettings

if TYPE_CHECKING:
    from pathlib import Path


def test_assistant_settings_store_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "assistant.yaml"
    store = AssistantSettingsStore(path)
    settings = AssistantSettings(
        provider="ollama",
        ollama_base_url="http://127.0.0.1:11434",
        ollama_model="llama3.2",
        ollama_keep_alive="10m",
        ollama_temperature=0.35,
    )

    store.save(settings)

    loaded = store.load()
    assert loaded == settings


def test_assistant_settings_store_defaults_when_missing(tmp_path: Path) -> None:
    store = AssistantSettingsStore(tmp_path / "missing.yaml")
    loaded = store.load()

    assert loaded.provider == "ollama"
    assert loaded.ollama_model == "llama3.2"
