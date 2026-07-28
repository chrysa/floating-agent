"""Provider-agnostic search result for local cached content."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(frozen=True, slots=True)
class SearchResult:
    """Represent one local search hit."""

    kind: str
    resource_id: str
    title: str
    summary: str
    source: str
    fresh_at: datetime
    cached: bool

    def __post_init__(self) -> None:
        if self.fresh_at.tzinfo is None:
            raise ValueError("fresh_at must be timezone-aware")
