from datetime import UTC, datetime

from floating_agent.domain.calendar_event import CalendarEvent
from floating_agent.domain.communication_message import CommunicationMessage
from floating_agent.domain.mail_attachment import MailAttachment
from floating_agent.domain.mail_message import MailMessage
from floating_agent.overlay.widgets.attention_widget import AttentionWidget


class _FakeStore:
    def __init__(
        self,
        mails: list[MailMessage],
        calendar_events: list[CalendarEvent],
        communications: list[CommunicationMessage],
    ) -> None:
        self._mails = mails
        self._calendar_events = calendar_events
        self._communications = communications

    def list_mail(self, account_id: str | None = None) -> list[MailMessage]:
        return self._mails

    def list_calendar_events(self, account_id: str | None = None) -> list[CalendarEvent]:
        return self._calendar_events

    def list_communications(self, account_id: str | None = None) -> list[CommunicationMessage]:
        return self._communications


def test_attention_widget_renders_local_summary(qtbot) -> None:
    store = _FakeStore(
        mails=[
            MailMessage(
                message_id="msg-1",
                account_id="demo-account",
                sender="Demo Sender <sender@example.test>",
                recipients=("recipient@example.test",),
                cc=(),
                sent_at=datetime(2026, 7, 21, 10, tzinfo=UTC),
                subject="Debian beta fixture",
                labels=("inbox",),
                attachments=(MailAttachment(filename="note.txt", content_type="text/plain", size_bytes=4),),
                body_text="hello",
                body_html=None,
                fresh_at=datetime(2026, 7, 21, 12, tzinfo=UTC),
                source="local-eml",
                cached=True,
            )
        ],
        calendar_events=[],
        communications=[],
    )
    widget = AttentionWidget(store=store)
    qtbot.addWidget(widget)

    assert "Mail 1" in widget._summary.text()
    assert "Debian beta fixture" in widget._detail.text()
