"""Tests for configuration loading."""

from pathlib import Path

from nightshift.config import Settings, StyleConfig, load_settings, load_style

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def test_load_settings():
    settings = load_settings(CONFIG_DIR / "settings.yaml")
    assert settings.collectors.hackernews.enabled is True
    assert settings.collectors.hackernews.top_n == 10
    assert settings.brief_builder.model == "claude-sonnet-4-6"


def test_load_style():
    style = load_style(CONFIG_DIR / "style.yaml")
    assert len(style.interests) > 0
    assert len(style.angle_types) > 0
    assert len(style.voice_notes) > 0


def test_settings_defaults():
    settings = Settings()
    assert settings.collectors.hackernews.enabled is True
    assert settings.collectors.github.enabled is False
    assert settings.delivery.enabled is False
