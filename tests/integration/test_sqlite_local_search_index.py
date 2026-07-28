from datetime import UTC, datetime
from pathlib import Path

from floating_agent.adapters.local.eml_importer import import_eml
from floating_agent.adapters.local.ics_importer import import_ics
from floating_agent.adapters.local.json_importer import import_json
from floating_agent.adapters.local.sqlite_local_search_index import SqliteLocalSearchIndex
from floating_agent.adapters.local.sqlite_local_store import SqliteLocalStore

MAIL_FIXTURE = Path(__file__).parents[1] / "fixtures" / "mail" / "demo-message.eml"
CALENDAR_FIXTURE = Path(__file__).parents[1] / "fixtures" / "calendar" / "demo-event.ics"
COMMUNICATION_FIXTURE = Path(__file__).parents[1] / "fixtures" / "communications" / "demo-thread.json"

MAIL_IMPORTED_AT = datetime(2026, 7, 21, 10, tzinfo=UTC)
CALENDAR_IMPORTED_AT = datetime(2026, 7, 21, 11, tzinfo=UTC)
COMM_IMPORTED_AT = datetime(2026, 7, 21, 12, tzinfo=UTC)


def test_sqlite_local_search_index_finds_recent_content(tmp_path: Path) -> None:
    database = tmp_path / "local-store.sqlite3"
    store = SqliteLocalStore(database)
    store.save_mail(import_eml(MAIL_FIXTURE, account_id="demo-account", imported_at=MAIL_IMPORTED_AT))
    store.save_calendar_event(
        import_ics(
            CALENDAR_FIXTURE,
            account_id="demo-account",
            calendar_id="demo-calendar",
            imported_at=CALENDAR_IMPORTED_AT,
        )[0]
    )
    store.save_communication(
        import_json(COMMUNICATION_FIXTURE, account_id="demo-account", imported_at=COMM_IMPORTED_AT)[0]
    )

    index = SqliteLocalSearchIndex(database)
    results = index.search("beta", limit=5)

    assert [result.kind for result in results] == ["communication", "calendar", "mail"]


def test_sqlite_local_search_index_returns_recent_hits_when_query_is_empty(tmp_path: Path) -> None:
    database = tmp_path / "local-store.sqlite3"
    store = SqliteLocalStore(database)
    store.save_mail(import_eml(MAIL_FIXTURE, account_id="demo-account", imported_at=MAIL_IMPORTED_AT))
    store.save_calendar_event(
        import_ics(
            CALENDAR_FIXTURE,
            account_id="demo-account",
            calendar_id="demo-calendar",
            imported_at=CALENDAR_IMPORTED_AT,
        )[0]
    )

    index = SqliteLocalSearchIndex(database)
    results = index.search("", limit=2)

    assert [result.kind for result in results] == ["calendar", "mail"]
