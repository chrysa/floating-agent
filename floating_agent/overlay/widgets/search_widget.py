"""Local search widget for cached content."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget

if TYPE_CHECKING:
    from collections.abc import Sequence

    from floating_agent.domain.search_result import SearchResult
    from floating_agent.ports.local_search import LocalSearchIndex


class SearchWidget(QWidget):
    """Search local content and render compact matches."""

    def __init__(self, search_index: LocalSearchIndex | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._search_index = search_index
        self._query = QLineEdit()
        self._query.setPlaceholderText("Search local mail, calendar, and communications")
        self._query.returnPressed.connect(self.search)
        self._run = QPushButton("Search")
        self._run.clicked.connect(self.search)
        self._results = QTextEdit()
        self._results.setReadOnly(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self._query)
        layout.addWidget(self._run)
        layout.addWidget(self._results)

        self.search()

    def search(self) -> None:
        """Search the local index with the current query."""
        if self._search_index is None:
            self._results.setText("No local search index configured.")
            return

        query = self._query.text().strip()
        results = self._search_index.search(query, limit=5)
        self._results.setText(_format_results(query, results))


def _format_results(query: str, results: Sequence[SearchResult]) -> str:
    if not results:
        return f"No local matches for {query or 'recent content'}."
    lines = []
    for result in results:
        lines.append(
            f"{result.kind}: {result.title} — {result.summary} [{result.source}]"
            f" ({result.fresh_at.isoformat()})"
        )
    return "\n".join(lines)
