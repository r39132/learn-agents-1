# Tutorial 1.5 — Mini-capstone: Cited Research Q&A

## What this builds

A complete research agent that:
1. Accepts a natural-language question
2. Searches the web (Tavily) for current information
3. Returns a cited answer in Markdown

This ties together everything in Module 1.

## What's new vs. Tutorial 1.4

| Feature | 1.4 | 1.5 |
|---------|-----|-----|
| Citation tracking | No | Yes — sources deduplicated |
| Structured output | Raw text | Markdown with answer + sources |
| CLI | `sys.argv[1]` | `--question` / `--save` flags |
| Save to file | No | `--save output.md` |

## Run it

```bash
# Default question
uv run python main.py

# Custom question
uv run python main.py --question "What is the current state of fusion energy research?"

# Save output to file
uv run python main.py --question "..." --save result.md
```

## Module 1 — What you've built

Starting from a plain LLM call that hallucinated, you now have an agent that:

- Runs a `while` loop (Tutorial 1.2)
- Calls real tools via the Anthropic protocol (Tutorial 1.3)
- Fetches live web results via Tavily (Tutorial 1.4)
- Tracks citations and formats structured output (this tutorial)

## Next: Module 2

Module 2 goes deeper on tool design: error handling, side-effecting tools,
parallel tool calls, and tools that require human approval.
