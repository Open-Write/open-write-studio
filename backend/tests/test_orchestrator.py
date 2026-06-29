"""
test_orchestrator.py — exercises the Phase P orchestrator state machine.

Uses an injectable model_call (no network) to drive the phase progression and
verify that: run state persists and resumes, the per-unit loop advances the
chapter index correctly, editorial_lock builds the manifest, and the critics
phase produces gate-valid artifacts via critics.compose_artifact.
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from app.pipeline import orchestrator, critics as critics_mod, lint_suite
from pipeline_fixtures import CHAPTER_TEXT, build_project


# --- canned model call -------------------------------------------------------
# Returns phase-appropriate content so each executor has something to write.

_PLAN_REPLY = (
    "## Chapter Plan\n\nScene 1: market morning. Scene vs summary: scene. "
    "Body anchor: hands on coins. Sensory register: fish, thyme. Prose distance: close."
)
_CRITIC_REPLY = (
    'Line 4: "The bread was still warm through the cloth." — strong sensory anchor that grounds '
    'the morning errand in real sensation; the verb choice and the cloth detail keep the reader '
    'inside Marta\'s body rather than narrating from above.\n\n'
    'Line 12: "The onion rolled against the salt paper and settled." — the verb carries the weight '
    'of the basket without naming it; the settling motion resolves the movement of the row into '
    'stillness, a small turn rendered entirely through object behavior.\n\n'
    'Line 18: "She decided it would." — the interior turn is earned by the preceding physical '
    'inventory of the jug and the soup; the abstraction is permitted because the concrete ground '
    'has already been laid, and the brevity of the line is the point.\n\n'
    'Overall the market morning is rendered in concrete physical detail from the first stall to '
    'the kitchen window. Body anchoring is distributed across hands, ribs, and feet rather than '
    'concentrated in a single beat, so no one anatomical register wears out. Sentence-opener '
    'variety holds throughout, with no triplet closings or uniform rhythm detected. The closing '
    'image at the window resolves the errand into stillness without summary shortcut. No '
    'named-emotion tells were found, and the dialogue beats land with subtext rather than '
    'exposition. The only note is the second paragraph could tighten the handcart beat. '
    'VERDICT: PASS'
)


def make_canned_model_call():
    """A canned async model call keyed off the system-prompt content."""
    async def model_call(system_prompt: str, user_prompt: str) -> str:
        s = system_prompt.lower()
        u = (user_prompt or "").lower()
        if "bible" in s and "architect" in s:
            return (
                "---BIBLE-FILE: bible/01_concept.md---\n# Concept\n\nA quiet market morning.\n"
                "\n---BIBLE-FILE: bible/04_outline.md---\n# Outline\n\n## Chapter 1\n\nMarta visits the market.\n"
                "\n---BIBLE-FILE: bible/07_format_rules.md---\n# Format Rules\n\nNo em dashes.\n"
            )
        if "voice experiment" in s or "lock a narrative voice" in s:
            return "# LOCKED_VOICE_SPEC\n\nProse distance: close. Body anchors: hands, ribs.\n"
        if "you are the editorial panel" in s or "before outline lock" in s:
            return "## Findings\n\nLine 1: arc holds. VERDICT: ADVANCE\n"
        if "you are the architect for a single chapter" in s:
            return _PLAN_REPLY
        if "you are the prose writer" in s:
            return CHAPTER_TEXT
        if "critic" in s or "show" in s or "voice" in s or "palette" in s:
            return _CRITIC_REPLY
        if "adversarial" in s:
            return "## Adversarial Read\n\nLine 20: tell-spot. Score: 7.5/10.\n"
        return "Canned reply.\n"
    return model_call


def _resolver(model_call):
    """Wrap a single canned model call as the role-based resolver the
    orchestrator now expects (both roles share the canned call)."""
    return lambda role: model_call


# --- tests -------------------------------------------------------------------

def test_start_and_load_run_state():
    with tempfile.TemporaryDirectory() as root:
        state = orchestrator.start_run(root, "Test Novel")
        assert state.current_phase == "bible"
        assert state.status == "running"

        loaded = orchestrator.load_run_state(root)
        assert loaded is not None
        assert loaded.project_name == "Test Novel"
        assert loaded.current_phase == "bible"
        assert os.path.isfile(os.path.join(root, "state", "pipeline_run.json"))


def test_next_phase_project_scope():
    with tempfile.TemporaryDirectory() as root:
        state = orchestrator.start_run(root)
        state.current_phase = "bible"
        assert orchestrator.next_phase(state) == "voice"
        state.current_phase = "voice"
        assert orchestrator.next_phase(state) == "editorial_lock"
        state.current_phase = "editorial_lock"
        # No units yet (manifest not built) -> still enters per-unit loop at architect.
        assert orchestrator.next_phase(state) == "architect"


def test_next_phase_unit_loop_and_closing():
    with tempfile.TemporaryDirectory() as root:
        state = orchestrator.start_run(root, units=[1, 2])
        # Within a chapter: architect -> writer -> critics -> editorial -> verify_unit
        state.current_phase = "architect"
        assert orchestrator.next_phase(state) == "writer"
        state.current_phase = "verify_unit"
        # More chapters remain -> back to architect for the next chapter.
        state.current_unit_index = 0
        assert orchestrator.next_phase(state) == "architect"
        # Last chapter -> assemble.
        state.current_unit_index = 1
        assert orchestrator.next_phase(state) == "assemble"
        state.current_phase = "assemble"
        assert orchestrator.next_phase(state) == "adversarial"
        state.current_phase = "adversarial"
        assert orchestrator.next_phase(state) == "finalize"
        state.current_phase = "finalize"
        assert orchestrator.next_phase(state) is None


def test_bible_phase_writes_files_and_advances():
    with tempfile.TemporaryDirectory() as root:
        state = orchestrator.start_run(root, "Test Novel")
        model_call = make_canned_model_call()
        result = _await(orchestrator.advance_phase(root, _resolver(model_call)))
        assert result["phase"] == "bible"
        assert os.path.isfile(os.path.join(root, "bible", "04_outline.md"))
        assert os.path.isfile(os.path.join(root, "bible", "01_concept.md"))
        # State advanced to voice.
        loaded = orchestrator.load_run_state(root)
        assert loaded.current_phase == "voice"


def test_editorial_lock_builds_manifest():
    with tempfile.TemporaryDirectory() as root:
        model_call = make_canned_model_call()
        orchestrator.start_run(root, "Test Novel")
        # Run bible + voice to seed the bible files.
        _await(orchestrator.advance_phase(root, _resolver(model_call)))
        _await(orchestrator.advance_phase(root, _resolver(model_call)))
        # editorial_lock should detect 1 chapter and build the manifest.
        result = _await(orchestrator.advance_phase(root, _resolver(model_call)))
        assert result["phase"] == "editorial_lock"
        assert result["result"]["manifest"] is not None
        assert result["result"]["manifest"]["chapters_detected"] == 1
        assert os.path.isfile(os.path.join(root, "state", "completion_manifest.json"))
        loaded = orchestrator.load_run_state(root)
        assert loaded.units == [1]


def test_critics_phase_produces_gate_valid_artifacts():
    with tempfile.TemporaryDirectory() as root:
        build_project(root)  # a gate-PASSING project with chapter 1 already written
        model_call = make_canned_model_call()
        orchestrator.start_run(root, "Test Novel")
        loaded = orchestrator.load_run_state(root)
        loaded.units = [1]
        loaded.current_phase = "critics"
        orchestrator.save_run_state(loaded)

        result = _await(orchestrator.advance_phase(root, _resolver(model_call)))
        assert result["phase"] == "critics"
        arts = result["result"]["critics"]
        assert len(arts) == 6  # five critics + editorial
        # Each artifact is gate-valid (compose_artifact enforces this).
        for a in arts:
            assert a["gate_substance_ok"] is True, a
            assert a["has_chapter_hash"] is True
            assert os.path.isfile(os.path.join(root, a["artifact_path"]))


def test_advance_marks_complete_at_finalize():
    with tempfile.TemporaryDirectory() as root:
        build_project(root)
        model_call = make_canned_model_call()
        orchestrator.start_run(root, "Test Novel")
        loaded = orchestrator.load_run_state(root)
        loaded.units = [1]
        loaded.current_phase = "finalize"
        orchestrator.save_run_state(loaded)

        result = _await(orchestrator.advance_phase(root, _resolver(model_call)))
        assert result["phase"] == "finalize"
        assert result["next_phase"] is None
        loaded = orchestrator.load_run_state(root)
        assert loaded.status == "complete"


# --- helper ------------------------------------------------------------------

def _await(coro):
    import asyncio
    return asyncio.new_event_loop().run_until_complete(coro)


def _run_all():
    tests = [
        test_start_and_load_run_state,
        test_next_phase_project_scope,
        test_next_phase_unit_loop_and_closing,
        test_bible_phase_writes_files_and_advances,
        test_editorial_lock_builds_manifest,
        test_critics_phase_produces_gate_valid_artifacts,
        test_advance_marks_complete_at_finalize,
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
