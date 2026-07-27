"""
pipeline_fixtures.py — shared fixture builder for the pipeline tests.

Builds a minimal Open-Write project (under a temp dir passed by the caller)
that PASSES the completion gate. Used by both the in-process logic test
(test_pipeline.py) and the HTTP routes test (test_pipeline_routes.py).
"""

import json
import os

from app.pipeline import lint_suite

CHAPTER_TEXT = """\
The morning market opened before the sun cleared the ridge. Marta walked between the stalls and counted the coins in her pocket twice. The fish seller nodded at her but said nothing. She bought bread, a single onion, and a twist of salt wrapped in brown paper.

A boy pushed a handcart past her, its iron rim ringing on the cobbles. She stepped aside and let him pass. The bread was still warm through the cloth. She held it against her ribs and kept walking.

At the far end of the row an old woman sat behind a table of dried herbs. Marta stopped and looked at the bundles of thyme. The old woman watched her hands, not her face. Marta picked up one bundle and turned it over. The leaves crumbled a little at the stem. She put it down and chose another.

The bell of the chapel rang the hour. Six strokes, and the market noise swallowed each one before it finished. Marta paid for the thyme and tucked it into the basket with the bread. The onion rolled against the salt paper and settled.

She climbed the lane toward home. The stone walls on either side held the night's cold a little longer than the open road. Lizards would be out later, on the south-facing stones. She thought about the water in the jug, whether it would be enough for the bread and the soup both. She decided it would.

Her door was where she had left it, the latch up as she had set it. She pushed inside and set the basket on the table. The room smelled of last night's fire and the soap she used on the floor. She unwrapped the bread and cut two slices. The crust resisted the knife and then gave way. She ate standing at the window, watching the light come down over the ridge and fill the valley below the town.
"""


def _write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def critic_body(label, chapter_hash=None, quote="The bread was still warm through the cloth."):
    """A critic/plan file body.

    When chapter_hash is given the real chapter hash is embedded, which is
    REQUIRED for files under critic_outputs/ (the finalize hollow_critics lint
    requires the hash present; verify's hash-binding check requires it to
    match). Coverage-report files pass chapter_hash=None so no hash is embedded
    (verify flags a mismatch, not an absence).
    """
    head = f"chapter_hash: {chapter_hash}\n\n" if chapter_hash else ""
    return (
        f"{head}"
        f"## Findings\n\n"
        f"Line 4: \"{quote}\" — the detail grounds the morning in real sensation.\n\n"
        f"Line 12: \"The onion rolled against the salt paper and settled.\" — the verb "
        f"carries the weight of the basket without naming it.\n\n"
        f"Line 18: \"She decided it would.\" — the interior turn is earned by the "
        f"preceding physical inventory.\n\n"
        f"The {label} pass reviewed this chapter against its scene goals and the "
        f"locked voice specification. The prose holds a consistent register from "
        f"the first stall to the kitchen window. Body anchoring is distributed "
        f"across hands, ribs, and feet rather than concentrated in a single beat. "
        f"Sentence-opener variety is maintained; no triplet closings were detected. "
        f"The market sequence moves the errand forward without summary shortcuts, "
        f"and the closing image resolves the motion into stillness at the window. "
        f"No negative-construction density spike was found, and the dialogue beats "
        f"land with subtext rather than exposition. VERDICT: PASS — the chapter "
        f"meets the {label} bar for advancement."
    )


def build_project(root):
    """Create a minimal Open-Write project that PASSES the completion gate."""
    _write(os.path.join(root, "bible", "01_concept.md"), "# Concept\n\nA quiet market morning.")
    _write(os.path.join(root, "bible", "04_outline.md"),
           "# Outline\n\n## Chapter 1\n\nMarta visits the market.\n")
    _write(os.path.join(root, "bible", "07_format_rules.md"), "# Format Rules\n\nNo em dashes.")
    _write(os.path.join(root, "bible", "LOCKED_VOICE_SPEC.md"), "# Voice\n\nLived History.")

    _write(os.path.join(root, "manuscript", "001_market.md"), CHAPTER_TEXT)
    _write(os.path.join(root, "manuscript", "novel.md"),
           "# Market Morning\n\n---\n\n" + CHAPTER_TEXT)

    chash = lint_suite.hash_chapter(os.path.join(root, "manuscript", "001_market.md"))

    _write(os.path.join(root, "critic_outputs", "chapter_1_plan.md"), critic_body("plan", chash))
    for label in ("show", "voice", "palette", "continuity", "naturalism"):
        _write(os.path.join(root, "critic_outputs", f"chapter_1_{label}.md"), critic_body(label, chash))

    _write(os.path.join(root, "coverage_reports", "editorial_report_ch1.md"), critic_body("editorial"))
    _write(os.path.join(root, "coverage_reports", "adversarial_read.md"), critic_body("adversarial"))

    _write(os.path.join(root, "state", "callback_ledger.json"), json.dumps({"seeds": []}))
    _write(os.path.join(root, "state", "convention_ledger.json"), json.dumps({"anchors": {}}))
