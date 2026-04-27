"""
Tutorial 1.2 — The Agent Loop

Every agent — regardless of framework — is a while loop with four steps:

    Perceive  → what is the current state of the world / conversation?
    Think     → ask the LLM what to do next
    Act       → execute whatever the LLM decided (call a tool, or stop)
    Observe   → add the result back to the conversation and repeat

This tutorial makes that loop explicit. The tool is a stub that returns
canned results so you can focus on the loop mechanics without needing
any API keys beyond Anthropic.

The loop has two stop conditions — learn to recognise both:
  1. stop_reason == "end_turn"  — the model decided it has a good answer
  2. iteration >= MAX_ITER      — safety ceiling so the loop can't run forever
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"
MAX_ITER = 10

# ---------------------------------------------------------------------------
# Stub tool — returns canned results so the loop runs without Tavily
# ---------------------------------------------------------------------------

STUB_RESULTS: dict[str, str] = {
    "default": (
        "Result: Recent research shows transformer models continue to dominate "
        "NLP benchmarks. Three papers from the past week discuss efficiency "
        "improvements via sparse attention and mixture-of-experts architectures."
    ),
}

SEARCH_TOOL: anthropic.types.ToolParam = {
    "name": "search",
    "description": "Search the web for recent information on a topic.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query"},
        },
        "required": ["query"],
    },
}


def stub_search(query: str) -> str:
    """Pretend to search; returns a canned answer."""
    return STUB_RESULTS.get(query, STUB_RESULTS["default"])


# ---------------------------------------------------------------------------
# The loop
# ---------------------------------------------------------------------------

@dataclass
class AgentRun:
    question: str
    messages: list[anthropic.types.MessageParam] = field(default_factory=list)
    iterations: int = 0
    final_answer: str = ""


def run_agent(question: str) -> AgentRun:
    client = anthropic.Anthropic()
    run = AgentRun(question=question)
    run.messages.append({"role": "user", "content": question})

    print(f"\nQuestion: {question}\n")

    while run.iterations < MAX_ITER:
        run.iterations += 1
        print(f"--- Iteration {run.iterations} ---")

        # THINK: ask the model what to do next
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=[SEARCH_TOOL],
            messages=run.messages,
        )

        print(f"stop_reason: {response.stop_reason}")

        # ACT + OBSERVE: handle what the model decided
        if response.stop_reason == "end_turn":
            # Model has a final answer — extract it and stop
            for block in response.content:
                if hasattr(block, "text"):
                    run.final_answer = block.text
            print(f"\nFinal answer:\n{run.final_answer}")
            break

        if response.stop_reason == "tool_use":
            # Model wants to call a tool — execute it and feed result back
            run.messages.append({"role": "assistant", "content": response.content})

            tool_results: list[anthropic.types.ToolResultBlockParam] = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"Tool call: {block.name}({block.input})")
                    result = stub_search(block.input.get("query", ""))  # type: ignore[arg-type]
                    print(f"Tool result: {result[:80]}...")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            # OBSERVE: add tool results so the model can reason over them
            run.messages.append({"role": "user", "content": tool_results})

    else:
        print(f"\nStopped: reached MAX_ITER={MAX_ITER}")

    return run


def main() -> None:
    print("=" * 70)
    print("THE AGENT LOOP — Perceive → Think → Act → Observe")
    print("=" * 70)

    run = run_agent("What are the latest breakthroughs in AI research this week?")

    print(f"\nCompleted in {run.iterations} iteration(s).")
    print("""
WHAT JUST HAPPENED
------------------
Each iteration of the while loop:

  Perceive  — run.messages contains the full conversation so far
  Think     — client.messages.create(...) returns the model's next move
  Act       — we called stub_search() when stop_reason == "tool_use"
  Observe   — we appended the tool result so the model can see it next turn

Two stop conditions fired:
  • stop_reason == "end_turn"  → model decided it had enough information
  • iteration >= MAX_ITER      → safety ceiling (didn't fire this run)

Every agent framework (LangGraph, LangChain, AutoGen) is a more
sophisticated version of exactly this loop.
""")


if __name__ == "__main__":
    main()
