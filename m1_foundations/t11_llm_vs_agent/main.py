"""
Tutorial 1.1 — Plain LLM call vs. agent

A plain LLM call is stateless: it has no tools, no loop, no ability to look
things up. It can only reason over what it already knows from training.

For research questions this creates two failure modes:
  1. Honest refusal — the model says it doesn't know (unhelpful).
  2. Hallucination — the model invents plausible-sounding but wrong facts.

Run this to see both failure modes, then read the explanation at the end.
"""

import os

import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-6"

QUESTIONS = [
    # Knowledge-cutoff question — model cannot know this
    "What are the three most-cited AI research papers published in the last 7 days?",
    # Real-time fact — changes constantly
    "What is the current price of NVIDIA stock and how has it moved this week?",
]


def plain_llm_call(client: anthropic.Anthropic, question: str) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": question}],
    )
    return response.content[0].text  # type: ignore[union-attr]


def main() -> None:
    client = anthropic.Anthropic()

    print("=" * 70)
    print("PLAIN LLM CALL — no tools, no loop, no real-world access")
    print("=" * 70)

    for i, question in enumerate(QUESTIONS, 1):
        print(f"\n[Question {i}] {question}\n")
        answer = plain_llm_call(client, question)
        print(f"[Answer]\n{answer}")
        print("-" * 70)

    print("""
WHY THIS IS NOT AN AGENT
------------------------
A plain LLM call has three fundamental limits for research tasks:

1. Knowledge cutoff — training data ends at a fixed date.
   Current events, recent papers, live prices: all invisible.

2. No grounding — when the model doesn't know, it has two options:
   say "I don't know" (honest but useless) or generate confident-sounding
   text that may be completely fabricated.

3. No iteration — a single call produces one response. If the answer is
   wrong or incomplete there is no mechanism to try again or fetch more.

An agent fixes all three by adding:
  • Tools  — actions the model can take (search, fetch, calculate)
  • A loop — the model acts, observes results, decides what to do next
  • State  — memory of what has been done so far

Tutorial 1.2 introduces the loop. Tutorial 1.3 adds tools.
""")


if __name__ == "__main__":
    main()
