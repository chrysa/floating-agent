from datetime import UTC, datetime

from pytestqt.qtbot import QtBot

from floating_agent.domain.outbox_item import OutboxItem
from floating_agent.domain.outbox_status import OutboxStatus
from floating_agent.overlay.widgets.outbox_widget import OutboxWidget
from floating_agent.ports.outbox import Outbox

NOW = datetime(2026, 7, 21, 12, tzinfo=UTC)


class _FakeOutbox(Outbox):
    def __init__(self, items: list[OutboxItem]) -> None:
        self._items = items

    def add(self, item: OutboxItem) -> OutboxItem:
        return item

    def get(self, item_id: str) -> OutboxItem | None:
        for item in self._items:
            if item.id == item_id:
                return item
        return None

    def save(self, item: OutboxItem) -> None:
        return None

    def list_by_status(self, statuses: set[OutboxStatus]) -> list[OutboxItem]:
        return [item for item in self._items if item.status in statuses]


def _item(status: OutboxStatus, *, last_error: str | None = None) -> OutboxItem:
    return OutboxItem(
        id=f"{status.value}-1",
        idempotency_key=f"{status.value}-key",
        provider="mail",
        account_id="demo-account",
        resource_type="message",
        resource_id="message-1",
        action_type="archive",
        payload={"source": "fixture"},
        status=status,
        created_at=NOW,
        updated_at=NOW,
        attempt_count=1,
        last_error=last_error,
        requires_confirmation=True,
        confirmed_at=NOW,
    )


def test_outbox_widget_renders_summary_and_details(qtbot: QtBot) -> None:
    widget = OutboxWidget(
        outbox=_FakeOutbox(
            [
                _item(OutboxStatus.QUEUED),
                _item(OutboxStatus.FAILED, last_error="temporary failure"),
                _item(OutboxStatus.SUCCEEDED),
            ]
        )
    )
    qtbot.addWidget(widget)

    assert "queued 1" in widget._summary.text()
    assert "failed 1" in widget._summary.text()
    assert "temporary failure" in widget._details.toPlainText()
