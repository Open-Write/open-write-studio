"""
test_pipeline.py — exercises the ported Open-Write completion-gate toolchain.

Runs with plain Python (`python tests/test_pipeline.py`) or under pytest
(`uv run pytest tests/test_pipeline.py`). The pipeline modules use only the
standard library, so the core logic is testable without FastAPI installed.
"""

import json
import os
import shutil
import sys
import tempfile

# Make `app` and the tests package importable when run directly from backend/.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from app.pipeline import word_count, build_manifest, verify_completion, finalize
from pipeline_fixtures import build_project, CHAPTER_TEXT


# --- Local helpers -----------------------------------------------------------

def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def _build_project(root):
    # Thin alias kept so the tests below read naturally; the real builder
    # lives in pipeline_fixtures so the routes test can share it.
    return build_project(root)


# --- Tests ------------------------------------------------------------------

def test_word_count_and_strip():
    raw = "# Heading\n\nProse body words here.\n\n[Word count: 3 words]\n--- BEGIN CRITIC ---\nx\n--- END CRITIC ---\n"
    clean = word_count.strip_artifacts(raw)
    assert word_count.count_prose_words_from_text(clean) == 4  # "Prose body words here."
    assert "Word count" not in clean
    assert "CRITIC" not in clean


def test_manifest_chapter_detection():
    with tempfile.TemporaryDirectory() as root:
        _write(os.path.join(root, "bible", "04_outline.md"),
               "# Outline\n\n## Chapter 1\n\n## Chapter 2\n\n## Chapter 3\n")
        assert build_manifest.count_chapters_in_outline(os.path.join(root, "bible", "04_outline.md")) == 3


def test_full_gate_pass():
    with tempfile.TemporaryDirectory() as root:
        _build_project(root)

        manifest = build_manifest.build_manifest(1, "Market Morning", "novel", word_floor=200)
        _write(os.path.join(root, "state", "completion_manifest.json"), json.dumps(manifest, indent=2))

        result = finalize.finalize(root)
        assert result["finalize_verdict"] == "COMPLETE", result
        assert os.path.isfile(os.path.join(root, "state", "COMPLETION_PASS.json"))
        assert not os.path.isfile(os.path.join(root, "state", "COMPLETION_INCOMPLETE.json"))

        # The certificate is bound to the manuscript hash.
        with open(os.path.join(root, "state", "COMPLETION_PASS.json"), encoding="utf-8") as f:
            cert = json.load(f)
        assert cert["manuscript_sha256"] == result["manuscript_sha256"]
        assert cert["agent_may_not_write_this_file"] is True


def test_full_gate_fail_on_missing_critic():
    with tempfile.TemporaryDirectory() as root:
        _build_project(root)
        os.remove(os.path.join(root, "critic_outputs", "chapter_1_voice.md"))  # remove a required critic

        manifest = build_manifest.build_manifest(1, "Market Morning", "novel", word_floor=200)
        _write(os.path.join(root, "state", "completion_manifest.json"), json.dumps(manifest, indent=2))

        result = finalize.finalize(root)
        assert result["finalize_verdict"] == "INCOMPLETE", result
        assert os.path.isfile(os.path.join(root, "state", "COMPLETION_INCOMPLETE.json"))
        assert not os.path.isfile(os.path.join(root, "state", "COMPLETION_PASS.json"))


def test_finalize_invalidates_stale_certificate():
    with tempfile.TemporaryDirectory() as root:
        _build_project(root)
        manifest = build_manifest.build_manifest(1, "Market Morning", "novel", word_floor=200)
        _write(os.path.join(root, "state", "completion_manifest.json"), json.dumps(manifest, indent=2))

        finalize.finalize(root)  # produces a valid certificate
        # Tamper with the manuscript so its hash changes.
        _write(os.path.join(root, "manuscript", "novel.md"),
               "# Market Morning\n\n---\n\n" + CHAPTER_TEXT + "\n\nAn extra paragraph changes the hash.\n")
        result = finalize.finalize(root)
        assert result["finalize_verdict"] == "INVALIDATED", result


def _run_all():
    tests = [
        test_word_count_and_strip,
        test_manifest_chapter_detection,
        test_full_gate_pass,
        test_full_gate_fail_on_missing_critic,
        test_finalize_invalidates_stale_certificate,
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
