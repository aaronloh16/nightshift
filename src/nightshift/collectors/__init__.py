"""Content collectors for trending topics."""

from nightshift.collectors.base import Collector
from nightshift.collectors.github import GitHubCollector
from nightshift.collectors.hackernews import HackerNewsCollector
from nightshift.collectors.reddit import RedditCollector

__all__ = ["Collector", "GitHubCollector", "HackerNewsCollector", "RedditCollector"]
