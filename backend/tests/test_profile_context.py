"""
test_profile_context.py — Phase G: importance-aware profile context for the pipeline.

Validates that profile_context loads character profiles, filters trait blocks by
importance level per consumer (architect/writer/voice/continuity), and surfaces
voice notes as declared voice registers. No network.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from app.pipeline import profile_context


# A minimal character profile in the on-disk Markdown+frontmatter format that
# app.routers.profiles._parse_profile_markdown understands. It carries one
# trait per importance level so the routing filter is observable.
_PROFILE_MD = """\
---
name: Marta
role: Protagonist
tags: []
status: active
created_at: 2026-01-01T00:00:00
updated_at: 2026-01-01T00:00:00
---

# Overview

A quiet market woman.

# Physical Traits

- trait: callused hands
  description: Hands hardened by years at the stall.
  importance: core

- trait: limp
  description: A faint limp from a childhood fall.
  importance: background

# Voice Notes

- trait: The Haggler
  description: Brisk, clipped, numbers-first. Surfaces at the market.
  importance: core

- trait: The Mother
  description: Softens, sentence shape lengthens, around her son.
  importance: present

# Hidden and Foreshadowing

- trait: knows the smuggler
  description: She has not told her son about the man at the dock.
  importance: hidden
"""


def _build_project(root):
    chars = os.path.join(root, "profiles", "characters")
    os.makedirs(chars, exist_ok=True)
    with open(os.path.join(chars, "marta.md"), "w", encoding="utf-8") as f:
        f.write(_PROFILE_MD)


def test_load_character_profiles():
    with tempfile.TemporaryDirectory() as root:
        _build_project(root)
        profiles = profile_context.load_character_profiles(root)
        assert len(profiles) == 1
        assert profiles[0].name == "Marta"


def test_load_returns_empty_when_no_profiles():
    with tempfile.TemporaryDirectory() as root:
        assert profile_context.load_character_profiles(root) == []


def test_architect_gets_every_importance_level():
    with tempfile.TemporaryDirectory() as root:
        _build_project(root)
        ctx = profile_context.character_context(root, "architect")
        # core, background, present, hidden all reach the architect.
        assert "callused hands [core]" in ctx
        assert "limp [background]" in ctx
        assert "The Mother [present]" in ctx
        assert "knows the smuggler [hidden]" in ctx


def test_writer_excludes_background_and_contextual():
    with tempfile.TemporaryDirectory() as root:
        _build_project(root)
        ctx = profile_context.character_context(root, "writer")
        assert "callused hands [core]" in ctx        # core kept
        assert "The Mother [present]" in ctx          # present kept
        assert "knows the smuggler [hidden]" in ctx   # hidden kept as subtext
        assert "limp [background]" not in ctx         # background excluded
        # The hidden-as-subtext note must be attached for the writer.
        assert "subtext only" in ctx or "NEVER name" in ctx


def test_voice_consumer_excludes_background_and_hidden():
    with tempfile.TemporaryDirectory() as root:
        _build_project(root)
        ctx = profile_context.character_context(root, "voice")
        assert "The Haggler [core]" in ctx
        assert "limp [background]" not in ctx
        assert "knows the smuggler [hidden]" not in ctx


def test_voice_registers_context_surfaces_named_registers():
    with tempfile.TemporaryDirectory() as root:
        _build_project(root)
        ctx = profile_context.voice_registers_context(root)
        assert "DECLARED VOICE REGISTERS" in ctx
        assert "The Haggler" in ctx
        assert "The Mother" in ctx
        # Non-voice material must NOT leak into the registers block.
        assert "callused hands" not in ctx


def test_voice_registers_empty_without_profiles():
    with tempfile.TemporaryDirectory() as root:
        assert profile_context.voice_registers_context(root) == ""


def _run_all():
    tests = [
        test_load_character_profiles,
        test_load_returns_empty_when_no_profiles,
        test_architect_gets_every_importance_level,
        test_writer_excludes_background_and_contextual,
        test_voice_consumer_excludes_background_and_hidden,
        test_voice_registers_context_surfaces_named_registers,
        test_voice_registers_empty_without_profiles,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {t.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"  ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if _run_all() else 0)
