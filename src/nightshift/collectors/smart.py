"""Smart collector — Grok agent with Composio Gmail + native x_search.

Reads newsletters via Composio, extracts topics, searches X via Grok's native
x_search tool, and returns a rich contextualized summary.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

from openai import OpenAI
from composio import Action, Composio

from nightshift.config import SmartCollectorConfig
from nightshift.models import XSearchResult

logger = logging.getLogger(__name__)


def _get_gmail_tool_schema() -> dict[str, Any]:
    """Fetch Gmail action schema from Composio in OpenAI function-calling format."""
    client = Composio()
    action_model = client.actions.get(action="GMAIL_FETCH_EMAILS")
    params = action_model.parameters.model_dump()

    properties = {}
    for k, v in params.get("properties", {}).items():
        if v.get("advanced"):
            continue
        prop: dict[str, Any] = {}
        if "type" in v:
            prop["type"] = v["type"]
        if "description" in v:
            prop["description"] = v["description"][:200]
        if "enum" in v:
            prop["enum"] = v["enum"]
        properties[k] = prop

    tool_params: dict[str, Any] = {
        "type": "object",
        "properties": properties,
    }
    required = params.get("required")
    if required:
        tool_params["required"] = required

    return {
        "type": "function",
        "function": {
            "name": "GMAIL_FETCH_EMAILS",
            "description": (action_model.description or "")[:300],
            "parameters": tool_params,
        },
    }


def _execute_composio_action(action_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute a Composio action and return the result."""
    client = Composio()
    entity = client.get_entity("default")
    return entity._execute(action=Action(action_name), params=arguments)


def _run_agent(
    model: str,
    prompt: str,
    tools: list[dict[str, Any]],
    max_iterations: int = 8,
) -> str:
    """Run the Grok agent loop — uses Responses API for native x_search + function calling for Gmail."""
    client = OpenAI(
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1",
    )

    # Use Responses API which supports both native x_search and function tools
    all_tools: list[dict[str, Any]] = [
        {"type": "x_search"},  # Grok's native X search
    ]
    # Add Gmail as a function tool — Responses API uses a different format
    for tool in tools:
        fn = tool["function"]
        all_tools.append({
            "type": "function",
            "name": fn["name"],
            "description": fn.get("description", ""),
            "parameters": fn.get("parameters", {}),
        })

    response = client.responses.create(
        model=model,
        tools=all_tools,
        input=prompt,
    )

    # Check if there are function tool calls we need to handle
    pending_calls = [
        block for block in response.output
        if hasattr(block, "type") and block.type == "function_call"
    ]

    iteration = 0
    while pending_calls and iteration < max_iterations:
        iteration += 1

        # Build input with previous output + tool results
        input_items = [{"role": "user", "content": prompt}]
        input_items.extend(_serialize_output(response.output))

        for call in pending_calls:
            fn_name = call.name
            fn_args = json.loads(call.arguments) if isinstance(call.arguments, str) else call.arguments

            print(f"[smart] Calling {fn_name}...")

            try:
                result = _execute_composio_action(fn_name, fn_args)
                result_str = json.dumps(result, default=str)
                if len(result_str) > 15000:
                    result_str = result_str[:15000] + "...(truncated)"
            except Exception as e:
                logger.error("Tool call %s failed: %s", fn_name, e)
                result_str = json.dumps({"error": str(e)})

            input_items.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": result_str,
            })

        response = client.responses.create(
            model=model,
            tools=all_tools,
            input=input_items,
        )

        pending_calls = [
            block for block in response.output
            if hasattr(block, "type") and block.type == "function_call"
        ]

    # Extract final text
    text_parts: list[str] = []
    for block in response.output:
        if hasattr(block, "text"):
            text_parts.append(block.text)
        elif hasattr(block, "content"):
            for cb in block.content:
                if hasattr(cb, "text"):
                    text_parts.append(cb.text)

    return "\n".join(text_parts).strip()


def _serialize_output(output: Any) -> list[dict[str, Any]]:
    """Serialize response output blocks for re-submission."""
    items: list[dict[str, Any]] = []
    for block in output:
        if hasattr(block, "model_dump"):
            items.append(block.model_dump())
        elif isinstance(block, dict):
            items.append(block)
    return items


AGENT_PROMPT = """\
You are a research agent gathering overnight AI/tech intelligence for a developer's morning brief.

Your job:
1. First, use GMAIL_FETCH_EMAILS to fetch recent emails from AI newsletters (search for: {search_terms}) to see what topics they're covering.
2. Extract the key topics and stories from those newsletters.
3. Use your x_search capability to find what people on X/Twitter are saying about each of those topics — look for high-engagement tweets, hot takes, notable accounts weighing in.
4. Also search X for any other major AI/tech developments in the last {lookback_hours} hours that the newsletters might have missed.

Additional topics to search on X: {extra_queries}

For each major topic, provide:
- What happened (the news/development)
- What people on X are saying about it (specific accounts, engagement levels, consensus vs contrarian takes)
- Notable tweets or threads worth engaging with

Return your findings as a structured summary organized by topic. Include specific @handles, tweet engagement numbers, and links where possible. Focus on the most interesting, high-signal content — not everything, just what matters.
"""


class SmartCollector:
    """Grok agent with Composio Gmail + native x_search — reads newsletters, searches X, returns rich summaries."""

    source_name = "smart"

    def __init__(self, config: SmartCollectorConfig) -> None:
        self.config = config

    async def collect(self) -> list[XSearchResult]:
        """Run the smart collection agent."""
        return await asyncio.to_thread(self._collect_sync)

    def _collect_sync(self) -> list[XSearchResult]:
        """Synchronous agent execution."""
        # Get Gmail tool from Composio
        gmail_tool = _get_gmail_tool_schema()
        tools = [gmail_tool]

        extra_queries = ", ".join(
            q.prompt for q in self.config.extra_queries
        ) if self.config.extra_queries else "AI agents, vibecoding, developer tools, industry drama"

        prompt = AGENT_PROMPT.format(
            search_terms=", ".join(self.config.newsletter_search_terms),
            lookback_hours=self.config.lookback_hours,
            extra_queries=extra_queries,
        )

        print(f"[smart] Starting agent (Grok + Gmail + x_search)...")
        summary = _run_agent(
            model=self.config.model,
            prompt=prompt,
            tools=tools,
            max_iterations=self.config.max_tool_calls,
        )

        if not summary:
            print("[smart] Agent returned empty summary")
            return []

        print(f"[smart] Agent returned {len(summary)} chars of analysis")
        return [
            XSearchResult(
                category="smart_digest",
                query_name="newsletter_x_research",
                summary=summary,
            )
        ]
