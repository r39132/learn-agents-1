# learn-agents-1

Learning to build AI agents from first principles, using the **Research Assistant** domain throughout:
an agent that answers ad-hoc questions by searching the web and tracks topics longitudinally over time.

See [SYLLABUS.md](SYLLABUS.md) for the full learning path.

## Setup

```bash
pyenv local 3.12
uv venv
uv sync --group dev
cp .env.example .env   # fill in your API keys
pre-commit install
```

## API Keys needed

| Key | Where to get it |
|-----|----------------|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com |
| `TAVILY_API_KEY` | https://app.tavily.com (free tier available) — needed from Tutorial 1.4 onward |

## Running a tutorial

Each tutorial lives in `m{N}_{module}/t{N}{M}_{name}/`. Run it with:

```bash
uv run python m1_foundations/t11_llm_vs_agent/main.py
```

Run its tests with:

```bash
uv run pytest m1_foundations/t11_llm_vs_agent/tests/
```

## Modules

| Module | Directory | Theme |
|--------|-----------|-------|
| 1 | `m1_foundations/` | What is an agent? |
| 2 | `m2_tool_use/` | Robust tool design |
| 3 | `m3_reasoning/` | Reasoning patterns |
| 4 | `m4_memory/` | State & memory |
| 5 | `m5_langgraph/` | LangGraph |
| 6 | `m6_multi_agent/` | Multi-agent systems |
| 7 | `m7_evaluation/` | Testing & eval |
| 8 | `m8_production/` | Production concerns |
