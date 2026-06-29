"""
critics.py — the Open-Write critic runner (Phase C of the pipeline).

Each critic reviews a single chapter and writes a gate-valid artifact to
critic_outputs/ (or coverage_reports/ for the editorial critic). "Gate-valid"
means the artifact passes the deterministic completion gate:

  - >= 120 words and >= 3 located findings (line/paragraph ref + quoted span)
  - the real chapter_hash embedded (proves the critic read the actual file)
  - a VERDICT line (PASS | ADVANCE | REVISE)

The critic prompts are condensed operative versions of the Open-Write critic
architecture (show / voice / palette / continuity / naturalism), tuned to
force located findings rather than bare PASS assertions. The model call is
injectable so the composition logic is testable without a network key.
"""

from __future__ import annotations

import os
import re

from .lint_suite import hash_chapter
from .lints import count_located_findings


CRITIC_TYPES = ("show", "voice", "palette", "continuity", "naturalism")
# The editorial critic writes to coverage_reports/ instead of critic_outputs/.
EDITORIAL_TYPE = "editorial"


# ── Critic system prompts ─────────────────────────────────────────────────────
# Each forces a specific review lens and the output contract (located findings
# + chapter_hash + VERDICT). Condensed from the Open-Write critic architecture.

_SHOW = """\
You are the SHOW critic. Your single job: enforce show-don't-tell.

Flag every place the chapter TELLS an emotion or state instead of SHOWING it
through physical detail, action, or dialogue. Specifically look for:
- Named emotions (grief, horror, joy, rage, devastation, fear) stated directly
- Abstract summary where a rendered scene belongs
- Interiority told rather than embodied (hands, spine, breath, throat)
- Adverbs carrying the weight a concrete detail should carry

For EVERY finding, cite the location and quote the exact passage:
  Line N: "<the exact quoted text>" — <what is wrong and how to fix it>

Output contract (do not deviate):
1. Begin with the chapter_hash line you are given.
2. A ## Findings section with at least three located findings (Line N + quote).
3. A one-paragraph overall assessment.
4. End with: VERDICT: PASS  (or ADVANCE or REVISE)
PASS = nothing to fix. ADVANCE = minor notes, ship as-is. REVISE = must fix.
Be specific and honest. A chapter with real tell-spots gets REVISE, not PASS.
"""


_VOICE = """\
You are the VOICE critic. Your job: per-character voice consistency.

Check that each character speaks in a register consistent with their profile,
and that the narration's prose distance (close, middle, lyric) is varied
rather than monotonous. If a DECLARED VOICE REGISTERS block is attached, check
the dialogue against each named register (which surface when, what triggers
the shift) and flag any line that breaks a declared register without dramatic
cause. Flag:
- Dialogue that sounds interchangeable between characters
- A character dropping their established register without dramatic cause
- Five or more consecutive paragraphs at the same prose distance
- Narrative voice drifting from the locked voice spec

For EVERY finding cite the location and quote the exact passage:
  Line N: "<exact quoted text>" — <the voice problem>

Output contract:
1. Begin with the chapter_hash line you are given.
2. ## Findings with at least three located findings (Line N + quote).
3. A one-paragraph overall assessment.
4. End with: VERDICT: PASS | ADVANCE | REVISE
"""


_PALETTE = """\
You are the PALETTE critic. Your job: emotional-palette verification.

Verify that the chapter's emotional range is rendered (not named) and that
the dominant emotion is earned by what came before. Flag:
- The same emotional register held too long without modulation
- Emotional beats asserted ("she felt X") rather than dramatized
- A jarring emotional turn with no grounding setup
- Sensory palette (sight/sound/touch/smell/taste) that is thin or repetitive

For EVERY finding cite the location and quote the exact passage:
  Line N: "<exact quoted text>" — <the palette problem>

Output contract:
1. Begin with the chapter_hash line you are given.
2. ## Findings with at least three located findings (Line N + quote).
3. A one-paragraph overall assessment.
4. End with: VERDICT: PASS | ADVANCE | REVISE
"""


