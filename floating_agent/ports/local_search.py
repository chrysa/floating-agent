"""Local search index contract."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence

    from floating_agent.domain.search_result import SearchResult


class LocalSearchIndex(Protocol):
    """Search cached local content without exposing storage details."""

    def search(self, query: str, *, limit: int = 10) -> Sequence[SearchResult]:
        """Return the best local matches for a free-text query."""
        ...
