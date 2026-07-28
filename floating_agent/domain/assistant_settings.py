"""Assistant runtime settings persisted locally for the desktop overlay."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AssistantSettings(BaseModel):
    """Local settings that control the default model and its endpoint."""

    provider: str = Field(default="ollama")
    ollama_base_url: str = Field(default="http://127.0.0.1:11434")
    ollama_model: str = Field(default="llama3.2")
    ollama_keep_alive: str = Field(default="5m")
    ollama_temperature: float = Field(default=0.2, ge=0.0, le=2.0)

