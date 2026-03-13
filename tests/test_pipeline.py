"""Tests for pipeline orchestration."""

from nightshift.models import TrendingItem
from nightshift.pipeline import _deduplicate


def test_deduplicate_by_url():
    items = [
        TrendingItem(title="A", url="https://example.com/1", source="hackernews"),
        TrendingItem(title="B", url="https://example.com/1", source="reddit"),  # duplicate URL
        TrendingItem(title="C", url="https://example.com/2", source="github"),
    ]
    result = _deduplicate(items)
    assert len(result) == 2
    assert result[0].title == "A"
    assert result[1].title == "C"


def test_deduplicate_empty():
    assert _deduplicate([]) == []
