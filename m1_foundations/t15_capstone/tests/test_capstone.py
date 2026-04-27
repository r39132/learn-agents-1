"""Tests for Tutorial 1.5 — the M1 capstone."""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


def load_module():  # type: ignore[no-untyped-def]
    path = Path(__file__).parent.parent / "main.py"
    spec = importlib.util.spec_from_file_location("t15_main", path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules["t15_main"] = mod  # required so @dataclass can resolve string annotations
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


def _make_tool_use_response(query: str) -> MagicMock:
    block = MagicMock()
    block.type = "tool_use"
    block.id = "id_1"
    block.name = "search"
    block.input = {"query": query}
    response = MagicMock()
    response.stop_reason = "tool_use"
    response.content = [block]
    return response


def _make_tavily(titles_urls: list[tuple[str, str]]) -> MagicMock:
    mock = MagicMock()
    mock.search.return_value = {
        "results": [
            {"title": t, "url": u, "content": f"Content about {t}"}
            for t, u in titles_urls
        ]
    }
    return mock


def test_result_has_answer_and_sources() -> None:
    t15 = load_module()
    mock_tavily = _make_tavily([("Paper A", "https://a.com"), ("Paper B", "https://b.com")])
    end_response = _make_end_turn_response("After searching, here is what I found.")
    tool_response = _make_tool_use_response("AI research 2025")

    with patch.object(t15.anthropic, "Anthropic") as MockClient, \
         patch.object(t15, "TavilyClient", return_value=mock_tavily), \
         patch.dict("os.environ", {"ANTHROPIC_API_KEY": "x", "TAVILY_API_KEY": "y"}):
        MockClient.return_value.messages.create.side_effect = [tool_response, end_response]
        result = t15.run_agent("What is new in AI?")

    assert result.answer != ""
    assert len(result.sources) == 2
    assert result.sources[0].title == "Paper A"
    assert result.sources[1].url == "https://b.com"


def test_sources_deduplicated_in_format_output() -> None:
    t15 = load_module()
    result = t15.ResearchResult(
        question="test",
        answer="answer",
        sources=[
            t15.Source(title="A", url="https://a.com", query="q1"),
            t15.Source(title="A", url="https://a.com", query="q2"),
            t15.Source(title="B", url="https://b.com", query="q1"),
        ],
    )
    output = t15.format_output(result)
    assert output.count("https://a.com") == 1
    assert output.count("https://b.com") == 1


def test_format_output_contains_question() -> None:
    t15 = load_module()
    result = t15.ResearchResult(question="What is AI?", answer="AI is...")
    output = t15.format_output(result)
    assert "What is AI?" in output


def test_format_output_contains_answer() -> None:
    t15 = load_module()
    result = t15.ResearchResult(question="Q", answer="This is the answer.")
    output = t15.format_output(result)
    assert "This is the answer." in output


def test_save_writes_file(tmp_path: Path) -> None:
    t15 = load_module()
    result = t15.ResearchResult(question="Q", answer="A")
    output = t15.format_output(result)
    save_path = tmp_path / "result.md"
    save_path.write_text(output)
    assert save_path.read_text() == output


def test_search_extracts_sources() -> None:
    t15 = load_module()
    mock_tavily = _make_tavily([("Title X", "https://x.com")])
    text, sources = t15.search(mock_tavily, "my query")
    assert len(sources) == 1
    assert sources[0].title == "Title X"
    assert sources[0].url == "https://x.com"
    assert sources[0].query == "my query"
    assert "Title X" in text
