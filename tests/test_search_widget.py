from datetime import UTC, datetime

from floating_agent.domain.search_result import SearchResult
from floating_agent.overlay.widgets.search_widget import SearchWidget
from pytestqt.qtbot import QtBot


class _FakeIndex:
    def search(self, query: str, *, limit: int = 10) -> list[SearchResult]:
        return [
            SearchResult(
                kind="mail",
                resource_id="msg-1",
                title="Debian beta fixture",
                summary="Demo Sender — offline checklist",
                source="local-eml",
                fresh_at=datetime(2026, 7, 21, 12, tzinfo=UTC),
                cached=True,
            )
        ]


def test_search_widget_renders_results(qtbot: QtBot) -> None:
    widget = SearchWidget(search_index=_FakeIndex())
    qtbot.addWidget(widget)

    widget._query.setText("beta")
    widget.search()

    assert "Debian beta fixture" in widget._results.toPlainText()
