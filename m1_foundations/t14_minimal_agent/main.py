"""
Tutorial 1.4 — A Minimal Working Agent

This is the first tutorial that calls a real external tool: Tavily for web search.
Everything from 1.1–1.3 comes together here:

  • The loop from Tutorial 1.2
  • The tool protocol from Tutorial 1.3
  • A real search tool instead of stubs

The agent is intentionally minimal — one tool, one question, straightforward loop.
Tutorial 1.5 (capstone) wraps this into a proper CLI with citation output.

Requirements:
  ANTHROPIC_API_KEY and TAVILY_API_KEY must be set in your .env file.
"""

from __future__ import annotations

import os
import sys

import anthropic
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

MODEL = "claude-sonnet-4-6"
MAX_ITER = 10

SYSTEM_PROMPT = """You are a research assistant. When asked a question, use the
search tool to find current, accurate information before answering.
Always answer based on what you find — do not rely on your training data alone."""

SEARCH_TOOL: anthropic.types.ToolParam = {
    "name": "search",
    "description": (
        "Search the web for current information. "
        "Returns a list of relevant results with titles, URLs, and content snippets."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query",
            },
        },
        "required": ["query"],
    },
}


def search(tavily: TavilyClient, query: str) -> str:
    print(f"  [search] {query}")
    results = tavily.search(query=query, max_results=3)
    formatted = []
    for r in results.get("results", []):
        formatted.append(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content']}\n")
    return "\n---\n".join(formatted) if formatted else "No results found."


def run_agent(question: str) -> str:
    _check_env()
    client = anthropic.Anthropic()
    tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

    messages: list[anthropic.types.MessageParam] = [
        {"role": "user", "content": question}
    ]

    for iteration in range(1, MAX_ITER + 1):
        print(f"\n--- Iteration {iteration} ---")

        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=[SEARCH_TOOL],
            messages=messages,
        )

        print(f"stop_reason: {response.stop_reason}")

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""

        if response.stop_reason != "tool_use":
            break

        messages.append({"role": "assistant", "content": response.content})

        tool_results: list[anthropic.types.ToolResultBlockParam] = []
        for block in response.content:
            if block.type == "tool_use":
                result = search(tavily, block.input["query"])  # type: ignore[index]
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        messages.append({"role": "user", "content": tool_results})

    return ""


def _check_env() -> None:
    missing = [k for k in ("ANTHROPIC_API_KEY", "TAVILY_API_KEY") if not os.getenv(k)]
    if missing:
        print(f"Error: missing environment variables: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in your API keys.")
        sys.exit(1)


def main() -> None:
    question = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "What are the most significant AI research developments from the past week?"
    )

    print("=" * 70)
    print("MINIMAL RESEARCH AGENT")
    print("=" * 70)
    print(f"\nQuestion: {question}\n")

    answer = run_agent(question)

    print("\n" + "=" * 70)
    print("ANSWER")
    print("=" * 70)
    print(answer)


if __name__ == "__main__":
    main()
