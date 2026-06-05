"""Tests for calendar + messaging tools and parsing (no live Google APIs)."""

from __future__ import annotations

from floating_agent.agent.tools import build_calendar_tool, build_messaging_tool
from floating_agent.plugins.calendar import CalendarEvent, _parse_event
from floating_agent.plugins.messaging import _parse_unread


class _FakeCalendar:
    def __init__(self, events: list[CalendarEvent]) -> None:
        self._events = events

    def upcoming(self, max_results: int = 5) -> list[CalendarEvent]:
        return self._events


class _FakeGmail:
    def unread_count(self) -> int:
        return 3


def test_parse_event_handles_datetime_and_date() -> None:
    dt = _parse_event({"summary": "Standup", "start": {"dateTime": "2026-06-05T09:00:00Z"}})
    assert dt == CalendarEvent(summary="Standup", start="2026-06-05T09:00:00Z")
    allday = _parse_event({"start": {"date": "2026-06-06"}})
    assert allday == CalendarEvent(summary="(no title)", start="2026-06-06")


def test_parse_unread_coerces() -> None:
    assert _parse_unread({"messagesUnread": 7}) == 7
    assert _parse_unread({"messagesUnread": "4"}) == 4
    assert _parse_unread({}) == 0


def test_calendar_tool_lists_events() -> None:
    tool = build_calendar_tool(_FakeCalendar([CalendarEvent("Lunch", "2026-06-05T12:00:00Z")]))
    out = tool.run({})
    assert "Lunch" in out
    assert "12:00" in out


def test_calendar_tool_empty() -> None:
    tool = build_calendar_tool(_FakeCalendar([]))
    assert "No upcoming events" in tool.run({})


def test_messaging_tool_reports_unread() -> None:
    tool = build_messaging_tool(_FakeGmail())
    assert "3 unread" in tool.run({})
