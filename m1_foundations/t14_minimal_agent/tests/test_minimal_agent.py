"""Tests for Tutorial 1.4 — minimal agent with real Tavily (mocked in tests)."""

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch


def load_module():  # type: ignore[no-untyped-def]
    path = Path(__file__).parent.parent / "main.py"
    spec = importlib.util.spec_from_file_location("t14_main", path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _make_tool_use_block(tool_id: str, query: str) -> MagicMock:
    block = MagicMock()
    block.type = "tool_use"
    block.id = tool_id
    block.name = "search"
    block.input = {"query": query}
    return block


def _make_end_turn_block(text: str) -> MagicMock:
    block = MagicMock()
    block.type = "text"
    block.text = text
    return block


def test_agent_returns_string_answer() -> None:
    t14 = load_module()

    text_block = _make_end_turn_block("Here are recent AI developments.")
    end_response = MagicMock()
    end_response.stop_reason = "end_turn"
    end_response.content = [text_block]

    with patch.object(t14.anthropic, "Anthropic") as MockAnthropicClient, \
         patch.object(t14, "TavilyClient"), \
         patch.dict("os.environ", {"ANTHROPIC_API_KEY": "x", "TAVILY_API_KEY": "y"}):
        MockAnthropicClient.return_value.messages.create.return_value = end_response
        result = t14.run_agent("What is new in AI?")

    assert isinstance(result, str)
    assert len(result) > 0


def test_agent_calls_search_tool() -> None:
    t14 = load_module()

    tool_block = _make_tool_use_block("id_1", "AI research 2025")
    tool_response = MagicMock()
    tool_response.stop_reason = "tool_use"
    tool_response.content = [tool_block]

    text_block = _make_end_turn_block("Based on search results...")
    end_response = MagicMock()
    end_response.stop_reason = "end_turn"
    end_response.content = [text_block]

    mock_tavily = MagicMock()
    mock_tavily.search.return_value = {
        "results": [{"title": "AI News", "url": "https://example.com", "content": "..."}]
    }

    with patch.object(t14.anthropic, "Anthropic") as MockAnthropicClient, \
         patch.object(t14, "TavilyClient", return_value=mock_tavily), \
         patch.dict("os.environ", {"ANTHROPIC_API_KEY": "x", "TAVILY_API_KEY": "y"}):
        MockAnthropicClient.return_value.messages.create.side_effect = [
            tool_response, end_response,
        ]
        result = t14.run_agent("What is new in AI?")

    mock_tavily.search.assert_called_once()
    assert isinstance(result, str)


def test_search_formats_results() -> None:
    t14 = load_module()

    mock_tavily = MagicMock()
    mock_tavily.search.return_value = {
        "results": [
            {"title": "Paper A", "url": "https://a.com", "content": "Summary A"},
            {"title": "Paper B", "url": "https://b.com", "content": "Summary B"},
        ]
    }
    result = t14.search(mock_tavily, "AI research")
    assert "Paper A" in result
    assert "https://a.com" in result
    assert "Summary A" in result


def test_search_handles_empty_results() -> None:
    t14 = load_module()

    mock_tavily = MagicMock()
    mock_tavily.search.return_value = {"results": []}
    result = t14.search(mock_tavily, "obscure topic")
    assert result == "No results found."
