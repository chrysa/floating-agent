"""SQLite implementation of cached local content persistence."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import TYPE_CHECKING, Any

from floating_agent.domain.calendar_event import CalendarEvent
from floating_agent.domain.communication_message import CommunicationMessage
from floating_agent.domain.mail_attachment import MailAttachment
from floating_agent.domain.mail_message import MailMessage

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from pathlib import Path

_SCHEMA_VERSION = 1
_MAIL_UPSERT_SQL = (
    "INSERT OR REPLACE INTO mail_messages (account_id, message_id, sender, recipients, cc, sent_at, subject, "
    "labels, attachments, body_text, body_html, fresh_at, source, cached) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
)
_CALENDAR_UPSERT_SQL = (
    "INSERT OR REPLACE INTO calendar_events (account_id, calendar_id, event_id, title, start_at, end_at, timezone, "
    "location, description, organizer, participants, response_status, reminders, recurrence, conflicts, fresh_at, "
    "source, cached) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
)
_COMMUNICATION_UPSERT_SQL = (
    "INSERT OR REPLACE INTO communication_messages (account_id, message_id, workspace, conversation, author, "
    "thread_id, content, mentions, reactions, sent_at, fresh_at, source, cached, unread) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
)


class SqliteLocalStore:
    """Persist imported local mail, calendar, and communication content."""

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path
        database_path.parent.mkdir(parents=True, exist_ok=True)
        self._migrate()

    def save_mail(self, message: MailMessage) -> MailMessage:
        with self._connect() as connection:
            connection.execute(_MAIL_UPSERT_SQL, self._mail_values(message))
        return message

    def save_calendar_event(self, event: CalendarEvent) -> CalendarEvent:
        with self._connect() as connection:
            connection.execute(_CALENDAR_UPSERT_SQL, self._calendar_values(event))
        return event

    def save_communication(self, message: CommunicationMessage) -> CommunicationMessage:
        with self._connect() as connection:
            connection.execute(_COMMUNICATION_UPSERT_SQL, self._communication_values(message))
        return message

    def list_mail(self, account_id: str | None = None) -> Sequence[MailMessage]:
        return self._list(
            "SELECT * FROM mail_messages",
            self._mail_from_row,
            account_id,
        )

    def list_calendar_events(self, account_id: str | None = None) -> Sequence[CalendarEvent]:
        return self._list(
            "SELECT * FROM calendar_events",
            self._calendar_from_row,
            account_id,
        )

    def list_communications(self, account_id: str | None = None) -> Sequence[CommunicationMessage]:
        return self._list(
            "SELECT * FROM communication_messages",
            self._communication_from_row,
            account_id,
        )

    def clear(self) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM mail_messages")
            connection.execute("DELETE FROM calendar_events")
            connection.execute("DELETE FROM communication_messages")

    def _list(self, query: str, decoder: Any, account_id: str | None) -> list[Any]:
        sql = query
        params: tuple[object, ...] = ()
        if account_id is not None:
            sql += " WHERE account_id = ?"
            params = (account_id,)
        sql += " ORDER BY fresh_at DESC, account_id DESC"
        with self._connect() as connection:
            rows = connection.execute(sql, params).fetchall()
        return [decoder(row) for row in rows]

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
                """CREATE TABLE IF NOT EXISTS mail_messages (
                account_id TEXT NOT NULL,
                message_id TEXT NOT NULL,
                sender TEXT NOT NULL,
                recipients TEXT NOT NULL,
                cc TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                subject TEXT NOT NULL,
                labels TEXT NOT NULL,
                attachments TEXT NOT NULL,
                body_text TEXT NOT NULL,
                body_html TEXT,
                fresh_at TEXT NOT NULL,
                source TEXT NOT NULL,
                cached INTEGER NOT NULL,
                PRIMARY KEY (account_id, message_id)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS calendar_events (
                account_id TEXT NOT NULL,
                calendar_id TEXT NOT NULL,
                event_id TEXT NOT NULL,
                title TEXT NOT NULL,
                start_at TEXT NOT NULL,
                end_at TEXT NOT NULL,
                timezone TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT NOT NULL,
                organizer TEXT NOT NULL,
                participants TEXT NOT NULL,
                response_status TEXT NOT NULL,
                reminders TEXT NOT NULL,
                recurrence TEXT NOT NULL,
                conflicts TEXT NOT NULL,
                fresh_at TEXT NOT NULL,
                source TEXT NOT NULL,
                cached INTEGER NOT NULL,
                PRIMARY KEY (account_id, calendar_id, event_id)
                )"""
            )
            connection.execute(
                """CREATE TABLE IF NOT EXISTS communication_messages (
                account_id TEXT NOT NULL,
                message_id TEXT NOT NULL,
                workspace TEXT NOT NULL,
                conversation TEXT NOT NULL,
                author TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                content TEXT NOT NULL,
                mentions TEXT NOT NULL,
                reactions TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                fresh_at TEXT NOT NULL,
                source TEXT NOT NULL,
                cached INTEGER NOT NULL,
                unread INTEGER NOT NULL,
                PRIMARY KEY (account_id, message_id)
                )"""
            )
            connection.execute(f"PRAGMA user_version = {_SCHEMA_VERSION}")

    @staticmethod
    def _mail_values(message: MailMessage) -> tuple[object, ...]:
        return (
            message.account_id,
            message.message_id,
            message.sender,
            json.dumps(message.recipients, ensure_ascii=False),
            json.dumps(message.cc, ensure_ascii=False),
            message.sent_at.isoformat(),
            message.subject,
            json.dumps(message.labels, ensure_ascii=False),
            json.dumps([_attachment_to_dict(item) for item in message.attachments], ensure_ascii=False),
            message.body_text,
            message.body_html,
            message.fresh_at.isoformat(),
            message.source,
            int(message.cached),
        )

    @staticmethod
    def _calendar_values(event: CalendarEvent) -> tuple[object, ...]:
        return (
            event.account_id,
            event.calendar_id,
            event.event_id,
            event.title,
            event.start_at.isoformat(),
            event.end_at.isoformat(),
            event.timezone,
            event.location,
            event.description,
            event.organizer,
            json.dumps(event.participants, ensure_ascii=False),
            event.response_status,
            json.dumps(event.reminders, ensure_ascii=False),
            json.dumps(event.recurrence, ensure_ascii=False),
            json.dumps(event.conflicts, ensure_ascii=False),
            event.fresh_at.isoformat(),
            event.source,
            int(event.cached),
        )

    @staticmethod
    def _communication_values(message: CommunicationMessage) -> tuple[object, ...]:
        return (
            message.account_id,
            message.message_id,
            message.workspace,
            message.conversation,
            message.author,
            message.thread_id,
            message.content,
            json.dumps(message.mentions, ensure_ascii=False),
            json.dumps(message.reactions, ensure_ascii=False),
            message.sent_at.isoformat(),
            message.fresh_at.isoformat(),
            message.source,
            int(message.cached),
            int(message.unread),
        )

    @staticmethod
    def _mail_from_row(row: Iterable[Any]) -> MailMessage:
        values = tuple(row)
        return MailMessage(
            message_id=values[1],
            account_id=values[0],
            sender=values[2],
            recipients=tuple(json.loads(values[3])),
            cc=tuple(json.loads(values[4])),
            sent_at=datetime.fromisoformat(values[5]),
            subject=values[6],
            labels=tuple(json.loads(values[7])),
            attachments=tuple(MailAttachment(**item) for item in json.loads(values[8])),
            body_text=values[9],
            body_html=values[10],
            fresh_at=datetime.fromisoformat(values[11]),
            source=values[12],
            cached=bool(values[13]),
        )

    @staticmethod
    def _calendar_from_row(row: Iterable[Any]) -> CalendarEvent:
        values = tuple(row)
        return CalendarEvent(
            account_id=values[0],
            calendar_id=values[1],
            event_id=values[2],
            title=values[3],
            start_at=datetime.fromisoformat(values[4]),
            end_at=datetime.fromisoformat(values[5]),
            timezone=values[6],
            location=values[7],
            description=values[8],
            organizer=values[9],
            participants=tuple(json.loads(values[10])),
            response_status=values[11],
            reminders=tuple(json.loads(values[12])),
            recurrence=tuple(json.loads(values[13])),
            conflicts=tuple(json.loads(values[14])),
            fresh_at=datetime.fromisoformat(values[15]),
            source=values[16],
            cached=bool(values[17]),
        )

    @staticmethod
    def _communication_from_row(row: Iterable[Any]) -> CommunicationMessage:
        values = tuple(row)
        return CommunicationMessage(
            account_id=values[0],
            message_id=values[1],
            workspace=values[2],
            conversation=values[3],
            author=values[4],
            thread_id=values[5],
            content=values[6],
            mentions=tuple(json.loads(values[7])),
            reactions=tuple(json.loads(values[8])),
            sent_at=datetime.fromisoformat(values[9]),
            fresh_at=datetime.fromisoformat(values[10]),
            source=values[11],
            cached=bool(values[12]),
            unread=bool(values[13]),
        )


def _attachment_to_dict(item: MailAttachment) -> dict[str, object]:
    return {
        "filename": item.filename,
        "content_type": item.content_type,
        "size_bytes": item.size_bytes,
    }
