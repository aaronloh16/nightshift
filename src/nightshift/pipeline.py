"""Pipeline orchestrator: collect → build brief → deliver."""

from __future__ import annotations

import asyncio

from nightshift.collectors.base import Collector
from nightshift.collectors.github import GitHubCollector
from nightshift.collectors.gmail import GmailCollector
from nightshift.collectors.hackernews import HackerNewsCollector
from nightshift.collectors.reddit import RedditCollector
from nightshift.collectors.rss import RSSCollector
from nightshift.collectors.smart import SmartCollector
from nightshift.collectors.xsearch import XSearchCollector
from nightshift.collectors.x_profile import XProfileCollector
from nightshift.config import Settings, StyleConfig
from nightshift.delivery import TelegramDelivery
from nightshift.brief_builder import BriefBuilder
from nightshift.models import MorningBrief, TrendingItem, XProfileContext, XSearchResult


def _build_collectors(settings: Settings) -> list[Collector]:
    """Build traditional collectors that return TrendingItem lists."""
    collectors: list[Collector] = []
    cfg = settings.collectors
    if cfg.hackernews.enabled:
        collectors.append(HackerNewsCollector(cfg.hackernews))
    if cfg.github.enabled:
        collectors.append(GitHubCollector(cfg.github))
    if cfg.reddit.enabled:
        collectors.append(RedditCollector(cfg.reddit))
    if cfg.rss.enabled:
        collectors.append(RSSCollector(cfg.rss))
    if cfg.gmail.enabled:
        collectors.append(GmailCollector(cfg.gmail))
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
    """Run all enabled traditional collectors concurrently and return deduplicated items."""
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


async def collect_x_search(settings: Settings) -> list[XSearchResult]:
    """Run smart collector (preferred) or legacy X search collector."""
    # Smart collector supersedes xsearch — it does newsletters + X search in one agent loop
    smart_cfg = settings.collectors.smart
    if smart_cfg.enabled:
        print("[pipeline] Running smart collector (Grok + Composio metatools)...")
        try:
            collector = SmartCollector(smart_cfg)
            results = await collector.collect()
            print(f"[pipeline] Smart collector: {len(results)} results")
            return results
        except Exception as e:
            print(f"[pipeline] Smart collector failed: {e}")
            return []

    # Fallback to legacy xsearch
    cfg = settings.collectors.xsearch
    if not cfg.enabled:
        return []

    print("[pipeline] Running X search collector...")
    try:
        collector = XSearchCollector(cfg)
        results = await collector.collect()
        print(f"[pipeline] X search: {len(results)} results")
        return results
    except Exception as e:
        print(f"[pipeline] X search collector failed: {e}")
        return []


async def collect_x_profile(settings: Settings) -> XProfileContext | None:
    """Run X profile collector if enabled."""
    cfg = settings.collectors.x_profile
    if not cfg.enabled:
        return None

    print("[pipeline] Running X profile collector...")
    try:
        collector = XProfileCollector(cfg)
        context = await collector.collect()
        print(f"[pipeline] X profile: {len(context.recent_tweets)} recent tweets")
        return context
    except Exception as e:
        print(f"[pipeline] X profile collector failed: {e}")
        return None


async def build_brief(
    settings: Settings,
    style: StyleConfig,
    items: list[TrendingItem],
    x_results: list[XSearchResult] | None = None,
    profile_context: XProfileContext | None = None,
) -> MorningBrief:
    """Build morning brief from collected data."""
    builder = BriefBuilder(settings.brief_builder, style)
    print(f"[pipeline] Building brief from {len(items)} items, {len(x_results or [])} X results...")
    brief = await builder.build(items, x_results or [], profile_context)
    print(f"[pipeline] Generated brief with {len(brief.sections)} section(s)")
    return brief


async def deliver(settings: Settings, brief: MorningBrief) -> None:
    """Send brief via configured delivery channel."""
    delivery = TelegramDelivery(settings.delivery)
    await delivery.send(brief)


async def run(settings: Settings, style: StyleConfig) -> MorningBrief:
    """Full pipeline: collect → build brief → deliver."""
    # Run all collectors in parallel
    items, x_results, profile_context = await asyncio.gather(
        collect(settings),
        collect_x_search(settings),
        collect_x_profile(settings),
    )

    if not items and not x_results:
        print("[pipeline] No items collected — nothing to build")
        return MorningBrief(sections=[])

    brief = await build_brief(settings, style, items, x_results, profile_context)

    # Always print to terminal
    print("\n" + brief.summary)

    # Deliver via Telegram if enabled
    await deliver(settings, brief)

    return brief
