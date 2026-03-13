"""Tests for configuration loading."""

from pathlib import Path

from nightshift.config import Settings, StyleConfig, load_settings, load_style

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def test_load_settings():
    settings = load_settings(CONFIG_DIR / "settings.yaml")
    assert settings.collectors.hackernews.enabled is True
    assert settings.collectors.hackernews.top_n == 10
    assert settings.drafter.model == "claude-sonnet-4-6"


def test_load_style():
    style = load_style(CONFIG_DIR / "style.yaml")
    assert len(style.examples) > 0
    assert len(style.guidelines) > 0
    assert "persona" in style.persona.lower() or len(style.persona) > 0


def test_settings_defaults():
    settings = Settings()
    assert settings.collectors.hackernews.enabled is True
    assert settings.collectors.github.enabled is False
    assert settings.delivery.enabled is False