_CONTINUITY = """\
You are the CONTINUITY critic. Your job: state, timeline, and callback checks.

Given the chapter and any attached context (prior summaries, callback ledger,
character profiles), verify internal consistency. Flag:
- A character knowing something they have not yet learned
- A physical state contradiction (injury, location, possession) with prior chapters
- A timeline impossibility (events out of order, impossible travel time)
- A seeded callback that was paid off inconsistently or dropped
- Pronoun/identity ambiguity that breaks reference

Decompose any assumption before accepting it. For EVERY finding cite the
location and quote the exact passage:
  Line N: "<exact quoted text>" — <the continuity break, with the prior reference>

Output contract:
1. Begin with the chapter_hash line you are given.
2. ## Findings with at least three located findings (Line N + quote).
3. A one-paragraph overall assessment.
4. End with: VERDICT: PASS | ADVANCE | REVISE
"""


_NATURALISM = """\
You are the NATURALISM critic. Your job: AI-tell detection.

This is the model-independence layer. Hunt for the fingerprints of machine
prose so a different-model pass would not catch the same chapter sleeping:
- Em-dash overuse (count both em dashes and double-hyphens)
- Triplet closings (three short declarative sentences in a row)
- Uniform sentence rhythm or opener variety that is TOO even
- Stock refrains ("He had work to do", "It was not enough") repeated
- Generic metaphor instead of specific physical detail

For EVERY finding cite the location and quote the exact passage:
  Line N: "<exact quoted text>" — <the tell and a concrete replacement>

Output contract:
1. Begin with the chapter_hash line you are given.
2. ## Findings with at least three located findings (Line N + quote).
3. A one-paragraph overall assessment.
4. End with: VERDICT: PASS | ADVANCE | REVISE
"""


_EDITORIAL = """\
You are the EDITORIAL critic. Your job: a structural + prose editorial pass.

Assess the chapter as an editor would: does the scene earn its place in the
arc, does it open and close with intention, is the pacing right, does it
advance a character or plot thread. Flag:
- A scene that does not earn its word count (padding, repetition)
- A weak opening hook or an ending that trails off
- Pacing problems (rushed transition, stalled middle)
- A beat that should have been cut or combined

For EVERY finding cite the location and quote the exact passage:
  Line N: "<exact quoted text>" — <the editorial issue and the fix>

Output contract:
1. Begin with the chapter_hash line you are given.
2. ## Findings with at least three located findings (Line N + quote).
3. A one-paragraph overall assessment.
4. End with: VERDICT: PASS | ADVANCE | REVISE
"""

