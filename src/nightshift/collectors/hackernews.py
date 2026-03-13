"""Hacker News collector using the public API + Algolia search."""

from __future__ import annotations

import asyncio

import httpx

from nightshift.config import HackerNewsConfig
from nightshift.models import TrendingItem

HN_TOP_STORIES = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
HN_ALGOLIA_SEARCH = "http://hn.algolia.com/api/v1/search"


class HackerNewsCollector:
    source_name = "hackernews"

    def __init__(self, config: HackerNewsConfig) -> None:
        self.config = config

    async def collect(self) -> list[TrendingItem]:
        async with httpx.AsyncClient(timeout=15) as client:
            # Build all tasks to run in parallel
            tasks: list[asyncio.Task[list[TrendingItem]]] = []

            # 1. Top stories (existing behavior)
            tasks.append(asyncio.ensure_future(self._fetch_top_stories(client)))

            # 2. Algolia keyword searches
            for keyword in self.config.search_keywords:
                tasks.append(asyncio.ensure_future(self._search_algolia(client, keyword)))

            # 3. Show HN posts
            if self.config.show_hn:
                tasks.append(asyncio.ensure_future(self._fetch_show_hn(client)))

            results = await asyncio.gather(*tasks, return_exceptions=True)

        # Merge and deduplicate
        seen_urls: set[str] = set()
        all_items: list[TrendingItem] = []
        for result in results:
            if isinstance(result, Exception):
                print(f"[hackernews] Fetch failed: {result}")
                continue
            for item in result:
                if item.url not in seen_urls:
                    seen_urls.add(item.url)
                    all_items.append(item)

        # Sort by score descending, return top_n
        all_items.sort(key=lambda x: x.score, reverse=True)
        return all_items[: self.config.top_n]

    async def _fetch_top_stories(self, client: httpx.AsyncClient) -> list[TrendingItem]:
        resp = await client.get(HN_TOP_STORIES)
        resp.raise_for_status()
        story_ids: list[int] = resp.json()

        fetch_n = min(self.config.top_n * 2, len(story_ids))
        tasks = [self._fetch_item(client, sid) for sid in story_ids[:fetch_n]]
        items = await asyncio.gather(*tasks, return_exceptions=True)

        results: list[TrendingItem] = []
        for item in items:
            if isinstance(item, Exception) or item is None:
                continue
            if item.score >= self.config.min_score:
                results.append(item)

        return results

    async def _search_algolia(self, client: httpx.AsyncClient, keyword: str) -> list[TrendingItem]:
        resp = await client.get(
            HN_ALGOLIA_SEARCH,
            params={
                "query": keyword,
                "tags": "story",
                "numericFilters": f"points>{self.config.min_score}",
            },
        )
        resp.raise_for_status()
        data = resp.json()

        results: list[TrendingItem] = []
        for hit in data.get("hits", []):
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
            results.append(
                TrendingItem(
                    title=hit.get("title", ""),
                    url=url,
                    source=self.source_name,
                    score=hit.get("points", 0),
                    description=hit.get("story_text", "") or "",
                )
            )
        return results

    async def _fetch_show_hn(self, client: httpx.AsyncClient) -> list[TrendingItem]:
        resp = await client.get(
            HN_ALGOLIA_SEARCH,
            params={
                "tags": "show_hn",
                "numericFilters": f"points>{self.config.min_score}",
            },
        )
        resp.raise_for_status()
        data = resp.json()

        results: list[TrendingItem] = []
        for hit in data.get("hits", []):
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
            results.append(
                TrendingItem(
                    title=hit.get("title", ""),
                    url=url,
                    source=self.source_name,
                    score=hit.get("points", 0),
                    description=hit.get("story_text", "") or "",
                )
            )
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
