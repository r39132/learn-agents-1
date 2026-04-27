# Tutorial 1.1 — Plain LLM Call vs. Agent

## What you'll learn

The difference between a plain LLM call and an agent.
A plain call is stateless — one prompt in, one response out.
An agent adds tools, a loop, and state.

## The problem

Ask a research question that requires current knowledge:

```
"What are the three most-cited AI papers published in the last 7 days?"
```

A plain LLM call will either:
- Honestly say it doesn't know (unhelpful)
- Confidently invent plausible-sounding papers (dangerous)

## Run it

```bash
uv run python main.py
```

## Key concepts

| Concept | Plain LLM | Agent |
|---------|-----------|-------|
| Tools | None | Search, fetch, calculate, ... |
| Loop | Single call | Repeats until done |
| State | None | Conversation history + memory |
| Grounding | Training data only | Real-world results |

## Next

Tutorial 1.2 introduces the agent loop structure.
