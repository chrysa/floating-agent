"""Google Calendar client (read).

Uses a bearer access token (CALENDAR_ACCESS_TOKEN); the full OAuth2 flow with
refresh is a follow-up. Network method is integration-only (pragma: no cover).
"""

from __future__ import annotations

from dataclasses import dataclass

_API = "https://www.googleapis.com/calendar/v3"


@dataclass(frozen=True)
class CalendarEvent:
    """A minimal upcoming-event view."""

    summary: str
    start: str


class CalendarClient:
    """Reads upcoming events from the user's primary calendar."""

    def __init__(self, access_token: str, timeout: float = 30.0) -> None:
        self._access_token = access_token
        self._timeout = timeout

    def upcoming(self, max_results: int = 5) -> list[CalendarEvent]:  # pragma: no cover - needs live API
        import httpx

        resp = httpx.get(
            f"{_API}/calendars/primary/events",
            headers={"Authorization": f"Bearer {self._access_token}"},
            params={"maxResults": max_results, "orderBy": "startTime", "singleEvents": "true"},
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return [_parse_event(item) for item in resp.json().get("items", [])]


def _parse_event(raw: dict[str, object]) -> CalendarEvent:
    summary = str(raw.get("summary", "(no title)"))
    start_obj = raw.get("start")
    start = ""
    if isinstance(start_obj, dict):
        start = str(start_obj.get("dateTime") or start_obj.get("date") or "")
    return CalendarEvent(summary=summary, start=start)
