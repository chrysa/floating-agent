from datetime import UTC, datetime
from pathlib import Path

from floating_agent.adapters.local.json_importer import import_json

FIXTURE = Path(__file__).parents[1] / "fixtures" / "communications" / "demo-thread.json"
IMPORTED_AT = datetime(2026, 7, 21, 12, tzinfo=UTC)


def test_import_json_exposes_workspace_thread_and_metadata() -> None:
    messages = import_json(FIXTURE, account_id="demo-account", imported_at=IMPORTED_AT)

    assert len(messages) == 1
    message = messages[0]
    assert message.account_id == "demo-account"
    assert message.workspace == "demo-workspace"
    assert message.conversation == "#release"
    assert message.author == "Demo User"
    assert message.thread_id == "thread-1"
    assert message.mentions == ("@release", "@qa")
    assert message.reactions == ("thumbs_up",)
    assert message.unread is True
    assert message.source == "local-json"
    assert message.cached is True


def test_import_json_parses_timezone_aware_sent_at() -> None:
    message = import_json(FIXTURE, account_id="demo-account", imported_at=IMPORTED_AT)[0]

    assert message.sent_at.tzinfo is not None
    assert message.fresh_at == IMPORTED_AT
