"""Configuration loader — merges settings.yaml + .env secrets."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Resolve project root (two levels up from this file → src/nightshift/ → project root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_DIR = _PROJECT_ROOT / "config"

load_dotenv(_PROJECT_ROOT / ".env")


# --- Sub-models ---


class HackerNewsConfig(BaseModel):
    enabled: bool = True
    top_n: int = 10
    min_score: int = 50


class GitHubConfig(BaseModel):
    enabled: bool = False
    topics: list[str] = Field(default_factory=lambda: ["artificial-intelligence", "llm"])
    created_within_days: int = 7
    min_stars: int = 50
    top_n: int = 10


class RedditConfig(BaseModel):
    enabled: bool = False
    subreddits: list[str] = Field(
        default_factory=lambda: ["LocalLLaMA", "MachineLearning"]
    )
    top_n: int = 5
    time_filter: str = "day"


class CollectorsConfig(BaseModel):
    hackernews: HackerNewsConfig = Field(default_factory=HackerNewsConfig)
    github: GitHubConfig = Field(default_factory=GitHubConfig)
    reddit: RedditConfig = Field(default_factory=RedditConfig)


class DrafterConfig(BaseModel):
    model: str = "claude-sonnet-4-6"
    max_tweets: int = 8
    max_tweet_length: int = 280


class DeliveryConfig(BaseModel):
    enabled: bool = False
    telegram_chat_id: str = ""


class Settings(BaseModel):
    collectors: CollectorsConfig = Field(default_factory=CollectorsConfig)
    drafter: DrafterConfig = Field(default_factory=DrafterConfig)
    delivery: DeliveryConfig = Field(default_factory=DeliveryConfig)


class StyleConfig(BaseModel):
    persona: str = ""
    guidelines: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)


# --- Loaders ---


def _resolve_env_vars(data: Any) -> Any:
    """Replace ${VAR} placeholders with environment variable values."""
    if isinstance(data, str) and data.startswith("${") and data.endswith("}"):
        var_name = data[2:-1]
        return os.environ.get(var_name, "")
    if isinstance(data, dict):
        return {k: _resolve_env_vars(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_resolve_env_vars(v) for v in data]
    return data


def load_settings(path: Path | None = None) -> Settings:
    path = path or _CONFIG_DIR / "settings.yaml"
    with open(path) as f:
        raw = yaml.safe_load(f)
    resolved = _resolve_env_vars(raw)
    return Settings.model_validate(resolved)


def load_style(path: Path | None = None) -> StyleConfig:
    path = path or _CONFIG_DIR / "style.yaml"
    with open(path) as f:
        raw = yaml.safe_load(f)
    return StyleConfig.model_validate(raw)
