"""Tests for Tutorial 1.3 — tool use protocol."""

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def load_module():  # type: ignore[no-untyped-def]
    path = Path(__file__).parent.parent / "main.py"
    spec = importlib.util.spec_from_file_location("t13_main", path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def test_get_date_returns_iso_string() -> None:
    t13 = load_module()
    result = t13.get_date()
    assert len(result) == 10
    assert result[4] == "-" and result[7] == "-"


def test_search_returns_string() -> None:
    t13 = load_module()
    result = t13.search("AI research 2024")
    assert isinstance(result, str)
    assert len(result) > 0


def test_dispatch_tool_search() -> None:
    t13 = load_module()
    result = t13.dispatch_tool("search", {"query": "test query"})
    assert isinstance(result, str)


def test_dispatch_tool_get_date() -> None:
    t13 = load_module()
    result = t13.dispatch_tool("get_date", {})
    assert len(result) == 10


def test_dispatch_tool_unknown_raises() -> None:
    t13 = load_module()
    with pytest.raises(ValueError, match="Unknown tool"):
        t13.dispatch_tool("nonexistent_tool", {})


def _make_tool_use_block(tool_id: str, name: str, input_data: dict) -> MagicMock:
    block = MagicMock()
    block.type = "tool_use"
    block.id = tool_id
    block.name = name
    block.input = input_data
    return block


def _make_end_turn_block(text: str) -> MagicMock:
    block = MagicMock()
    block.type = "text"
    block.text = text
    return block


def test_run_with_tools_end_to_end() -> None:
    t13 = load_module()

    tool_block = _make_tool_use_block("id_1", "get_date", {})
    tool_response = MagicMock()
    tool_response.stop_reason = "tool_use"
    tool_response.content = [tool_block]

    text_block = _make_end_turn_block("Today is 2025-01-01.")
    end_response = MagicMock()
    end_response.stop_reason = "end_turn"
    end_response.content = [text_block]

    with patch.object(t13.anthropic, "Anthropic") as MockClient:
        MockClient.return_value.messages.create.side_effect = [tool_response, end_response]
        result = t13.run_with_tools("What is today's date?")

    assert isinstance(result, str)


def test_tool_results_include_all_tool_uses() -> None:
    """Every tool_use block must produce exactly one tool_result."""
    t13 = load_module()

    block1 = _make_tool_use_block("id_1", "get_date", {})
    block2 = _make_tool_use_block("id_2", "search", {"query": "AI news"})
    tool_response = MagicMock()
    tool_response.stop_reason = "tool_use"
    tool_response.content = [block1, block2]

    text_block = _make_end_turn_block("Here is the answer.")
    end_response = MagicMock()
    end_response.stop_reason = "end_turn"
    end_response.content = [text_block]

    captured_messages: list = []

    def capture_create(**kwargs):  # type: ignore[no-untyped-def]
        captured_messages.extend(kwargs.get("messages", []))
        if len(captured_messages) < 4:
            return tool_response
        return end_response

    with patch.object(t13.anthropic, "Anthropic") as MockClient:
        MockClient.return_value.messages.create.side_effect = capture_create
        t13.run_with_tools("What is today and what is new in AI?")

    tool_result_messages = [
        m for m in captured_messages
        if m.get("role") == "user"
        and isinstance(m.get("content"), list)
        and any(
            isinstance(b, dict) and b.get("type") == "tool_result"
            for b in m["content"]
        )
    ]
    assert len(tool_result_messages) >= 1
    tool_results = tool_result_messages[0]["content"]
    assert len(tool_results) == 2
