"""
Tutorial 1.3 — Tool Use Basics

Tool use is how agents interact with the world outside the model.
This tutorial dissects the Anthropic tool-use protocol step by step.

The protocol has four parts:
  1. DEFINE   — describe tools as JSON schemas in the API call
  2. DETECT   — check stop_reason == "tool_use" in the response
  3. DISPATCH — find tool_use blocks, call the matching function
  4. RETURN   — send tool_result blocks back so the model can continue

We use two stub tools (no external API keys needed):
  • search(query)      — finds web results (stubbed)
  • get_date()         — returns today's date (real: uses Python datetime)

Studying two tools together shows how to dispatch to different handlers
from a single response that may contain multiple tool calls.
"""

from __future__ import annotations

import json
from datetime import date
from typing import Any

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"

# ---------------------------------------------------------------------------
# Tool definitions — these are the JSON schemas sent to the API
# ---------------------------------------------------------------------------

TOOLS: list[anthropic.types.ToolParam] = [
    {
        "name": "search",
        "description": (
            "Search the web for information on a topic. "
            "Use this when you need current or factual information."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query string",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_date",
        "description": "Returns today's date in ISO format (YYYY-MM-DD).",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]

# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def search(query: str) -> str:
    """Stub: in Tutorial 1.4 this becomes a real Tavily call."""
    return (
        f"[stub results for '{query}']: "
        "Three relevant articles found discussing recent developments. "
        "Researchers at major labs published findings on efficiency and scale."
    )


def get_date() -> str:
    return date.today().isoformat()


def dispatch_tool(name: str, tool_input: dict[str, Any]) -> str:
    """Route a tool call to the right function."""
    if name == "search":
        return search(tool_input["query"])
    if name == "get_date":
        return get_date()
    raise ValueError(f"Unknown tool: {name}")


# ---------------------------------------------------------------------------
# The protocol, one step at a time
# ---------------------------------------------------------------------------

def run_with_tools(question: str) -> str:
    client = anthropic.Anthropic()
    messages: list[anthropic.types.MessageParam] = [
        {"role": "user", "content": question}
    ]

    print(f"\nQuestion: {question}\n")

    while True:
        # STEP 1: DEFINE — pass tool schemas to the API
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        print(f"stop_reason: {response.stop_reason}")
        print(f"content blocks: {[b.type for b in response.content]}")

        # STEP 2: DETECT — did the model want to call tools?
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""

        if response.stop_reason != "tool_use":
            break

        # The assistant message must be added before we add tool results
        messages.append({"role": "assistant", "content": response.content})

        # STEP 3: DISPATCH — find every tool_use block and call it
        tool_results: list[anthropic.types.ToolResultBlockParam] = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            print(f"\n  Tool called : {block.name}")
            print(f"  Input       : {json.dumps(block.input, indent=2)}")

            result = dispatch_tool(block.name, block.input)  # type: ignore[arg-type]
            print(f"  Result      : {result[:100]}...")

            # STEP 4: RETURN — wrap results in tool_result blocks
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})

    return ""


def main() -> None:
    print("=" * 70)
    print("TOOL USE BASICS — Define → Detect → Dispatch → Return")
    print("=" * 70)

    answer = run_with_tools(
        "What is today's date, and what are the latest developments in AI research?"
    )

    print(f"\nFinal answer:\n{answer}")

    print("""
THE PROTOCOL IN SUMMARY
-----------------------
DEFINE   tools=[TOOLS]           Attach schemas to every API call.
DETECT   stop_reason=="tool_use" Model signalled it wants to act.
DISPATCH dispatch_tool(name, ...) Your code decides what to run.
RETURN   tool_result blocks       Feed results back as a user turn.

Key invariants:
  • Every tool_use block needs exactly one matching tool_result.
  • The assistant message (with tool_use blocks) must be appended
    BEFORE the user message (with tool_results).
  • A single response can contain multiple tool_use blocks —
    process all of them before continuing.
""")


if __name__ == "__main__":
    main()
