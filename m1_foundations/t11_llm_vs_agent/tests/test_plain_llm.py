"""Tests for Tutorial 1.1 — verifies the module structure, not LLM output."""

import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock


def load_module():  # type: ignore[no-untyped-def]
    path = Path(__file__).parent.parent / "main.py"
    spec = importlib.util.spec_from_file_location("t11_main", path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def test_plain_llm_call_returns_string() -> None:
    t11 = load_module()

    mock_text = MagicMock()
    mock_text.text = "I don't have access to real-time data."
    mock_response = MagicMock()
    mock_response.content = [mock_text]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    result = t11.plain_llm_call(mock_client, "What happened in AI this week?")

    assert isinstance(result, str)
    assert len(result) > 0
    mock_client.messages.create.assert_called_once()


def test_plain_llm_call_passes_question_to_api() -> None:
    t11 = load_module()

    mock_text = MagicMock()
    mock_text.text = "Some answer."
    mock_response = MagicMock()
    mock_response.content = [mock_text]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    question = "What is the latest research on transformers?"
    t11.plain_llm_call(mock_client, question)

    call_kwargs = mock_client.messages.create.call_args
    messages = call_kwargs.kwargs.get("messages") or call_kwargs.args[0]
    assert any(question in str(m) for m in messages)
