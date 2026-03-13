"""Domain models for the Nightshift pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TrendingItem:
    """A single trending item collected from any source."""

    title: str
    url: str
    source: str  # "hackernews", "github", "reddit", "rss"
    score: int = 0
    description: str = ""
    collected_at: datetime = field(default_factory=datetime.now)

    @property
    def dedup_key(self) -> str:
        return self.url


@dataclass
class XSearchResult:
    """Result from a single Grok x_search query."""

    category: str  # e.g. "releases", "drama"
    query_name: str
    summary: str  # Grok's narrative summary
    collected_at: datetime = field(default_factory=datetime.now)


@dataclass
class XProfileContext:
    """Context from Aaron's X account for the brief builder."""

    recent_tweets: list[str]
    collected_at: datetime = field(default_factory=datetime.now)


@dataclass
class BriefSection:
    """One section of the morning brief."""

    category: str  # e.g. "releases", "drama", "tools"
    headline: str  # one-line summary
    context: str  # 2-3 sentences of what happened
    sources: list[str]  # URLs / tweet links
    tweet_ideas: list[str]  # 2-3 angle suggestions


@dataclass
class MorningBrief:
    sections: list[BriefSection]
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def summary(self) -> str:
        """Format brief for display/delivery."""
        lines = [f"\U0001f305 Nightshift Morning Brief \u2014 {self.created_at:%Y-%m-%d %H:%M}", ""]
        for section in self.sections:
            lines.append(f"\u2501\u2501\u2501 {section.category.upper()} \u2501\u2501\u2501")
            lines.append(f"\U0001f4cc {section.headline}")
            lines.append("")
            lines.append(section.context)
            if section.sources:
                lines.append("")
                lines.append("Sources:")
                for src in section.sources:
                    lines.append(f"  \u2022 {src}")
            if section.tweet_ideas:
                lines.append("")
                lines.append("Tweet ideas:")
                for idea in section.tweet_ideas:
                    lines.append(f"  \U0001f4a1 {idea}")
            lines.append("")
        return "\n".join(lines)
