"""Local RFC 5322 EML import adapter."""

from __future__ import annotations

from datetime import UTC, datetime
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses, parsedate_to_datetime
from typing import TYPE_CHECKING

from floating_agent.domain.mail_attachment import MailAttachment
from floating_agent.domain.mail_message import MailMessage

if TYPE_CHECKING:
    from email.message import EmailMessage
    from pathlib import Path

_LOCAL_EML_SOURCE = "local-eml"


def import_eml(path: Path, *, account_id: str, imported_at: datetime) -> MailMessage:
    """Read one local EML file into the provider-agnostic mail model."""
    return parse_eml_bytes(path.read_bytes(), account_id=account_id, imported_at=imported_at)


def parse_eml_bytes(content: bytes, *, account_id: str, imported_at: datetime) -> MailMessage:
    """Parse RFC 5322 bytes without contacting a remote provider."""
    if imported_at.tzinfo is None:
        raise ValueError("imported_at must be timezone-aware")
    message = BytesParser(policy=policy.default).parsebytes(content)
    sent_at = _sent_at(message)
    body_text, body_html = _bodies(message)
    return MailMessage(
        message_id=str(message.get("Message-ID", "")).strip("<> "),
        account_id=account_id,
        sender=str(message.get("From", "")),
        recipients=_addresses(message.get_all("To", [])),
        cc=_addresses(message.get_all("Cc", [])),
        sent_at=sent_at,
        subject=str(message.get("Subject", "")),
        labels=_labels(str(message.get("X-Labels", ""))),
        attachments=_attachments(message),
        body_text=body_text,
        body_html=body_html,
        fresh_at=imported_at,
        source=_LOCAL_EML_SOURCE,
        cached=True,
    )


def _sent_at(message: EmailMessage) -> datetime:
    raw_date = message.get("Date")
    if raw_date is None:
        raise ValueError("EML message is missing a Date header")
    value = parsedate_to_datetime(str(raw_date))
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def _addresses(headers: list[str]) -> tuple[str, ...]:
    return tuple(address for _name, address in getaddresses(headers) if address)


def _labels(raw_labels: str) -> tuple[str, ...]:
    return tuple(label.strip() for label in raw_labels.split(",") if label.strip())


def _bodies(message: EmailMessage) -> tuple[str, str | None]:
    text_part = message.get_body(preferencelist=("plain",))
    html_part = message.get_body(preferencelist=("html",))
    text = "" if text_part is None else text_part.get_content()
    html = None if html_part is None else html_part.get_content()
    return str(text), None if html is None else str(html)


def _attachments(message: EmailMessage) -> tuple[MailAttachment, ...]:
    attachments = []
    for part in message.iter_attachments():
        payload = part.get_payload(decode=True) or b""
        attachments.append(
            MailAttachment(
                filename=part.get_filename() or "attachment",
                content_type=part.get_content_type(),
                size_bytes=len(payload),
            )
        )
    return tuple(attachments)
