"""Morning brief builder using Claude API."""

from __future__ import annotations

import json
import re

import anthropic

from nightshift.config import BriefBuilderConfig, StyleConfig
from nightshift.models import (
    BriefSection,
    MorningBrief,
    TrendingItem,
    XProfileContext,
    XSearchResult,
)


class BriefBuilder:
    def __init__(self, config: BriefBuilderConfig, style: StyleConfig) -> None:
        self.config = config
        self.style = style
        self.client = anthropic.Anthropic()

    async def build(
        self,
        items: list[TrendingItem],
        x_results: list[XSearchResult],
        profile_context: XProfileContext | None = None,
    ) -> MorningBrief:
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(items, x_results, profile_context)

        message = self.client.messages.create(
            model=self.config.model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        response_text = message.content[0].text
        return self._parse_brief(response_text)

    def _build_system_prompt(self) -> str:
        interests = "\n".join(f"- {i}" for i in self.style.interests)
        angles = "\n".join(f"- {a}" for a in self.style.angle_types)

        return f"""You are a morning brief compiler for a developer focused on AI, dev tools, and vibecoding.

## Voice & Interests
{self.style.voice_notes.strip()}

Key interests:
{interests}

## Angle types for tweet ideas
{angles}

## Your task
Produce a structured JSON response containing the most interesting, relevant, and actionable items from the provided sources. Group them into sections.

Each section has:
- "category": one of "Big Releases", "Drama & Hot Takes", "Cool Projects", "Industry Moves", "Vibecoding", "Sleeper Hits", "People to Engage With", "Tech to Try"
- "headline": one-line summary of what happened
- "context": 2-3 sentences explaining the situation and why it matters
- "sources": list of URLs or tweet links
- "tweet_ideas": 2-3 angle suggestions (NOT pre-written tweets). Examples: "react to X with first impressions", "contrarian take on Y", "try this tool and post about it"

Target 5-{self.config.max_sections} sections. Pick only the most interesting items — not everything needs a section.

If the user's recent tweets are provided, avoid suggesting topics they've already covered.

## Response format
Return ONLY valid JSON — an array of section objects. No markdown fences, no commentary outside the JSON.

Example:
[
  {{
    "category": "Big Releases",
    "headline": "OpenAI ships GPT-5 with native tool use",
    "context": "OpenAI announced GPT-5 today with built-in function calling...",
    "sources": ["https://openai.com/blog/gpt-5"],
    "tweet_ideas": ["hot take on whether this changes the agent landscape", "compare to Claude's tool use approach"]
  }}
]"""

    def _build_user_prompt(
        self,
        items: list[TrendingItem],
        x_results: list[XSearchResult],
        profile_context: XProfileContext | None = None,
    ) -> str:
        parts: list[str] = []

        # Traditional collector items
        if items:
            items_block = "\n\n".join(
                f"[{item.source}] {item.title}\n"
                f"  URL: {item.url}\n"
                f"  Score: {item.score}"
                + (f"\n  Description: {item.description[:300]}" if item.description else "")
                for item in items
            )
            parts.append(f"## Trending items (HN, Reddit, GitHub, RSS)\n\n{items_block}")

        # X search results
        if x_results:
            x_block = "\n\n".join(
                f"[{r.category} / {r.query_name}]\n{r.summary}"
                for r in x_results
            )
            parts.append(f"## X/Twitter search results\n\n{x_block}")

        # Profile context
        if profile_context and profile_context.recent_tweets:
            tweets_block = "\n".join(
                f"- {tweet}" for tweet in profile_context.recent_tweets
            )
            parts.append(
                f"## Aaron's recent tweets (avoid repeating these topics)\n\n{tweets_block}"
            )

        if not parts:
            parts.append("No sources available — generate a brief based on general AI/dev trends.")

        return "\n\n---\n\n".join(parts)

    def _parse_brief(self, response: str) -> MorningBrief:
        """Parse Claude's JSON response into a MorningBrief."""
        # Strip markdown code fences if present
        cleaned = response.strip()
        cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned)
        cleaned = cleaned.strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            print(f"[brief_builder] Failed to parse JSON response: {e}")
            print(f"[brief_builder] Raw response:\n{response[:500]}")
            return MorningBrief(sections=[])

        if not isinstance(data, list):
            print("[brief_builder] Expected JSON array, got something else")
            return MorningBrief(sections=[])

        sections: list[BriefSection] = []
        for item in data:
            try:
                section = BriefSection(
                    category=item.get("category", "Uncategorized"),
                    headline=item.get("headline", ""),
                    context=item.get("context", ""),
                    sources=item.get("sources", []),
                    tweet_ideas=item.get("tweet_ideas", []),
                )
                sections.append(section)
            except (KeyError, TypeError) as e:
                print(f"[brief_builder] Skipping malformed section: {e}")
                continue

        print(f"[brief_builder] Parsed {len(sections)} section(s)")
        return MorningBrief(sections=sections)
