"""
Tutorial 1.5 — Mini-capstone: Cited Research Q&A

This capstone ties together all of Module 1:
  1.1  Plain LLM calls cannot answer current-events questions
  1.2  Agents use a Perceive → Think → Act → Observe loop
  1.3  Tools follow a Define → Detect → Dispatch → Return protocol
  1.4  Tavily gives the agent real web access

What this adds beyond 1.4:
  • Citation tracking — every source the agent searched is recorded
  • Structured output — answer + cited sources printed cleanly
  • --question CLI flag
  • Optional --save flag to write results to a Markdown file

Usage:
    uv run python main.py
    uv run python main.py --question "Who won the last F1 championship?"
    uv run python main.py --question "..." --save output.md
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

MODEL = "claude-sonnet-4-6"
MAX_ITER = 10

SYSTEM_PROMPT = """You are a research assistant that answers questions using
current web sources. Always search before answering. In your final answer,
reference the sources you consulted by their titles."""

SEARCH_TOOL: anthropic.types.ToolParam = {
    "name": "search",
    "description": "Search the web for current information on a topic.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query"},
        },
        "required": ["query"],
    },
}


@dataclass
class Source:
    title: str
    url: str
    query: str


@dataclass
class ResearchResult:
    question: str
    answer: str = ""
    sources: list[Source] = field(default_factory=list)
    iterations: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


def search(tavily: TavilyClient, query: str) -> tuple[str, list[Source]]:
    """Returns (formatted_text, sources_found)."""
    print(f"  [search] {query}")
    results = tavily.search(query=query, max_results=3)
    sources: list[Source] = []
    formatted: list[str] = []

    for r in results.get("results", []):
        sources.append(Source(title=r["title"], url=r["url"], query=query))
        formatted.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content']}"
        )

    text = "\n---\n".join(formatted) if formatted else "No results found."
    return text, sources


def run_agent(question: str) -> ResearchResult:
    _check_env()
    client = anthropic.Anthropic()
    tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

    result = ResearchResult(question=question)
    messages: list[anthropic.types.MessageParam] = [
        {"role": "user", "content": question}
    ]

    for iteration in range(1, MAX_ITER + 1):
        result.iterations = iteration
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
                    result.answer = block.text
            return result

        if response.stop_reason != "tool_use":
            break

        messages.append({"role": "assistant", "content": response.content})

        tool_results: list[anthropic.types.ToolResultBlockParam] = []
        for block in response.content:
            if block.type == "tool_use":
                text, sources = search(tavily, block.input["query"])  # type: ignore[index]
                result.sources.extend(sources)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": text,
                })

        messages.append({"role": "user", "content": tool_results})

    return result


def format_output(result: ResearchResult) -> str:
    lines = [
        f"# Research Result",
        f"**Question**: {result.question}",
        f"**Date**: {result.timestamp}",
        f"**Iterations**: {result.iterations}",
        "",
        "## Answer",
        result.answer,
        "",
        "## Sources Consulted",
    ]
    seen: set[str] = set()
    for s in result.sources:
        if s.url not in seen:
            seen.add(s.url)
            lines.append(f"- [{s.title}]({s.url})")
    return "\n".join(lines)


def _check_env() -> None:
    missing = [k for k in ("ANTHROPIC_API_KEY", "TAVILY_API_KEY") if not os.getenv(k)]
    if missing:
        print(f"Error: missing environment variables: {', '.join(missing)}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Research Q&A agent with citations")
    parser.add_argument(
        "--question", "-q",
        default="What are the most significant AI research developments from the past week?",
        help="The research question to answer",
    )
    parser.add_argument(
        "--save", "-s",
        metavar="FILE",
        help="Save the result as Markdown to this file",
    )
    args = parser.parse_args()

    print("=" * 70)
    print("RESEARCH AGENT — Module 1 Capstone")
    print("=" * 70)
    print(f"\nQuestion: {args.question}\n")

    result = run_agent(args.question)
    output = format_output(result)

    print("\n" + "=" * 70)
    print(output)

    if args.save:
        Path(args.save).write_text(output)
        print(f"\nSaved to {args.save}")


if __name__ == "__main__":
    main()