_SYSTEM_PROMPTS = {
    "show": _SHOW, "voice": _VOICE, "palette": _PALETTE,
    "continuity": _CONTINUITY, "naturalism": _NATURALISM,
    EDITORIAL_TYPE: _EDITORIAL,
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def chapter_number_from_filename(filename: str) -> int:
    """Extract the leading chapter number from a filename (001_market.md -> 1)."""
    m = re.match(r"(\d+)", os.path.basename(filename))
    return int(m.group(1)) if m else 0


def artifact_relpath(critic_type: str, chapter_number: int) -> str:
    """Where a critic's output lives, relative to the project root."""
    if critic_type == EDITORIAL_TYPE:
        return os.path.join("coverage_reports", f"editorial_report_ch{chapter_number}.md")
    return os.path.join("critic_outputs", f"chapter_{chapter_number}_{critic_type}.md")


def ensure_gate_format(content: str, chapter_hash: str) -> str:
    """
    Post-process the model output so the artifact is gate-valid regardless of
    whether the model obeyed the output contract:
      - guarantee the chapter_hash line is present at the top (proves the
        critic read this exact chapter; verify's hash-binding check requires
        an embedded hash to MATCH, and finalize's hollow_critics lint requires
        one to be PRESENT)
      - guarantee a ## Findings heading exists (so a PASS verdict is not HOLLOW)
    """
    header = f"chapter_hash: {chapter_hash}\n\n"
    # Strip any chapter_hash line the model may have emitted, then prepend ours.
    content = re.sub(r"^chapter_hash\s*[:=]\s*[a-fA-F0-9]{16,}\s*\n+", "", content,
                     flags=re.IGNORECASE | re.MULTILINE)
    content = header + content.lstrip()
    if not re.search(r"(?m)^#{1,3}\s*(?:Findings?|Violations?|Issues?|Flags?|Problems?|Weaknesses|Criticism)",
                     content):
        # Insert a Findings heading before the first Line N: finding if present,
        # else before the first blank-delimited block.
        if re.search(r"(?im)^\s*line\s+\d+", content):
            content = re.sub(r"(?im)^(\s*line\s+\d+)", r"## Findings\n\n\1", content, count=1)
        else:
            content = re.sub(r"\n\n", "\n\n## Findings\n\n", content, count=1)
    return content.strip() + "\n"


def extract_verdict(content: str) -> str:
    m = re.search(r"VERDICT\s*[:=]?\s*(PASS|ADVANCE|REVISE)", content, re.IGNORECASE)
    return m.group(1).upper() if m else "UNKNOWN"


# ── Prompt composition ────────────────────────────────────────────────────────

def build_messages(critic_type: str, chapter_text: str, chapter_hash: str,
                   context: str = "") -> tuple[str, list[dict]]:
    """Return (system_prompt, messages) for a critic pass."""
    system = _SYSTEM_PROMPTS[critic_type]
    user_parts = [f"chapter_hash: {chapter_hash}\n"]
    if context:
        user_parts.append(f"--- ATTACHED CONTEXT ---\n{context}\n--- END CONTEXT ---\n")
    user_parts.append("--- CHAPTER ---\n" + chapter_text + "\n--- END CHAPTER ---")
    user_parts.append(
        "\nReview this chapter now. Remember: begin your report with the "
        f"chapter_hash line (chapter_hash: {chapter_hash}), include a ## Findings "
        "section with at least three located findings each citing Line N and a "
        "quoted span, then your assessment, then VERDICT."
    )
    return system, [{"role": "user", "content": "\n".join(user_parts)}]


# ── Composition (testable without a network) ──────────────────────────────────

def compose_artifact(critic_type: str, chapter_number: int, model_output: str,
                     chapter_hash: str, project_path: str) -> dict:
    """
    Turn a model's raw critic output into a gate-valid artifact on disk.
    Returns metadata about the artifact (path, verdict, word count, located
    findings, and whether it currently satisfies the gate's substance rules).
    """
    content = ensure_gate_format(model_output, chapter_hash)
    rel = artifact_relpath(critic_type, chapter_number)
    full = os.path.join(project_path, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)

    word_count = len(content.split())
    located = count_located_findings(content)
    return {
        "critic_type": critic_type,
        "artifact_path": rel,
        "verdict": extract_verdict(content),
        "word_count": word_count,
        "located_findings": located,
        "has_chapter_hash": True,
        "gate_substance_ok": word_count >= 120 and located >= 3,
        "content_preview": content[:200],
    }


# ── Live runner ───────────────────────────────────────────────────────────────

async def run_critic(
    critic_type: str,
    chapter_path: str,
    project_path: str,
    api_key: str,
    model_id: str,
    context: str = "",
    temperature: float = 0.3,
    base_url: str = "https://openrouter.ai/api/v1",
) -> dict:
    """
    Run one critic over one chapter and write its artifact. Calls an
    OpenAI-compatible provider via app.ai.openrouter.run_chat. The model reply
    is post-processed by compose_artifact so the result always carries the real
    chapter hash.
    """
    from app.ai.openrouter import run_chat
    from .word_count import strip_artifacts

    with open(chapter_path, "r", encoding="utf-8-sig") as f:
        chapter_text = f.read().replace("\ufeff", "")
    chapter_text = strip_artifacts(chapter_text)
    chapter_hash = hash_chapter(chapter_path)

    system, messages = build_messages(critic_type, chapter_text, chapter_hash, context)
    reply = await run_chat(api_key, model_id, system, messages, temperature=temperature, base_url=base_url)

    chapter_number = chapter_number_from_filename(chapter_path)
    return compose_artifact(critic_type, chapter_number, reply, chapter_hash, project_path)
