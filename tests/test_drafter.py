"""Tests for the brief builder."""

import json

from nightshift.brief_builder import BriefBuilder
from nightshift.config import BriefBuilderConfig, StyleConfig
from nightshift.models import TrendingItem, XSearchResult


def test_parse_brief_valid_json():
    config = BriefBuilderConfig()
    style = StyleConfig(
        voice_notes="Test voice",
        interests=["AI"],
        angle_types=["hot take"],
    )
    builder = BriefBuilder(config, style)

    response = json.dumps([
        {
            "category": "Big Releases",
            "headline": "Test release",
            "context": "Some context here.",
            "sources": ["https://example.com"],
            "tweet_ideas": ["react to this"],
        }
    ])
    brief = builder._parse_brief(response)

    assert len(brief.sections) == 1
    assert brief.sections[0].category == "Big Releases"
    assert brief.sections[0].headline == "Test release"


def test_parse_brief_with_code_fences():
    config = BriefBuilderConfig()
    style = StyleConfig(voice_notes="", interests=[], angle_types=[])
    builder = BriefBuilder(config, style)

    response = '```json\n[{"category": "Cool Projects", "headline": "Test", "context": "ctx", "sources": [], "tweet_ideas": []}]\n```'
    brief = builder._parse_brief(response)

    assert len(brief.sections) == 1
    assert brief.sections[0].category == "Cool Projects"


def test_parse_brief_invalid_json():
    config = BriefBuilderConfig()
    style = StyleConfig(voice_notes="", interests=[], angle_types=[])
    builder = BriefBuilder(config, style)

    brief = builder._parse_brief("not valid json at all")
    assert len(brief.sections) == 0


def test_build_system_prompt_includes_style():
    config = BriefBuilderConfig()
    style = StyleConfig(
        voice_notes="lowercase energy",
        interests=["vibecoding", "dev tools"],
        angle_types=["hot take", "signal boost"],
    )
    builder = BriefBuilder(config, style)
    prompt = builder._build_system_prompt()

    assert "lowercase energy" in prompt
    assert "vibecoding" in prompt
    assert "hot take" in prompt


def test_build_user_prompt_includes_sources():
    config = BriefBuilderConfig()
    style = StyleConfig(voice_notes="", interests=[], angle_types=[])
    builder = BriefBuilder(config, style)

    items = [
        TrendingItem(title="Test Item", url="https://example.com", source="hackernews", score=100),
    ]
    x_results = [
        XSearchResult(category="AI", query_name="test query", summary="Some summary"),
    ]

    prompt = builder._build_user_prompt(items, x_results)

    assert "Test Item" in prompt
    assert "https://example.com" in prompt
    assert "Some summary" in prompt
