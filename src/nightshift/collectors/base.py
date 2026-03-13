"""Base collector protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from nightshift.models import TrendingItem


@runtime_checkable
class Collector(Protocol):
    """Interface that all collectors must implement."""

    source_name: str

    async def collect(self) -> list[TrendingItem]: ...
