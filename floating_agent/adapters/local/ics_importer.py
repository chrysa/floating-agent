"""Local ICS import adapter."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

from floating_agent.domain.calendar_event import CalendarEvent

if TYPE_CHECKING:
    from pathlib import Path

_LOCAL_ICS_SOURCE = "local-ics"


@dataclass(frozen=True, slots=True)
class _Property:
    name: str
    params: dict[str, str]
    value: str


def import_ics(path: Path, *, account_id: str, calendar_id: str, imported_at: datetime) -> tuple[CalendarEvent, ...]:
    """Read a local ICS file into provider-agnostic calendar events."""
    return parse_ics_bytes(path.read_bytes(), account_id=account_id, calendar_id=calendar_id, imported_at=imported_at)


def parse_ics_bytes(
    content: bytes,
    *,
    account_id: str,
    calendar_id: str,
    imported_at: datetime,
) -> tuple[CalendarEvent, ...]:
    """Parse a minimal RFC 5545 payload without contacting a remote provider."""
    if imported_at.tzinfo is None:
        raise ValueError("imported_at must be timezone-aware")
    events = []
    current: list[_Property] | None = None
    alarms: list[str] = []
    in_alarm = False

    for raw_line in _unfold(content.decode("utf-8")).splitlines():
        line = raw_line.strip()
        if line == "BEGIN:VEVENT":
            current = []
            alarms = []
            in_alarm = False
            continue
        if line == "END:VEVENT":
            if current is None:
                continue
            events.append(
                _build_event(current, alarms, account_id=account_id, calendar_id=calendar_id, imported_at=imported_at)
            )
            current = None
            continue
        if current is None:
            continue
        if line == "BEGIN:VALARM":
            in_alarm = True
            continue
        if line == "END:VALARM":
            in_alarm = False
            continue
        if in_alarm:
            prop = _parse_property(line)
            if prop.name == "TRIGGER":
                alarms.append(prop.value)
            continue
        prop = _parse_property(line)
        current.append(prop)

    return tuple(events)


def _build_event(
    properties: list[_Property],
    reminders: list[str],
    *,
    account_id: str,
    calendar_id: str,
    imported_at: datetime,
) -> CalendarEvent:
    lookup = _property_map(properties)
    start_at, timezone = _parse_datetime(lookup.get("DTSTART"))
    end_at, _ = _parse_datetime(lookup.get("DTEND"))
    return CalendarEvent(
        event_id=_single(lookup.get("UID"), default=""),
        account_id=account_id,
        calendar_id=calendar_id,
        title=_text(_single(lookup.get("SUMMARY"))),
        start_at=start_at,
        end_at=end_at,
        timezone=timezone,
        location=_text(_single(lookup.get("LOCATION"))),
        description=_text(_single(lookup.get("DESCRIPTION"))),
        organizer=_organizer(lookup.get("ORGANIZER")),
        participants=_participants(lookup.get_all("ATTENDEE")),
        response_status=_single(lookup.get("STATUS"), default="needsAction"),
        reminders=tuple(reminders),
        recurrence=tuple(_text(rule.value) for rule in lookup.get_all("RRULE")),
        conflicts=_conflicts(lookup),
        fresh_at=imported_at,
        source=_LOCAL_ICS_SOURCE,
        cached=True,
    )


def _unfold(content: str) -> str:
    lines = content.splitlines()
    unfolded: list[str] = []
    for line in lines:
        if line.startswith((" ", "\t")) and unfolded:
            unfolded[-1] += line[1:]
        else:
            unfolded.append(line)
    return "\n".join(unfolded)


def _parse_property(line: str) -> _Property:
    left, value = line.split(":", 1)
    parts = left.split(";")
    name = parts[0].upper()
    params: dict[str, str] = {}
    for part in parts[1:]:
        key, _, raw = part.partition("=")
        params[key.upper()] = raw
    return _Property(name=name, params=params, value=_text(value))


def _property_map(properties: list[_Property]) -> _PropertyLookup:
    lookup = _PropertyLookup()
    for prop in properties:
        lookup.add(prop)
    return lookup


class _PropertyLookup:
    def __init__(self) -> None:
        self._values: dict[str, list[_Property]] = {}

    def add(self, prop: _Property) -> None:
        self._values.setdefault(prop.name, []).append(prop)

    def get(self, name: str) -> _Property | None:
        items = self._values.get(name, [])
        return items[0] if items else None

    def get_all(self, name: str) -> list[_Property]:
        return list(self._values.get(name, []))


def _single(prop: _Property | None, *, default: str = "") -> str:
    return default if prop is None else prop.value


def _parse_datetime(prop: _Property | None) -> tuple[datetime, str]:
    if prop is None:
        raise ValueError("ICS event is missing a datetime property")
    raw = prop.value
    tzid = prop.params.get("TZID")
    if raw.endswith("Z"):
        return datetime.strptime(raw, "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC), "UTC"
    if len(raw) == 8:
        return datetime.strptime(raw, "%Y%m%d").replace(tzinfo=UTC), "UTC"
    zone = ZoneInfo(tzid) if tzid is not None else UTC
    return datetime.strptime(raw, "%Y%m%dT%H%M%S").replace(tzinfo=zone), tzid or "UTC"


def _text(value: str) -> str:
    return (
        value.replace("\\n", "\n")
        .replace("\\N", "\n")
        .replace("\\,", ",")
        .replace("\\;", ";")
        .replace("\\\\", "\\")
    )


def _organizer(prop: _Property | None) -> str:
    if prop is None:
        return ""
    address = prop.value.removeprefix("mailto:")
    name = prop.params.get("CN")
    return f"{name} <{address}>" if name is not None else address


def _participants(values: list[_Property]) -> tuple[str, ...]:
    items: list[str] = []
    for value in values:
        address = value.value.removeprefix("mailto:")
        name = value.params.get("CN")
        items.append(f"{name} <{address}>" if name is not None else address)
    return tuple(items)


def _conflicts(lookup: _PropertyLookup) -> tuple[str, ...]:
    values = lookup.get("X-CONFLICTS") or lookup.get("CONFLICTS")
    if values is None:
        return ()
    return tuple(item.strip() for item in values.value.split(",") if item.strip())
