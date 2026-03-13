"""Tests for the tweet drafter."""

from nightshift.drafter import Drafter
from nightshift.config import DrafterConfig, StyleConfig
from nightshift.models import TrendingItem


def test_parse_drafts():
    config = DrafterConfig()
    style = StyleConfig(
        persona="Test persona",
        guidelines=["Keep it short"],
        examples=["Example tweet"],
    )
    drafter = Drafter(config, style)

    items = [
        TrendingItem(title="Item 1", url="https://example.com/1", source="hn"),
        TrendingItem(title="Item 2", url="https://example.com/2", source="hn"),
    ]

    response = "First tweet about item 1\n---\nSecond tweet about item 2"
    drafts = drafter._parse_drafts(response, items)

    assert len(drafts) == 2
    assert "First tweet" in drafts[0].text
    assert "Second tweet" in drafts[1].text
    assert drafts[0].source_item.title == "Item 1"


def test_parse_drafts_extra_blocks_ignored():
    config = DrafterConfig()
    style = StyleConfig(persona="", guidelines=[], examples=[])
    drafter = Drafter(config, style)

    items = [TrendingItem(title="Only one", url="https://example.com", source="hn")]
    response = "Tweet one\n---\nExtra tweet\n---\nAnother extra"
    drafts = drafter._parse_drafts(response, items)

    assert len(drafts) == 1


def test_build_system_prompt_includes_style():
    config = DrafterConfig()
    style = StyleConfig(
        persona="You are witty",
        guidelines=["Be concise", "No hashtags"],
        examples=["Example tweet here"],
    )
    drafter = Drafter(config, style)
    prompt = drafter._build_system_prompt()

    assert "You are witty" in prompt
    assert "Be concise" in prompt
    assert "Example tweet here" in prompt
