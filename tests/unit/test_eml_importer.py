from datetime import UTC, datetime
from pathlib import Path

from floating_agent.adapters.local.eml_importer import import_eml

FIXTURE = Path(__file__).parents[1] / "fixtures" / "mail" / "demo-message.eml"
IMPORTED_AT = datetime(2026, 7, 21, 12, tzinfo=UTC)


def test_import_eml_exposes_readable_content_and_metadata() -> None:
    message = import_eml(FIXTURE, account_id="demo-account", imported_at=IMPORTED_AT)

    assert message.account_id == "demo-account"
    assert message.sender == "Demo Sender <sender@example.test>"
    assert message.recipients == ("recipient@example.test",)
    assert message.cc == ("team@example.test",)
    assert message.subject == "Debian beta fixture"
    assert message.labels == ("inbox", "follow-up")
    assert "offline Debian beta checklist" in message.body_text
    assert message.source == "local-eml"
    assert message.cached is True


def test_import_eml_lists_attachment_without_exposing_content() -> None:
    message = import_eml(FIXTURE, account_id="demo-account", imported_at=IMPORTED_AT)

    assert len(message.attachments) == 1
    assert message.attachments[0].filename == "checklist.txt"
    assert message.attachments[0].content_type == "text/plain"
    assert message.attachments[0].size_bytes > 0
