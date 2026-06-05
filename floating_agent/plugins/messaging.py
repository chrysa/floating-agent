"""Gmail summary client (read).

Uses a bearer access token (GMAIL_ACCESS_TOKEN); OAuth2 refresh is a follow-up.
Network method is integration-only (pragma: no cover).
"""

from __future__ import annotations

_API = "https://gmail.googleapis.com/gmail/v1"


class GmailClient:
    """Reads a lightweight unread summary from the user's inbox."""

    def __init__(self, access_token: str, timeout: float = 30.0) -> None:
        self._access_token = access_token
        self._timeout = timeout

    def unread_count(self) -> int:  # pragma: no cover - needs live API
        import httpx

        resp = httpx.get(
            f"{_API}/users/me/labels/INBOX",
            headers={"Authorization": f"Bearer {self._access_token}"},
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return _parse_unread(resp.json())


def _parse_unread(raw: dict[str, object]) -> int:
    value = raw.get("messagesUnread", 0)
    return int(value) if isinstance(value, int | str) else 0
