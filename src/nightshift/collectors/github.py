"""GitHub trending repos collector via Composio."""

from __future__ import annotations

from datetime import datetime, timedelta

from nightshift.config import GitHubConfig
from nightshift.integrations import execute_action
from nightshift.models import TrendingItem


class GitHubCollector:
    source_name = "github"

    def __init__(self, config: GitHubConfig) -> None:
        self.config = config

    async def collect(self) -> list[TrendingItem]:
        since = datetime.now() - timedelta(days=self.config.created_within_days)
        date_str = since.strftime("%Y-%m-%d")

        # Build query: recently created, min stars, topic filter
        topic_filter = " ".join(f"topic:{t}" for t in self.config.topics[:3])
        query = f"created:>{date_str} stars:>={self.config.min_stars} {topic_filter}"

        result = execute_action(
            "GITHUB_SEARCH_REPOSITORIES",
            {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": self.config.top_n,
            },
        )

        items: list[TrendingItem] = []
        for repo in (result.get("items") or [])[:self.config.top_n]:
            items.append(
                TrendingItem(
                    title=repo.get("full_name", ""),
                    url=repo.get("html_url", ""),
                    source=self.source_name,
                    score=repo.get("stargazers_count", 0),
                    description=repo.get("description", "") or "",
                )
            )
        return items
