"""Mail attachment metadata available from a local message."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MailAttachment:
    """Describe an attachment without forcing its content into memory."""

    filename: str
    content_type: str
    size_bytes: int
