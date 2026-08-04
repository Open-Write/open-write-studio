# tests/test_profile_chat_prompts.py -- Profile Companion prompt guardrails
# ===========================================================================
# Tests for build_profile_chat_system_prompt and the mode routing in
# _profile_chat_addendum. Open-Write supports these modes:
#   chat/general/ask_clarifying, refine/interpret_profile/generate_summary,
#   extract_traits, check_consistency, guide, and a fallback for unknown modes.

from app.ai.prompts import (
    BASE_WRITING_ASSISTANT_CONTRACT,
    TEMPERATURE_DEFAULTS,
    _profile_chat_addendum,
    build_profile_chat_system_prompt,
)


CHARACTER_SECTIONS = [
    "Physical Traits", "Personality Traits", "Motivations", "Voice Notes",
    "Hidden and Foreshadowing Traits", "Relationships Overview", "Notes",
]


# ── Existing modes route to their addenda ────────────────────────────────────

def test_chat_mode_exists():
    text = _profile_chat_addendum("chat", "character", None)
    assert "MODE: GENERAL CHAT" in text


def test_refine_mode_exists():
    text = _profile_chat_addendum("refine", "character", None)
    assert "MODE: REFINE AND INTERPRET" in text


def test_extract_traits_mode_exists():
    text = _profile_chat_addendum("extract_traits", "character", None)
    assert "MODE: EXTRACT TRAITS" in text


def test_check_consistency_mode_exists():
    text = _profile_chat_addendum("check_consistency", "character", None)
    assert "MODE: CHECK CONSISTENCY" in text


def test_guide_mode_exists():
    text = _profile_chat_addendum("guide", "character", None)
    assert "MODE: GUIDED PROFILE BUILDING" in text


def test_unknown_mode_still_falls_back():
    assert "MODE: FALLBACK" in _profile_chat_addendum("no-such-mode", "character", None)


# ── Full system prompt assembly ──────────────────────────────────────────────

def test_system_prompt_includes_base_contract():
    prompt = build_profile_chat_system_prompt("chat", "character", "general", CHARACTER_SECTIONS)
    assert BASE_WRITING_ASSISTANT_CONTRACT in prompt
    assert "MODE: GENERAL CHAT" in prompt


def test_system_prompt_carries_content_mode():
    prompt = build_profile_chat_system_prompt("chat", "character", "mature", CHARACTER_SECTIONS)
    assert "CONTENT MODE: MATURE" in prompt


# ── Temperature ─────────────────────────────────────────────────────────────

def test_profile_temperature_is_below_generation():
    assert TEMPERATURE_DEFAULTS["profile"] < TEMPERATURE_DEFAULTS["generation"]
