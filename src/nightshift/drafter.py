"""Tweet drafter using Claude API."""

from __future__ import annotations

import anthropic

from nightshift.config import DrafterConfig, StyleConfig
from nightshift.models import TrendingItem, TweetDraft


class Drafter:
    def __init__(self, config: DrafterConfig, style: StyleConfig) -> None:
        self.config = config
        self.style = style
        self.client = anthropic.Anthropic()

    async def draft(self, items: list[TrendingItem]) -> list[TweetDraft]:
        if not items:
            return []

        items = items[: self.config.max_tweets]
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(items)

        message = self.client.messages.create(
            model=self.config.model,
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )

        response_text = message.content[0].text
        return self._parse_drafts(response_text, items)

    def _build_system_prompt(self) -> str:
        examples_block = "\n\n".join(
            f"Example {i+1}:\n{ex.strip()}"
            for i, ex in enumerate(self.style.examples)
        )
        guidelines = "\n".join(f"- {g}" for g in self.style.guidelines)

        return f"""{self.style.persona.strip()}

## Guidelines
{guidelines}

## Example tweets
{examples_block}"""

    def _build_user_prompt(self, items: list[TrendingItem]) -> str:
        items_block = "\n\n".join(
            f"[{i+1}] {item.title}\n    URL: {item.url}\n    Source: {item.source} | Score: {item.score}"
            + (f"\n    Description: {item.description[:200]}" if item.description else "")
            for i, item in enumerate(items)
        )

        return f"""Draft one tweet for each of the following trending items.
Return exactly one tweet per item, separated by a line containing only "---".
Do not include numbering, labels, or any extra text — just the tweet text.

{items_block}"""

    def _parse_drafts(
        self, response: str, items: list[TrendingItem]
    ) -> list[TweetDraft]:
        blocks = [b.strip() for b in response.split("---") if b.strip()]
        drafts: list[TweetDraft] = []
        for i, text in enumerate(blocks):
            if i >= len(items):
                break
            drafts.append(TweetDraft(text=text, source_item=items[i]))
        return drafts
