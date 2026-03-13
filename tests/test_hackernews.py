"""Tests for Hacker News collector."""

import pytest
import httpx
import respx

from nightshift.collectors.hackernews import HackerNewsCollector, HN_TOP_STORIES, HN_ITEM
from nightshift.config import HackerNewsConfig


@pytest.fixture
def hn_config():
    return HackerNewsConfig(enabled=True, top_n=3, min_score=10)


@respx.mock
@pytest.mark.asyncio
async def test_collect_stories(hn_config):
    # Mock top stories endpoint
    respx.get(HN_TOP_STORIES).mock(
        return_value=httpx.Response(200, json=[1, 2, 3, 4, 5, 6])
    )

    # Mock individual story endpoints
    for i in range(1, 7):
        respx.get(HN_ITEM.format(id=i)).mock(
            return_value=httpx.Response(200, json={
                "id": i,
                "type": "story",
                "title": f"Story {i}",
                "url": f"https://example.com/{i}",
                "score": i * 20,
            })
        )

    collector = HackerNewsCollector(hn_config)
    items = await collector.collect()

    assert len(items) == 3
    assert all(item.source == "hackernews" for item in items)
    assert all(item.score >= 10 for item in items)


@respx.mock
@pytest.mark.asyncio
async def test_collect_filters_low_score(hn_config):
    hn_config.min_score = 100

    respx.get(HN_TOP_STORIES).mock(
        return_value=httpx.Response(200, json=[1, 2])
    )
    for i in range(1, 3):
        respx.get(HN_ITEM.format(id=i)).mock(
            return_value=httpx.Response(200, json={
                "id": i,
                "type": "story",
                "title": f"Story {i}",
                "url": f"https://example.com/{i}",
                "score": 50,  # below threshold
            })
        )

    collector = HackerNewsCollector(hn_config)
    items = await collector.collect()

    assert len(items) == 0


@respx.mock
@pytest.mark.asyncio
async def test_collect_handles_missing_url(hn_config):
    respx.get(HN_TOP_STORIES).mock(
        return_value=httpx.Response(200, json=[42])
    )
    respx.get(HN_ITEM.format(id=42)).mock(
        return_value=httpx.Response(200, json={
            "id": 42,
            "type": "story",
            "title": "Ask HN: Something",
            "score": 200,
            # no url field — should fallback to HN item URL
        })
    )

    collector = HackerNewsCollector(hn_config)
    items = await collector.collect()

    assert len(items) == 1
    assert "news.ycombinator.com" in items[0].url
