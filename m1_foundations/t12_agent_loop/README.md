# Tutorial 1.2 — The Agent Loop

## What you'll learn

Every agent is a `while` loop with four steps:

```
Perceive → Think → Act → Observe → (repeat)
```

This tutorial makes that loop explicit using a stub search tool
(no Tavily key needed) so you can focus on the mechanics.

## The loop in code

```python
while iterations < MAX_ITER:
    response = client.messages.create(...)   # THINK

    if response.stop_reason == "end_turn":   # ACT: done
        extract final answer; break

    if response.stop_reason == "tool_use":   # ACT: call tool
        result = call_tool(...)
        append result to messages            # OBSERVE
```

## Stop conditions

| Condition | Meaning |
|-----------|---------|
| `stop_reason == "end_turn"` | Model decided it has a complete answer |
| `iterations >= MAX_ITER` | Safety ceiling — prevents infinite loops |

## Run it

```bash
uv run python main.py
```

## Next

Tutorial 1.3 replaces the stub tool with real Anthropic tool-use schemas
and shows how to handle multiple tool types.
