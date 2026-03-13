"""Grok-powered X/Twitter search collector — runs categorised queries via xAI API."""

from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone

from openai import OpenAI

from nightshift.config import XSearchConfig
from nightshift.models import XSearchResult

logger = logging.getLogger(__name__)


def _build_client() -> OpenAI:
    """Create an OpenAI client pointed at the xAI endpoint."""
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise RuntimeError("XAI_API_KEY environment variable is not set")
    return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")


def _build_query_prompt(query_prompt: str, lookback_hours: int) -> str:
    """Build a detailed prompt for a single search query."""
    return (
        f"Search X/Twitter for the last {lookback_hours} hours and summarize: "
        f"{query_prompt}. "
        "Focus on the most notable, high-engagement posts and developments. "
        "Provide specific accounts, tweets, and links where possible."
    )


def _run_single_query(
    client: OpenAI,
    model: str,
    query_name: str,
    query_prompt: str,
    lookback_hours: int,
    from_date: str,
    to_date: str,
) -> XSearchResult:
    """Execute a single Grok x_search query (synchronous)."""
    prompt = _build_query_prompt(query_prompt, lookback_hours)

    response = client.responses.create(
        model=model,
        tools=[
            {
                "type": "x_search",
                "x_search": {"from_date": from_date, "to_date": to_date},
            },
            {"type": "web_search"},
        ],
        input=prompt,
    )

    # Extract the text content from the response
    summary_parts: list[str] = []
    for block in response.output:
        if hasattr(block, "text"):
            summary_parts.append(block.text)
        elif hasattr(block, "content"):
            for content_block in block.content:
                if hasattr(content_block, "text"):
                    summary_parts.append(content_block.text)

    summary = "\n".join(summary_parts).strip()
    if not summary:
        summary = "(No results found)"

    # Derive category from query name
    category = query_name.lower().replace(" ", "_")

    return XSearchResult(
        category=category,
        query_name=query_name,
        summary=summary,
    )


class XSearchCollector:
    """Runs multiple targeted X/Twitter search queries via Grok API in parallel."""

    source_name = "xsearch"

    def __init__(self, config: XSearchConfig) -> None:
        self.config = config

    async def collect(self) -> list[XSearchResult]:
        """Run all configured queries concurrently and return results."""
        if not self.config.queries:
            logger.warning("XSearchCollector: no queries configured, skipping")
            return []

        client = _build_client()

        now = datetime.now(timezone.utc)
        from_dt = now - timedelta(hours=self.config.lookback_hours)
        from_date = from_dt.strftime("%Y-%m-%d")
        to_date = now.strftime("%Y-%m-%d")

        tasks = [
            asyncio.to_thread(
                _run_single_query,
                client,
                self.config.model,
                query.name,
                query.prompt,
                self.config.lookback_hours,
                from_date,
                to_date,
            )
            for query in self.config.queries
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        collected: list[XSearchResult] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                query_name = self.config.queries[i].name
                logger.error("XSearch query '%s' failed: %s", query_name, result)
            else:
                collected.append(result)

        return collected
