"""X/Twitter profile collector — pulls recent tweets for posting context via Composio."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime

from nightshift.config import XProfileConfig
from nightshift.integrations import execute_action
from nightshift.models import XProfileContext


@dataclass
class ProfileTweet:
    """A single tweet from the user's profile."""

    tweet_id: str
    text: str
    created_at: str
    likes: int = 0
    retweets: int = 0
    replies: int = 0


class XProfileCollector:
    """Pulls the user's recent tweets via Composio for posting context."""

    source_name = "x_profile"

    def __init__(self, config: XProfileConfig) -> None:
        self.config = config

    async def collect(self) -> XProfileContext:
        """Fetch recent tweets from the authenticated X account."""
        result = await asyncio.to_thread(
            execute_action,
            "TWITTER_GET_USER_TWEETS",
            {"count": self.config.lookback_count},
        )

        tweets: list[str] = []
        for item in result.get("tweets") or result.get("data") or []:
            text = item.get("text", "")
            if text:
                tweets.append(text)

        return XProfileContext(recent_tweets=tweets)
