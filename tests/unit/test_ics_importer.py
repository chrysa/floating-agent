from datetime import UTC, datetime
from pathlib import Path

from floating_agent.adapters.local.ics_importer import import_ics

FIXTURE = Path(__file__).parents[1] / "fixtures" / "calendar" / "demo-event.ics"
IMPORTED_AT = datetime(2026, 7, 21, 12, tzinfo=UTC)


def test_import_ics_exposes_full_event_metadata() -> None:
    events = import_ics(FIXTURE, account_id="demo-account", calendar_id="demo-calendar", imported_at=IMPORTED_AT)

    assert len(events) == 1
    event = events[0]
    assert event.account_id == "demo-account"
    assert event.calendar_id == "demo-calendar"
    assert event.title == "Debian beta planning"
    assert event.location == "Dock 7"
    assert event.organizer == "Demo Organizer <organizer@example.test>"
    assert event.participants == ("Dev One <dev1@example.test>", "Dev Two <dev2@example.test>")
    assert event.response_status == "CONFIRMED"
    assert event.reminders == ("-PT15M",)
    assert event.recurrence == ("FREQ=WEEKLY;COUNT=4",)
    assert event.conflicts == ("demo-event-1", "demo-event-2")
    assert event.timezone == "Europe/Paris"
    assert event.source == "local-ics"
    assert event.cached is True


def test_import_ics_parses_timezone_aware_datetimes() -> None:
    event = import_ics(FIXTURE, account_id="demo-account", calendar_id="demo-calendar", imported_at=IMPORTED_AT)[0]

    assert event.start_at.tzinfo is not None
    assert event.end_at.tzinfo is not None
    assert event.fresh_at == IMPORTED_AT
