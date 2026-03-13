"""Hacker News collector using the public API (no Composio needed)."""

from __future__ import annotations

import asyncio

import httpx

from nightshift.config import HackerNewsConfig
from nightshift.models import TrendingItem

HN_TOP_STORIES = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{id}.json"


class HackerNewsCollector:
    source_name = "hackernews"

    def __init__(self, config: HackerNewsConfig) -> None:
        self.config = config

    async def collect(self) -> list[TrendingItem]:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(HN_TOP_STORIES)
            resp.raise_for_status()
            story_ids: list[int] = resp.json()

            # Fetch top N stories concurrently
            fetch_n = min(self.config.top_n * 2, len(story_ids))
            tasks = [
                self._fetch_item(client, sid) for sid in story_ids[:fetch_n]
            ]
            items = await asyncio.gather(*tasks, return_exceptions=True)

        results: list[TrendingItem] = []
        for item in items:
            if isinstance(item, Exception) or item is None:
                continue
            if item.score >= self.config.min_score:
                results.append(item)
            if len(results) >= self.config.top_n:
                break

        return results

    async def _fetch_item(self, client: httpx.AsyncClient, story_id: int) -> TrendingItem | None:
        resp = await client.get(HN_ITEM.format(id=story_id))
        resp.raise_for_status()
        data = resp.json()
        if not data or data.get("type") != "story":
            return None
        return TrendingItem(
            title=data.get("title", ""),
            url=data.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
            source=self.source_name,
            score=data.get("score", 0),
            description=data.get("text", "") or "",
        )
