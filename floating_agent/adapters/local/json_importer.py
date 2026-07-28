"""Local JSON import adapter for communications."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from floating_agent.domain.communication_message import CommunicationMessage

if TYPE_CHECKING:
    from pathlib import Path

_LOCAL_JSON_SOURCE = "local-json"


def import_json(path: Path, *, account_id: str, imported_at: datetime) -> tuple[CommunicationMessage, ...]:
    """Read a local JSON file into provider-agnostic communication messages."""
    return parse_json_bytes(path.read_bytes(), account_id=account_id, imported_at=imported_at)


def parse_json_bytes(content: bytes, *, account_id: str, imported_at: datetime) -> tuple[CommunicationMessage, ...]:
    """Parse a demo communications export without contacting a remote provider."""
    if imported_at.tzinfo is None:
        raise ValueError("imported_at must be timezone-aware")
    raw = json.loads(content.decode("utf-8"))
    payload = raw if isinstance(raw, dict) else {"messages": raw}
    workspace = str(payload.get("workspace", "local-workspace"))
    conversation = str(payload.get("conversation", "local-conversation"))
    messages = payload.get("messages", [])
    if not isinstance(messages, list):
        raise ValueError("messages must be a JSON array")
    return tuple(
        _parse_message(
            message,
            account_id=account_id,
            workspace=workspace,
            conversation=conversation,
            imported_at=imported_at,
        )
        for message in messages
    )


def _parse_message(
    raw: dict[str, Any],
    *,
    account_id: str,
    workspace: str,
    conversation: str,
    imported_at: datetime,
) -> CommunicationMessage:
    if not isinstance(raw, dict):
        raise ValueError("message entries must be JSON objects")
    sent_at = _parse_datetime(raw.get("sent_at"))
    mentions = _as_strings(raw.get("mentions", []))
    reactions = _as_strings(raw.get("reactions", []))
    return CommunicationMessage(
        message_id=str(raw.get("id", "")),
        account_id=account_id,
        workspace=workspace,
        conversation=str(raw.get("conversation", conversation)),
        author=str(raw.get("author", "")),
        thread_id=str(raw.get("thread_id", raw.get("id", ""))),
        content=str(raw.get("content", "")),
        mentions=mentions,
        reactions=reactions,
        sent_at=sent_at,
        fresh_at=imported_at,
        source=_LOCAL_JSON_SOURCE,
        cached=True,
        unread=bool(raw.get("unread", False)),
    )


def _parse_datetime(raw: object) -> datetime:
    if not isinstance(raw, str) or not raw:
        raise ValueError("sent_at must be an ISO 8601 string")
    value = raw.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


def _as_strings(raw: object) -> tuple[str, ...]:
    if not isinstance(raw, list):
        return ()
    return tuple(str(item) for item in raw if str(item))
