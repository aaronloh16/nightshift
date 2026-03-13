"""Tests for domain models."""

from nightshift.models import Digest, TrendingItem, TweetDraft


def test_trending_item_dedup_key():
    item = TrendingItem(title="Test", url="https://example.com", source="test")
    assert item.dedup_key == "https://example.com"


def test_digest_summary():
    item = TrendingItem(title="Test", url="https://example.com", source="hackernews", score=100)
    draft = TweetDraft(text="This is a tweet", source_item=item)
    digest = Digest(drafts=[draft])

    summary = digest.summary
    assert "Nightshift Digest" in summary
    assert "This is a tweet" in summary
    assert "https://example.com" in summary
    assert "hackernews" in summary


def test_digest_empty():
    digest = Digest(drafts=[])
    assert "Nightshift Digest" in digest.summary
