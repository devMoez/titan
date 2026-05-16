"""Tests for the Nous-Titan-3/4 non-agentic warning detector.

Prior to this check, the warning fired on any model whose name contained
``"Titan"`` anywhere (case-insensitive). That false-positived on unrelated
local Modelfiles such as ``Titan-brain:qwen3-14b-ctx16k`` — a tool-capable
Qwen3 wrapper that happens to live under the "Titan" tag namespace.

``is_nous_Titan_non_agentic`` should only match the actual Nous Research
Titan-3 / Titan-4 chat family.
"""

from __future__ import annotations

import pytest

from Titan_cli.model_switch import (
    _Titan_MODEL_WARNING,
    _check_Titan_model_warning,
    is_nous_Titan_non_agentic,
)


@pytest.mark.parametrize(
    "model_name",
    [
        "NousResearch/Titan-3-Llama-3.1-70B",
        "NousResearch/Titan-3-Llama-3.1-405B",
        "Titan-3",
        "Titan-3",
        "Titan-4",
        "Titan-4-405b",
        "Titan_4_70b",
        "openrouter/Titan3:70b",
        "openrouter/nousresearch/Titan-4-405b",
        "NousResearch/Titan3",
        "Titan-3.1",
    ],
)
def test_matches_real_nous_Titan_chat_models(model_name: str) -> None:
    assert is_nous_Titan_non_agentic(model_name), (
        f"expected {model_name!r} to be flagged as Nous Titan 3/4"
    )
    assert _check_Titan_model_warning(model_name) == _Titan_MODEL_WARNING


@pytest.mark.parametrize(
    "model_name",
    [
        # Kyle's local Modelfile — qwen3:14b under a custom tag
        "Titan-brain:qwen3-14b-ctx16k",
        "Titan-brain:qwen3-14b-ctx32k",
        "Titan-honcho:qwen3-8b-ctx8k",
        # Plain unrelated models
        "qwen3:14b",
        "qwen3-coder:30b",
        "qwen2.5:14b",
        "claude-opus-4-6",
        "anthropic/claude-sonnet-4.5",
        "gpt-5",
        "openai/gpt-4o",
        "google/gemini-2.5-flash",
        "deepseek-chat",
        # Non-chat Titan models we don't warn about
        "Titan-llm-2",
        "Titan2-pro",
        "nous-Titan-2-mistral",
        # Edge cases
        "",
        "Titan",  # bare "Titan" isn't the 3/4 family
        "Titan-brain",
        "brain-Titan-3-impostor",  # "3" not preceded by /: boundary
    ],
)
def test_does_not_match_unrelated_models(model_name: str) -> None:
    assert not is_nous_Titan_non_agentic(model_name), (
        f"expected {model_name!r} NOT to be flagged as Nous Titan 3/4"
    )
    assert _check_Titan_model_warning(model_name) == ""


def test_none_like_inputs_are_safe() -> None:
    assert is_nous_Titan_non_agentic("") is False
    # Defensive: the helper shouldn't crash on None-ish falsy input either.
    assert _check_Titan_model_warning("") == ""

