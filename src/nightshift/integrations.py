"""Composio client singleton for GitHub, Reddit, Gmail, and Telegram integrations."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from composio import Action, Composio


@lru_cache(maxsize=1)
def get_composio_client() -> Composio:
    """Return a shared Composio client (reads COMPOSIO_API_KEY from env)."""
    return Composio()


def execute_action(action: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute a Composio action and return the result."""
    client = get_composio_client()
    entity = client.get_entity("default")
    result = entity._execute(
        action=Action(action),
        params=arguments,
    )
    return result
