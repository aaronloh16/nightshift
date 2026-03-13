"""Tests for domain models."""

from nightshift.models import BriefSection, MorningBrief, TrendingItem


def test_trending_item_dedup_key():
    item = TrendingItem(title="Test", url="https://example.com", source="test")
    assert item.dedup_key == "https://example.com"


def test_morning_brief_summary():
    section = BriefSection(
        category="Big Releases",
        headline="Test headline",
        context="Some context about the release.",
        sources=["https://example.com"],
        tweet_ideas=["react to this release"],
    )
    brief = MorningBrief(sections=[section])

    summary = brief.summary
    assert "Morning Brief" in summary
    assert "BIG RELEASES" in summary
    assert "Test headline" in summary
    assert "https://example.com" in summary
    assert "react to this release" in summary


def test_morning_brief_empty():
    brief = MorningBrief(sections=[])
    assert "Morning Brief" in brief.summary
