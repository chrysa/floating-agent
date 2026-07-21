"""SQLite implementation of durable Outbox persistence."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import TYPE_CHECKING, Any

from floating_agent.domain.outbox_item import OutboxItem
from floating_agent.domain.outbox_status import OutboxStatus

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from pathlib import Path

_SCHEMA_VERSION = 1
_INSERT_SQL = (
    "INSERT OR IGNORE INTO outbox (id, idempotency_key, provider, account_id, resource_type, resource_id, "
    "action_type, payload, status, created_at, updated_at, attempt_count, last_error, requires_confirmation, "
    "confirmed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
)
_SELECT_BY_KEY_SQL = "SELECT * FROM outbox WHERE idempotency_key = ?"
_SELECT_BY_ID_SQL = "SELECT * FROM outbox WHERE id = ?"
_SELECT_ALL_SQL = "SELECT * FROM outbox ORDER BY created_at, id"
_UPDATE_SQL = (
    "UPDATE outbox SET idempotency_key = ?, provider = ?, account_id = ?, resource_type = ?, resource_id = ?, "
    "action_type = ?, payload = ?, status = ?, created_at = ?, updated_at = ?, attempt_count = ?, last_error = ?, "
    "requires_confirmation = ?, confirmed_at = ? WHERE id = ?"
)


class SqliteOutbox:
    """Persist Outbox actions in a restart-safe local SQLite database."""

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self._migrate()

    def add(self, item: OutboxItem) -> OutboxItem:
        """Insert an item once, returning the prior item for a duplicate key."""
        with self._connect() as connection:
            connection.execute(
                _INSERT_SQL,
                self._to_values(item),
            )
            row = connection.execute(
                _SELECT_BY_KEY_SQL,
                (item.idempotency_key,),
            ).fetchone()
        if row is None:
            raise RuntimeError("Outbox insert did not return a persisted row")
        return self._from_row(row)

    def get(self, item_id: str) -> OutboxItem | None:
        """Return an item by identifier."""
        with self._connect() as connection:
            row = connection.execute(
                _SELECT_BY_ID_SQL,
                (item_id,),
            ).fetchone()
        return None if row is None else self._from_row(row)

    def save(self, item: OutboxItem) -> None:
        """Persist an existing item without changing its idempotency identity."""
        values = self._to_values(item)
        with self._connect() as connection:
            cursor = connection.execute(
                _UPDATE_SQL,
                (*values[1:], item.id),
            )
        if cursor.rowcount != 1:
            raise KeyError(item.id)

    def list_by_status(self, statuses: set[OutboxStatus]) -> Sequence[OutboxItem]:
        """Return items in deterministic creation order."""
        if not statuses:
            return []
        with self._connect() as connection:
            rows = connection.execute(_SELECT_ALL_SQL).fetchall()
        items = [self._from_row(row) for row in rows]
        return [item for item in items if item.status in statuses]

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path, timeout=5)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _migrate(self) -> None:
        with self._connect() as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version > _SCHEMA_VERSION:
                raise RuntimeError(f"Unsupported database schema version: {version}")
            connection.execute(
                """CREATE TABLE IF NOT EXISTS outbox (
                id TEXT PRIMARY KEY,
                idempotency_key TEXT NOT NULL UNIQUE,
                provider TEXT NOT NULL,
                account_id TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                action_type TEXT NOT NULL,
                payload TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                attempt_count INTEGER NOT NULL,
                last_error TEXT,
                requires_confirmation INTEGER NOT NULL,
                confirmed_at TEXT
                )"""
            )
            connection.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")

    @staticmethod
    def _to_values(item: OutboxItem) -> tuple[object, ...]:
        return (
            item.id,
            item.idempotency_key,
            item.provider,
            item.account_id,
            item.resource_type,
            item.resource_id,
            item.action_type,
            json.dumps(item.payload, ensure_ascii=False, sort_keys=True),
            item.status.value,
            item.created_at.isoformat(),
            item.updated_at.isoformat(),
            item.attempt_count,
            item.last_error,
            int(item.requires_confirmation),
            None if item.confirmed_at is None else item.confirmed_at.isoformat(),
        )

    @staticmethod
    def _from_row(row: Iterable[Any]) -> OutboxItem:
        values = tuple(row)
        payload = json.loads(values[7])
        if not isinstance(payload, dict):
            raise ValueError("Stored Outbox payload must be a JSON object")
        return OutboxItem(
            id=values[0],
            idempotency_key=values[1],
            provider=values[2],
            account_id=values[3],
            resource_type=values[4],
            resource_id=values[5],
            action_type=values[6],
            payload=payload,
            status=OutboxStatus(values[8]),
            created_at=datetime.fromisoformat(values[9]),
            updated_at=datetime.fromisoformat(values[10]),
            attempt_count=values[11],
            last_error=values[12],
            requires_confirmation=bool(values[13]),
            confirmed_at=None if values[14] is None else datetime.fromisoformat(values[14]),
        )
