"""RSS feed collector using feedparser."""

import asyncio
from datetime import datetime

import feedparser

from nightshift.config import RSSConfig
from nightshift.models import TrendingItem


class RSSCollector:
    source_name = "rss"

    def __init__(self, config: RSSConfig) -> None:
        self.config = config

    async def collect(self) -> list[TrendingItem]:
        # Run feedparser in thread pool (it's synchronous + does HTTP)
        tasks = [
            asyncio.to_thread(self._fetch_feed, feed_url)
            for feed_url in self.config.feeds
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_items: list[TrendingItem] = []
        for result in results:
            if isinstance(result, Exception):
                print(f"[rss] Feed failed: {result}")
                continue
            all_items.extend(result)

        # Sort by published date (newest first), return top_n
        all_items.sort(key=lambda x: x.collected_at, reverse=True)
        return all_items[: self.config.top_n]

    def _fetch_feed(self, url: str) -> list[TrendingItem]:
        feed = feedparser.parse(url)
        items: list[TrendingItem] = []
        for entry in feed.entries[: self.config.max_per_feed]:
            published = (
                datetime(*entry.published_parsed[:6])
                if hasattr(entry, "published_parsed") and entry.published_parsed
                else datetime.now()
            )
            items.append(
                TrendingItem(
                    title=entry.get("title", ""),
                    url=entry.get("link", ""),
                    source=self.source_name,
                    score=0,
                    description=entry.get("summary", "")[:300] if entry.get("summary") else "",
                    collected_at=published,
                )
            )
        return items
