# Tutorial 1.4 — A Minimal Working Agent

## What you'll learn

The first tutorial with a **real external tool**: Tavily web search.
Everything from 1.1–1.3 comes together:

- The agent loop (Tutorial 1.2)
- The tool protocol (Tutorial 1.3)
- A real search tool instead of stubs

## Requirements

Both API keys must be set in `.env`:

```
ANTHROPIC_API_KEY=...
TAVILY_API_KEY=...        # free tier at app.tavily.com
```

## Run it

```bash
# Default question
uv run python main.py

# Custom question
uv run python main.py "What are the latest developments in quantum computing?"
```

## What's intentionally missing

This agent is minimal by design. Tutorial 1.5 (mini-capstone) adds:
- Citation formatting
- A proper CLI with `--question` flag
- Output saved to a file

## Next

Tutorial 1.5 ties M1 together into a complete research Q&A tool.
