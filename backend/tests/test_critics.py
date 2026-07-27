"""
test_critics.py — exercises the critic runner's composition logic.

Validates that compose_artifact produces gate-valid artifacts (hash embedded,
>= 3 located findings, >= 120 words, VERDICT present) and writes them to the
directory the manifest verifier expects. No network call — we feed a canned
model reply.
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from app.pipeline import critics, lint_suite
from pipeline_fixtures import build_project

# A canned model reply that is deliberately IMPERFECT: it omits the
# chapter_hash line and has no ## Findings heading. compose_artifact must fix
# both so the artifact still passes the gate.
_MODEL_REPLY = """\
Line 4: "The bread was still warm through the cloth." — strong sensory anchor, keep.

Line 12: "The onion rolled against the salt paper and settled." — the verb carries weight without naming it; good show-don't-tell.

Line 18: "She decided it would." — the interior turn is earned by the preceding inventory of the jug and the soup.

Overall the market morning is rendered in concrete physical detail. Body anchoring is spread across hands, ribs, and feet rather than concentrated in a single beat. Sentence-opener variety holds; no triplet closings. The closing image at the window resolves the errand into stillness. No named-emotion tells were found and the dialogue beats land with subtext. The only note is the second paragraph could tighten the handcart beat.

VERDICT: PASS
"""


def test_compose_artifact_is_gate_valid():
    with tempfile.TemporaryDirectory() as root:
        build_project(root)
        chapter_path = os.path.join(root, "manuscript", "001_market.md")
        chash = lint_suite.hash_chapter(chapter_path)

        result = critics.compose_artifact("show", 1, _MODEL_REPLY, chash, root)

        # Written to the manifest's expected location.
        assert result["artifact_path"] == os.path.join("critic_outputs", "chapter_1_show.md")
        assert os.path.isfile(os.path.join(root, result["artifact_path"]))

        # The chapter hash was embedded even though the model omitted it.
        with open(os.path.join(root, result["artifact_path"]), encoding="utf-8") as f:
            content = f.read()
        assert chash in content
        assert "chapter_hash:" in content

        # Gate substance rules satisfied.
        assert result["has_chapter_hash"] is True
        assert result["located_findings"] >= 3, result
        assert result["word_count"] >= 120, result
        assert result["gate_substance_ok"] is True
        assert result["verdict"] == "PASS"


def test_editorial_writes_to_coverage_reports():
    with tempfile.TemporaryDirectory() as root:
        build_project(root)
        chapter_path = os.path.join(root, "manuscript", "001_market.md")
        chash = lint_suite.hash_chapter(chapter_path)

        result = critics.compose_artifact("editorial", 1, _MODEL_REPLY, chash, root)
        assert result["artifact_path"] == os.path.join("coverage_reports", "editorial_report_ch1.md")
        assert os.path.isfile(os.path.join(root, result["artifact_path"]))


def test_composed_artifact_passes_hollow_critics_lint():
    """The written artifact must satisfy finalize's hollow_critics blocking lint."""
    from app.pipeline import lints
    with tempfile.TemporaryDirectory() as root:
        build_project(root)
        chapter_path = os.path.join(root, "manuscript", "001_market.md")
        chash = lint_suite.hash_chapter(chapter_path)

        critics.compose_artifact("voice", 1, _MODEL_REPLY, chash, root)

        report = lints.lint_hollow_critics(root)
        # The voice critic file must not appear in the hollow-critic findings.
        offenders = {f["file"] for f in report["findings"]}
        assert "chapter_1_voice.md" not in offenders, report


def _run_all():
    tests = [test_compose_artifact_is_gate_valid, test_editorial_writes_to_coverage_reports,
             test_composed_artifact_passes_hollow_critics_lint]
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
