# Tutorial 1.3 — Tool Use Basics

## What you'll learn

The Anthropic tool-use protocol, broken into four explicit steps:

```
DEFINE   → attach tool schemas to the API call
DETECT   → check stop_reason == "tool_use"
DISPATCH → call the right function for each tool_use block
RETURN   → send tool_result blocks back to the model
```

## Two tools

| Tool | What it does |
|------|-------------|
| `search(query)` | Stub web search (becomes real Tavily in Tutorial 1.4) |
| `get_date()` | Returns today's date — real, uses Python `datetime` |

Using two tools together shows how to dispatch from a single response
that may contain multiple tool calls.

## Key invariants

- Every `tool_use` block needs **exactly one** matching `tool_result`
- Append the **assistant message first**, then the **tool_result user message**
- A single response can contain **multiple** `tool_use` blocks — process all before continuing

## Run it

```bash
uv run python main.py
```

## Next

Tutorial 1.4 replaces the stub search with real **Tavily** and assembles
a minimal end-to-end research agent.
