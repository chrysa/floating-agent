"""Tests for the Notion tools + page parsing (no live Notion)."""

from __future__ import annotations

from floating_agent.agent.tools import build_notion_tools
from floating_agent.plugins.notion import NotionPage, _UNTITLED, _extract_title, _parse_page


class _FakeNotion:
    def __init__(self) -> None:
        self.created: list[tuple[str, str]] = []

    def search(self, query: str) -> list[NotionPage]:
        if query == "empty":
            return []
        return [NotionPage(id="p1", title="Roadmap", url="https://n/p1")]

    def create_task(self, database_id: str, title: str) -> NotionPage:
        self.created.append((database_id, title))
        return NotionPage(id="p2", title=title, url="https://n/p2")


def test_parse_page_extracts_title() -> None:
    raw = {
        "id": "abc",
        "url": "https://n/abc",
        "properties": {"Name": {"type": "title", "title": [{"plain_text": "Hello"}]}},
    }
    page = _parse_page(raw)
    assert page == NotionPage(id="abc", title="Hello", url="https://n/abc")


def test_extract_title_falls_back_when_missing() -> None:
    assert _extract_title({"properties": {}}) == _UNTITLED
    assert _extract_title({}) == _UNTITLED


def test_search_tool_formats_results() -> None:
    [search] = build_notion_tools(_FakeNotion())
    out = search.run({"query": "road"})
    assert "Roadmap" in out
    assert "https://n/p1" in out


def test_search_tool_handles_no_results() -> None:
    [search] = build_notion_tools(_FakeNotion())
    assert "No matching" in search.run({"query": "empty"})


def test_no_write_tool_without_database() -> None:
    tools = build_notion_tools(_FakeNotion())
    assert [t.name for t in tools] == ["notion_search"]


def test_create_tool_is_confirm_gated_and_creates() -> None:
    fake = _FakeNotion()
    tools = build_notion_tools(fake, database_id="db1")
    create = next(t for t in tools if t.name == "notion_create_task")
    assert create.requires_confirmation is True
    out = create.run({"title": "Buy milk"})
    assert fake.created == [("db1", "Buy milk")]
    assert "Buy milk" in out
