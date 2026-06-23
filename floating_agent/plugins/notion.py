"""Notion REST API client (read/write).

MCP is unavailable in a packaged app, so we talk to api.notion.com directly with
NOTION_API_KEY. Network methods are integration-only (pragma: no cover).
"""

from __future__ import annotations

from dataclasses import dataclass

_API = "https://api.notion.com/v1"
_VERSION = "2022-06-28"
_UNTITLED = "(untitled)"


@dataclass(frozen=True)
class NotionPage:
    """A minimal view of a Notion page/result."""

    id: str
    title: str
    url: str


class NotionClient:
    """Thin wrapper over the Notion REST API."""

    def __init__(self, api_key: str, timeout: float = 30.0) -> None:
        self._api_key = api_key
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Notion-Version": _VERSION,
            "Content-Type": "application/json",
        }

    def search(self, query: str) -> list[NotionPage]:  # pragma: no cover - needs live Notion
        import httpx

        resp = httpx.post(
            f"{_API}/search",
            headers=self._headers(),
            json={"query": query, "page_size": 5},
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return [_parse_page(r) for r in resp.json().get("results", [])]

    def create_task(self, database_id: str, title: str) -> NotionPage:  # pragma: no cover - needs live Notion
        import httpx

        resp = httpx.post(
            f"{_API}/pages",
            headers=self._headers(),
            json={
                "parent": {"database_id": database_id},
                "properties": {"Name": {"title": [{"text": {"content": title}}]}},
            },
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return _parse_page(resp.json())


def _parse_page(raw: dict[str, object]) -> NotionPage:
    page_id = str(raw.get("id", ""))
    url = str(raw.get("url", ""))
    title = _extract_title(raw)
    return NotionPage(id=page_id, title=title, url=url)


def _extract_title(raw: dict[str, object]) -> str:
    props = raw.get("properties")
    if not isinstance(props, dict):
        return _UNTITLED
    for value in props.values():
        if isinstance(value, dict) and value.get("type") == "title":
            parts = value.get("title", [])
            if isinstance(parts, list) and parts:
                first = parts[0]
                if isinstance(first, dict):
                    return str(first.get("plain_text", _UNTITLED))
    return _UNTITLED
