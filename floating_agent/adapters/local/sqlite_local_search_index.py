"""SQLite-backed local search index."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import TYPE_CHECKING, Any

from floating_agent.domain.search_result import SearchResult

if TYPE_CHECKING:
    from pathlib import Path

_SEARCH_SQL = (
    "SELECT kind, resource_id, title, summary, source, fresh_at, cached FROM ("
    "SELECT 'mail' AS kind, message_id AS resource_id, subject AS title, sender || ' — ' || body_text AS summary, "
    "source, fresh_at, cached, account_id, recipients, cc, labels FROM mail_messages "
    "UNION ALL "
    "SELECT 'calendar' AS kind, event_id AS resource_id, title AS title, location || ' — ' || description AS summary, "
    "source, fresh_at, cached, account_id, participants, reminders, recurrence FROM calendar_events "
    "UNION ALL "
    "SELECT 'communication' AS kind, message_id AS resource_id, conversation AS title, author || ' — ' || content "
    "AS summary, "
    "source, fresh_at, cached, account_id, mentions, reactions, unread FROM communication_messages"
    ") WHERE lower(title || ' ' || summary) LIKE ? ORDER BY fresh_at DESC LIMIT ?"
)
_RECENT_SQL = (
    "SELECT kind, resource_id, title, summary, source, fresh_at, cached FROM ("
    "SELECT 'mail' AS kind, message_id AS resource_id, subject AS title, sender || ' — ' || body_text AS summary, "
    "source, fresh_at, cached FROM mail_messages "
    "UNION ALL "
    "SELECT 'calendar' AS kind, event_id AS resource_id, title AS title, location || ' — ' || description AS summary, "
    "source, fresh_at, cached FROM calendar_events "
    "UNION ALL "
    "SELECT 'communication' AS kind, message_id AS resource_id, conversation AS title, author || ' — ' || content "
    "AS summary, "
    "source, fresh_at, cached FROM communication_messages"
    ") ORDER BY fresh_at DESC LIMIT ?"
)


class SqliteLocalSearchIndex:
    """Search local cached content with deterministic SQLite queries."""

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path

    def search(self, query: str, *, limit: int = 10) -> list[SearchResult]:
        needle = query.strip().lower()
        with self._connect() as connection:
            if needle:
                rows = connection.execute(_SEARCH_SQL, (f"%{needle}%", limit)).fetchall()
            else:
                rows = connection.execute(_RECENT_SQL, (limit,)).fetchall()
        return [self._from_row(row) for row in rows]

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._database_path, timeout=5)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @staticmethod
    def _from_row(row: Any) -> SearchResult:
        values = tuple(row)
        return SearchResult(
            kind=values[0],
            resource_id=values[1],
            title=values[2],
            summary=values[3],
            source=values[4],
            fresh_at=datetime.fromisoformat(values[5]),
            cached=bool(values[6]),
        )
