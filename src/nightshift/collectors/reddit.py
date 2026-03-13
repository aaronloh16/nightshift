"""Reddit hot posts collector via Composio."""

from __future__ import annotations

from nightshift.config import RedditConfig
from nightshift.integrations import execute_action
from nightshift.models import TrendingItem


class RedditCollector:
    source_name = "reddit"

    def __init__(self, config: RedditConfig) -> None:
        self.config = config

    async def collect(self) -> list[TrendingItem]:
        items: list[TrendingItem] = []

        for subreddit in self.config.subreddits:
            result = execute_action(
                "REDDIT_GET_HOT_POSTS",
                {
                    "subreddit": subreddit,
                    "limit": self.config.top_n,
                    "t": self.config.time_filter,
                },
            )

            for post in (result.get("data", {}).get("children") or []):
                data = post.get("data", {}) if isinstance(post, dict) else {}
                items.append(
                    TrendingItem(
                        title=data.get("title", ""),
                        url=f"https://reddit.com{data.get('permalink', '')}",
                        source=self.source_name,
                        score=data.get("score", 0),
                        description=data.get("selftext", "")[:300] or "",
                    )
                )

        return items
