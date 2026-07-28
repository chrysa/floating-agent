from datetime import UTC, datetime
from pathlib import Path

from floating_agent.adapters.local.eml_importer import import_eml
from floating_agent.adapters.local.ics_importer import import_ics
from floating_agent.adapters.local.json_importer import import_json
from floating_agent.adapters.local.sqlite_local_store import SqliteLocalStore

MAIL_FIXTURE = Path(__file__).parents[1] / "fixtures" / "mail" / "demo-message.eml"
CALENDAR_FIXTURE = Path(__file__).parents[1] / "fixtures" / "calendar" / "demo-event.ics"
COMMUNICATION_FIXTURE = Path(__file__).parents[1] / "fixtures" / "communications" / "demo-thread.json"
IMPORTED_AT = datetime(2026, 7, 21, 12, tzinfo=UTC)


def test_sqlite_local_store_survives_adapter_restart(tmp_path) -> None:
    database = tmp_path / "local-store.sqlite3"
    store = SqliteLocalStore(database)
    store.save_mail(import_eml(MAIL_FIXTURE, account_id="demo-account", imported_at=IMPORTED_AT))
    store.save_calendar_event(
        import_ics(
            CALENDAR_FIXTURE,
            account_id="demo-account",
            calendar_id="demo-calendar",
            imported_at=IMPORTED_AT,
        )[0]
    )
    store.save_communication(import_json(COMMUNICATION_FIXTURE, account_id="demo-account", imported_at=IMPORTED_AT)[0])

    restored = SqliteLocalStore(database)

    assert len(restored.list_mail()) == 1
    assert len(restored.list_calendar_events()) == 1
    assert len(restored.list_communications()) == 1
    assert restored.list_mail()[0].subject == "Debian beta fixture"
    assert restored.list_calendar_events()[0].title == "Debian beta planning"
    assert restored.list_communications()[0].conversation == "#release"


def test_sqlite_local_store_clear_removes_cached_content(tmp_path) -> None:
    store = SqliteLocalStore(tmp_path / "local-store.sqlite3")
    store.save_mail(import_eml(MAIL_FIXTURE, account_id="demo-account", imported_at=IMPORTED_AT))

    store.clear()

    assert store.list_mail() == []
