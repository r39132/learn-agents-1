"""Tests for Tutorial 1.2 — the agent loop mechanics."""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


def load_module():  # type: ignore[no-untyped-def]
    path = Path(__file__).parent.parent / "main.py"
    spec = importlib.util.spec_from_file_location("t12_main", path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules["t12_main"] = mod  # required so @dataclass can resolve string annotations
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _make_end_turn_response(text: str) -> MagicMock:
    block = MagicMock()
    block.type = "text"
    block.text = text
    response = MagicMock()
    response.stop_reason = "end_turn"
    response.content = [block]
    return response


def _make_tool_use_response(tool_id: str, query: str) -> MagicMock:
    block = MagicMock()
    block.type = "tool_use"
    block.id = tool_id
    block.name = "search"
    block.input = {"query": query}
    response = MagicMock()
    response.stop_reason = "tool_use"
    response.content = [block]
    return response


def test_loop_stops_on_end_turn() -> None:
    t12 = load_module()
    end_response = _make_end_turn_response("Here is a summary of recent AI research.")

    with patch.object(t12.anthropic, "Anthropic") as MockClient:
        MockClient.return_value.messages.create.return_value = end_response
        run = t12.run_agent("What is new in AI?")

    assert run.iterations == 1
    assert "summary" in run.final_answer


def test_loop_calls_tool_then_stops() -> None:
    t12 = load_module()
    tool_response = _make_tool_use_response("tool_1", "recent AI research")
    end_response = _make_end_turn_response("Based on search results, here is the answer.")

    with patch.object(t12.anthropic, "Anthropic") as MockClient:
        MockClient.return_value.messages.create.side_effect = [tool_response, end_response]
        run = t12.run_agent("What is new in AI?")

    assert run.iterations == 2
    assert run.final_answer != ""


def test_loop_respects_max_iter() -> None:
    t12 = load_module()
    tool_response = _make_tool_use_response("tool_1", "query")

    with patch.object(t12.anthropic, "Anthropic") as MockClient:
        MockClient.return_value.messages.create.return_value = tool_response
        t12.MAX_ITER = 3
        run = t12.run_agent("Keep searching forever")

    assert run.iterations == 3


def test_stub_search_returns_string() -> None:
    t12 = load_module()
    result = t12.stub_search("anything")
    assert isinstance(result, str)
    assert len(result) > 0
