"""Gmail newsletter collector via Composio — pulls recent AI newsletter emails."""

from __future__ import annotations

import asyncio

from nightshift.config import GmailConfig
from nightshift.integrations import execute_action
from nightshift.models import TrendingItem


class GmailCollector:
    """Pulls newsletter emails from Gmail via Composio and extracts content."""

    source_name = "gmail"

    def __init__(self, config: GmailConfig) -> None:
        self.config = config

    async def collect(self) -> list[TrendingItem]:
        """Fetch recent newsletter emails matching configured search terms."""
        query = " OR ".join(self.config.search_terms) if self.config.search_terms else "newsletter"

        result = await asyncio.to_thread(
            execute_action,
            "GMAIL_FETCH_EMAILS",
            {
                "query": query,
                "max_results": self.config.max_results,
            },
        )

        items: list[TrendingItem] = []
        messages = (
            result.get("data", {}).get("messages")
            or result.get("messages")
            or []
        )
        for msg in messages:
            subject = msg.get("subject", "")
            sender = msg.get("sender", "") or msg.get("from", "")
            snippet = msg.get("messageText", "")[:500] or msg.get("snippet", "") or ""
            message_id = msg.get("messageId", "") or msg.get("id", "")

            if not subject:
                continue

            items.append(
                TrendingItem(
                    title=f"[Newsletter] {subject}",
                    url=f"https://mail.google.com/mail/u/0/#inbox/{message_id}" if message_id else "",
                    source=self.source_name,
                    score=0,
                    description=f"From: {sender}\n{snippet[:300]}",
                )
            )

        print(f"[gmail] Collected {len(items)} newsletter email(s)")
        return items
