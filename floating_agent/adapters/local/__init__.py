"""Offline local adapter implementations."""

from floating_agent.adapters.local.assistant_settings_store import AssistantSettingsStore
from floating_agent.adapters.local.connectivity_monitor import LocalConnectivityMonitor
from floating_agent.adapters.local.docker_cli_monitor import DockerCliMonitor
from floating_agent.adapters.local.eml_importer import import_eml, parse_eml_bytes
from floating_agent.adapters.local.ics_importer import import_ics, parse_ics_bytes
from floating_agent.adapters.local.json_importer import import_json, parse_json_bytes
from floating_agent.adapters.local.ollama_client import OllamaClient
from floating_agent.adapters.local.sqlite_local_search_index import SqliteLocalSearchIndex
from floating_agent.adapters.local.sqlite_local_store import SqliteLocalStore
from floating_agent.adapters.local.sqlite_outbox import SqliteOutbox

__all__ = [
    "AssistantSettingsStore",
    "LocalConnectivityMonitor",
    "DockerCliMonitor",
    "OllamaClient",
    "SqliteLocalSearchIndex",
    "SqliteLocalStore",
    "SqliteOutbox",
    "import_eml",
    "import_ics",
    "import_json",
    "parse_eml_bytes",
    "parse_ics_bytes",
    "parse_json_bytes",
]
