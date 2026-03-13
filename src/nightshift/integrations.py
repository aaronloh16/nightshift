"""Composio client singleton for GitHub, Reddit, and Telegram integrations."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from composio import Composio


@lru_cache(maxsize=1)
def get_composio_client() -> Composio:
    """Return a shared Composio client (reads COMPOSIO_API_KEY from env)."""
    return Composio()


def execute_action(action: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute a Composio action and return the result."""
    client = get_composio_client()
    result = client.tools.execute(
        action=action,
        arguments=arguments,
        entity_id="nightshift",
    )
    return result
