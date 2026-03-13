"""Domain models for the Nightshift pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TrendingItem:
    """A single trending item collected from any source."""

    title: str
    url: str
    source: str  # "hackernews", "github", "reddit"
    score: int = 0
    description: str = ""
    collected_at: datetime = field(default_factory=datetime.now)

    @property
    def dedup_key(self) -> str:
        return self.url


@dataclass
class TweetDraft:
    """A drafted tweet based on a trending item."""

    text: str
    source_item: TrendingItem
    drafted_at: datetime = field(default_factory=datetime.now)


@dataclass
class Digest:
    """A collection of tweet drafts ready for delivery."""

    drafts: list[TweetDraft]
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def summary(self) -> str:
        lines = [f"🌅 Nightshift Digest — {self.created_at:%Y-%m-%d %H:%M}", ""]
        for i, draft in enumerate(self.drafts, 1):
            lines.append(f"--- Tweet {i} ({draft.source_item.source}) ---")
            lines.append(draft.text)
            lines.append(f"Source: {draft.source_item.url}")
            lines.append("")
        return "\n".join(lines)
