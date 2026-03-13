"""Content collectors for trending topics."""

from nightshift.collectors.base import Collector
from nightshift.collectors.github import GitHubCollector
from nightshift.collectors.gmail import GmailCollector
from nightshift.collectors.hackernews import HackerNewsCollector
from nightshift.collectors.reddit import RedditCollector
from nightshift.collectors.rss import RSSCollector
from nightshift.collectors.smart import SmartCollector
from nightshift.collectors.x_profile import XProfileCollector
from nightshift.collectors.xsearch import XSearchCollector

__all__ = [
    "Collector",
    "GitHubCollector",
    "GmailCollector",
    "HackerNewsCollector",
    "RedditCollector",
    "RSSCollector",
    "SmartCollector",
    "XProfileCollector",
    "XSearchCollector",
]
