"""Pipeline orchestrator: collect → draft → deliver."""

from __future__ import annotations

import asyncio

from nightshift.collectors.base import Collector
from nightshift.collectors.github import GitHubCollector
from nightshift.collectors.hackernews import HackerNewsCollector
from nightshift.collectors.reddit import RedditCollector
from nightshift.config import Settings, StyleConfig
from nightshift.delivery import TelegramDelivery
from nightshift.drafter import Drafter
from nightshift.models import Digest, TrendingItem


def _build_collectors(settings: Settings) -> list[Collector]:
    collectors: list[Collector] = []
    cfg = settings.collectors
    if cfg.hackernews.enabled:
        collectors.append(HackerNewsCollector(cfg.hackernews))
    if cfg.github.enabled:
        collectors.append(GitHubCollector(cfg.github))
    if cfg.reddit.enabled:
        collectors.append(RedditCollector(cfg.reddit))
    return collectors


def _deduplicate(items: list[TrendingItem]) -> list[TrendingItem]:
    seen: set[str] = set()
    unique: list[TrendingItem] = []
    for item in items:
        if item.dedup_key not in seen:
            seen.add(item.dedup_key)
            unique.append(item)
    return unique


async def collect(settings: Settings) -> list[TrendingItem]:
    """Run all enabled collectors concurrently and return deduplicated items."""
    collectors = _build_collectors(settings)
    if not collectors:
        print("[pipeline] No collectors enabled")
        return []

    print(f"[pipeline] Running {len(collectors)} collector(s)...")
    results = await asyncio.gather(
        *(c.collect() for c in collectors), return_exceptions=True
    )

    all_items: list[TrendingItem] = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"[pipeline] Collector {collectors[i].source_name} failed: {result}")
            continue
        print(f"[pipeline] {collectors[i].source_name}: {len(result)} items")
        all_items.extend(result)

    deduped = _deduplicate(all_items)
    print(f"[pipeline] {len(deduped)} unique items after dedup")
    return deduped


async def draft(settings: Settings, style: StyleConfig, items: list[TrendingItem]) -> Digest:
    """Draft tweets for the given items."""
    drafter = Drafter(settings.drafter, style)
    print(f"[pipeline] Drafting tweets for {len(items)} items...")
    drafts = await drafter.draft(items)
    print(f"[pipeline] Generated {len(drafts)} draft(s)")
    return Digest(drafts=drafts)


async def deliver(settings: Settings, digest: Digest) -> None:
    """Send digest via configured delivery channel."""
    delivery = TelegramDelivery(settings.delivery)
    await delivery.send(digest)


async def run(settings: Settings, style: StyleConfig) -> Digest:
    """Full pipeline: collect → draft → deliver."""
    items = await collect(settings)
    if not items:
        print("[pipeline] No items collected — nothing to draft")
        return Digest(drafts=[])

    digest = await draft(settings, style, items)

    # Always print to terminal
    print("\n" + digest.summary)

    # Deliver via Telegram if enabled
    await deliver(settings, digest)

    return digest
