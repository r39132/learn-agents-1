# learn-agents-1: Building Agents — Learning Syllabus

## Decisions

| Question | Decision |
|----------|----------|
| Framework scope | Raw Anthropic SDK first (M1–M4), then LangGraph (M5+) |
| Module 4 depth | Re-derive memory concepts from scratch |
| Other frameworks | Anthropic SDK + LangGraph only |
| Capstone cadence | Mini-capstone at the end of each module |
| Domain | Research Assistant — ad-hoc Q&A + longitudinal topic digests |

## Domain: Research Assistant

A single agent that does two things:
- **Ad-hoc mode**: answer a natural-language question by searching the web, reading sources, and returning a cited answer
- **Digest mode**: track a topic over time — fetch what's new, diff against memory, summarize changes

**Tools**: Tavily API (web search), HTTP page fetcher  
**Memory backend**: builds up across M4 from scratch (in-memory → persistent → vector)  
**Dev stack**: Python 3.12, `pyenv` + `uv`, `ruff`, `mypy`, `pytest`, `pre-commit`

---

## Module 1 — Foundations: What Is an Agent?

**Theme**: Distinguish agents from plain LLM calls; understand the core loop.

| Tutorial | Topic | Key Concepts |
|----------|-------|--------------|
| 1.1 | Plain LLM call vs. agent | Stateless completion, why it's not an agent |
| 1.2 | The agent loop | Perceive → Think → Act → Observe cycle |
| 1.3 | Tool use basics | Anthropic function-calling API, tool schemas |
| 1.4 | A minimal working agent | Single-tool research agent with `while` loop, stop conditions |
| 1.5 | **Mini-capstone** | Agent that answers one research question end-to-end with a single search tool |

---

## Module 2 — Tool Use in Depth

**Theme**: Give the research agent real, robust capabilities.

| Tutorial | Topic | Key Concepts |
|----------|-------|--------------|
| 2.1 | Designing good tools | Schema design, idempotency, error contracts |
| 2.2 | Read-only tools | Web search (Tavily), page fetch, text extraction |
| 2.3 | Side-effecting tools | Writing research notes to disk, human-in-the-loop approval |
| 2.4 | Tool error handling | Graceful degradation, retry logic, fallback strategies |
| 2.5 | Parallel tool calls | Fetching multiple sources simultaneously |
| 2.6 | **Mini-capstone** | Multi-tool agent: searches, fetches pages, writes a cited summary to a file |

---

## Module 3 — Reasoning Patterns

**Theme**: Teach the agent how to think before and after acting.

| Tutorial | Topic | Key Concepts |
|----------|-------|--------------|
| 3.1 | ReAct (Reason + Act) | Interleaved thought/action traces |
| 3.2 | Chain-of-thought prompting | Structured scratchpad, extended thinking |
| 3.3 | Plan-and-execute | Upfront search plan, sub-query decomposition |
| 3.4 | Reflection and self-critique | Agent scores source quality before committing to answer |
| 3.5 | **Mini-capstone** | Agent that plans its searches, reflects on source credibility, and self-corrects a weak answer |

---

## Module 4 — State & Memory

**Theme**: Give the agent durable context, re-derived from scratch.

| Tutorial | Topic | Key Concepts |
|----------|-------|--------------|
| 4.1 | Conversation history management | Context window limits, summarization |
| 4.2 | Episodic memory | Storing and retrieving past research sessions |
| 4.3 | Semantic memory | Embedding + vector search for long-term recall |
| 4.4 | Working memory patterns | Scratchpad, structured state objects |
| 4.5 | Longitudinal topic tracking | Diff new findings against memory; digest mode foundation |
| 4.6 | **Mini-capstone** | Digest-mode agent: tracks a topic across multiple runs, only surfaces what's new |

---

## Module 5 — Agentic Frameworks: LangGraph

**Theme**: Re-express the research agent as a stateful graph.

| Tutorial | Topic | Key Concepts |
|----------|-------|--------------|
| 5.1 | LangGraph core concepts | Nodes, edges, state schema, `StateGraph` |
| 5.2 | Ad-hoc mode as a graph | search → read → synthesize → cite pipeline |
| 5.3 | Conditional edges | Branching on "need more sources" vs. "answer is sufficient" |
| 5.4 | Human-in-the-loop | Interrupt before publishing a digest, approve, resume |
| 5.5 | Persistence with checkpointers | `SqliteSaver` for resumable research sessions |
| 5.6 | Streaming agent output | Token streaming, intermediate state to a UI |
| 5.7 | **Mini-capstone** | Full research agent in LangGraph supporting both ad-hoc and digest modes with checkpointing |

---

## Module 6 — Multi-Agent Systems

**Theme**: Compose agents that coordinate, delegate, and check each other.

| Tutorial | Topic | Key Concepts |
|----------|-------|--------------|
| 6.1 | Orchestrator + subagents | Dispatcher routes subtopics to specialist searchers |
| 6.2 | Parallel subagents | Fan-out one subagent per subtopic, aggregate results |
| 6.3 | Agent as a tool | Wrap the ad-hoc agent as a tool for the digest orchestrator |
| 6.4 | Supervisor pattern | Quality-control agent reviews and challenges subagent findings |
| 6.5 | Shared state across agents | Shared knowledge base, conflict resolution |
| 6.6 | **Mini-capstone** | Multi-agent research system: orchestrator fans out to parallel searchers, supervisor merges and fact-checks the digest |

---

## Module 7 — Evaluation & Testing

**Theme**: Know whether the agent actually works.

| Tutorial | Topic | Key Concepts |
|----------|-------|--------------|
| 7.1 | Unit-testing tools | Mocking LLM responses, deterministic tool tests |
| 7.2 | Trace-based testing | Recording and replaying agent runs |
| 7.3 | Citation grounding tests | Verify ad-hoc answers cite real, fetched sources |
| 7.4 | Diff correctness tests | Verify digest mode only surfaces genuinely new findings |
| 7.5 | LLM-as-judge | Model scores answer accuracy, completeness, and citation quality |
| 7.6 | **Mini-capstone** | Full test suite for both agent modes with grounding checks and LLM-as-judge scoring |

---

## Module 8 — Production Concerns

**Theme**: Move from prototype to something you'd run in production.

| Tutorial | Topic | Key Concepts |
|----------|-------|--------------|
| 8.1 | Observability & tracing | Structured logs, span tracing (LangSmith / OpenTelemetry) |
| 8.2 | Cost & latency management | Token budgets, Anthropic prompt caching |
| 8.3 | Safety & guardrails | Input validation, output filtering, low-confidence flagging |
| 8.4 | Deployment patterns | FastAPI wrapper serving both agent modes, async execution |
| 8.5 | **Mini-capstone** | Production-ready research API: both modes, streaming, cost tracking, guardrails, traced |

---

## Suggested Learning Path

```
M1 → M2 → M3 → M4 → M5 → M6 → M7 → M8
```

Each tutorial is a self-contained Python project with:
- Runnable `main.py` / CLI entry point
- `tests/` with `pytest`
- `pyproject.toml` (`uv`-managed), `ruff`, `mypy` configured
- `.pre-commit-config.yaml`
- Short `README.md` explaining the concept and how to run
