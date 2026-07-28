"""Compact configuration panel for the local Ollama assistant."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from floating_agent.domain.assistant_settings import AssistantSettings

if TYPE_CHECKING:
    from collections.abc import Callable

    from floating_agent.adapters.local.assistant_settings_store import AssistantSettingsStore


class AssistantConfigWidget(QWidget):
    """Allow editing the default Ollama endpoint and model from the overlay."""

    def __init__(
        self,
        store: AssistantSettingsStore,
        on_saved: Callable[[AssistantSettings], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._store = store
        self._on_saved = on_saved
        self._settings = self._store.load()

        self._title = QLabel("Assistant configuration")
        self._status = QLabel()
        self._provider = QLineEdit()
        self._provider.setReadOnly(True)
        self._base_url = QLineEdit()
        self._model = QLineEdit()
        self._keep_alive = QLineEdit()
        self._temperature = QDoubleSpinBox()
        self._temperature.setDecimals(2)
        self._temperature.setSingleStep(0.05)
        self._temperature.setRange(0.0, 2.0)
        self._refresh = QPushButton("Reload")
        self._save = QPushButton("Save")

        form = QFormLayout()
        form.addRow("Provider", self._provider)
        form.addRow("Ollama URL", self._base_url)
        form.addRow("Model", self._model)
        form.addRow("Keep alive", self._keep_alive)
        form.addRow("Temperature", self._temperature)

        buttons = QHBoxLayout()
        buttons.addWidget(self._refresh)
        buttons.addWidget(self._save)

        layout = QVBoxLayout(self)
        layout.addWidget(self._title)
        layout.addWidget(self._status)
        layout.addLayout(form)
        layout.addLayout(buttons)

        self._refresh.clicked.connect(self.reload)
        self._save.clicked.connect(self.save)
        self.reload()

    def reload(self) -> None:
        """Load the current settings from disk into the form."""
        self._settings = self._store.load()
        self._provider.setText(self._settings.provider)
        self._base_url.setText(self._settings.ollama_base_url)
        self._model.setText(self._settings.ollama_model)
        self._keep_alive.setText(self._settings.ollama_keep_alive)
        self._temperature.setValue(self._settings.ollama_temperature)
        self._status.setText(self._summary())

    def save(self) -> None:
        """Persist the form and notify the overlay that the client changed."""
        settings = AssistantSettings(
            provider=self._provider.text().strip() or "ollama",
            ollama_base_url=self._base_url.text().strip() or "http://127.0.0.1:11434",
            ollama_model=self._model.text().strip() or "llama3.2",
            ollama_keep_alive=self._keep_alive.text().strip() or "5m",
            ollama_temperature=self._temperature.value(),
        )
        self._store.save(settings)
        self._settings = settings
        self._status.setText(self._summary())
        self._on_saved(settings)

    def _summary(self) -> str:
        return f"{self._settings.provider} · {self._settings.ollama_model} @ {self._settings.ollama_base_url}"

