"""
orchestrator.py — the Open-Write autonomous pipeline (Phase P).

A resumable, phase-by-phase state machine that drives the full novel-production
pipeline over OpenRouter, gated by the deterministic toolchain between phases.
The orchestrator NEVER auto-advances past a FAIL and writes its run state to
`<project>/state/pipeline_run.json` so a run can be paused and resumed across
sessions (an Open-Write rule: "reduce context = resume, never abbreviate").

Phase sequence
--------------
  Project scope:   bible -> voice -> editorial_lock (builds the manifest)
  Per unit (loop): architect -> writer -> critics -> editorial -> verify_unit
  Project scope:   assemble -> adversarial -> finalize

Each call to ``advance_phase`` runs exactly ONE phase and returns its artifact
metadata + the gate verdict, so the frontend can pause for human approval
between phases. The model call is injectable (``model_call``) so the
progression logic is testable without a network key, mirroring the pattern
already proven in critics.py.

System prompts are loaded from the canonical Open-Write rule files under
``openwrite/novel_template/.kilo/rules-*.md`` when present, with a condensed
operative fallback when a file is missing (so a project that doesn't ship the
reference tree still runs).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Awaitable, Callable, Optional

from . import build_manifest, verify_completion, finalize as finalize_mod
from .word_count import strip_artifacts
from . import profile_context

# ── Path to the frozen Open-Write reference (read-only) ───────────────────────
# Resolved lazily so importing this module never depends on the reference tree.
_REFERENCE_ROOT = os.environ.get(
    "OPENWRITE_REFERENCE",
    os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "openwrite")),
)
_RULE_DIR = os.path.join(_REFERENCE_ROOT, "novel_template", ".kilo")

RUN_STATE_FILENAME = "pipeline_run.json"
RUN_STATE_REL = os.path.join("state", RUN_STATE_FILENAME)


# ── Model-call type ──────────────────────────────────────────────────────────
# async (system_prompt: str, user_prompt: str) -> str
ModelCall = Callable[[str, str], Awaitable[str]]


# ── Phases ───────────────────────────────────────────────────────────────────

# Scope tags
PROJECT = "project"
PER_UNIT = "per_unit"

# Ordered phase keys. Project phases run once; per-unit phases run for each
# chapter in the manifest scope.
PROJECT_PHASES = ["bible", "voice", "editorial_lock"]
UNIT_PHASES = ["architect", "writer", "critics", "editorial", "verify_unit"]
CLOSING_PHASES = ["assemble", "adversarial", "finalize"]

ALL_PHASES = PROJECT_PHASES + UNIT_PHASES + CLOSING_PHASES


@dataclass
class PhaseSpec:
    key: str
    label: str
    scope: str
    rule_file: Optional[str]          # relative to novel_template/.kilo/
    fallback_prompt: str
    gate_phase: bool                  # run the gate after this phase?


PHASE_SPECS: dict[str, PhaseSpec] = {
    "bible": PhaseSpec(
        "bible", "Bible (concept / outline / format)", PROJECT,
        rule_file=None,
        gate_phase=False,
        fallback_prompt=(
            "You are the ARCHITECT for the story bible. Produce the foundational "
            "bible files: a concept (logline + thematic architecture), an outline "
            "(chapter-by-chapter beats with palettes and state changes), and format "
            "rules (prose discipline). Ground every choice in concrete physical "
            "rendering. Output the outline so each chapter is a level-2 heading "
            "(## Chapter N) so the manifest builder can count chapters. Write "
            "markdown sections separated by '---BIBLE-FILE: <relpath>---' markers."
        ),
    ),
    "voice": PhaseSpec(
        "voice", "Voice selection", PROJECT,
        rule_file=None,
        gate_phase=False,
        fallback_prompt=(
            "You are the VOICE experiment runner. Select and lock a narrative voice "
            "for this novel. Describe the prose distance (close / middle / lyric), "
            "the body-anchor conventions (hands, spine, throat), the sentence-rhythm "
            "profile, and the register each character speaks in. Output a LOCKED_VOICE_SPEC."
        ),
    ),
    "editorial_lock": PhaseSpec(
        "editorial_lock", "Editorial review + outline lock", PROJECT,
        rule_file="rules-editorial-eval.md",
        gate_phase=False,
        fallback_prompt=(
            "You are the EDITORIAL panel reviewing the bible for structural soundness "
            "before outline lock. Assess arc shape, chapter pacing, thematic spine, "
            "and callback seeding. Produce a coverage report with located findings and "
            "an ADVANCE/REVISE verdict. The outline is locked after this pass."
        ),
    ),
    "architect": PhaseSpec(
        "architect", "Architect (per-unit plan)", PER_UNIT,
        rule_file="rules-architect.md",
        gate_phase=False,
        fallback_prompt=(
            "You are the ARCHITECT for a single chapter. Given the bible, voice spec, "
            "and prior chapter tail, produce a per-beat rendering plan: scene vs summary "
            "designation, body anchors, sensory register, prose distance, want/obstacle/"
            "subtext/turn, concrete particulars, entry/exit, and per-scene word allocations. "
            "Output the plan as markdown."
        ),
    ),
    "writer": PhaseSpec(
        "writer", "Prose writer (draft)", PER_UNIT,
        rule_file="rules-prose-writer.md",
        gate_phase=True,
        fallback_prompt=(
            "You are the PROSE WRITER. Given the architect plan, format rules, voice spec, "
            "character profiles, and the prior chapter's tail, write the full chapter prose. "
            "Show, do not tell. Vary prose distance. Anchor interiority in the body. Do not "
            "pad to a word count; the 800-word floor is a stub tripwire, not a goal."
        ),
    ),
    "critics": PhaseSpec(
        "critics", "Critics (show/voice/palette/continuity/naturalism)", PER_UNIT,
        rule_file="rules-critic-show.md",
        gate_phase=True,
        fallback_prompt=(
            "You are dispatching the FIVE CRITICS. Each critic receives only the chapter "
            "text + its rubric and must embed the chapter_hash. Produce a combined critic "
            "block covering show-don't-tell, voice, palette, continuity, and naturalism, "
            "each with located findings (Line N + quoted span) and a VERDICT."
        ),
    ),
    "editorial": PhaseSpec(
        "editorial", "Editorial eval (per unit)", PER_UNIT,
        rule_file="rules-editorial-eval.md",
        gate_phase=True,
        fallback_prompt=(
            "You are the EDITORIAL critic for one chapter. Read the chapter + bible only "
            "(blinded from other critics). Assess scene earnings, opening/closing, pacing, "
            "and arc advancement. Produce located findings and a VERDICT (PASS/ADVANCE/REVISE)."
        ),
    ),
    "verify_unit": PhaseSpec(
        "verify_unit", "Verify (per unit gate)", PER_UNIT,
        rule_file=None,
        gate_phase=True,
        fallback_prompt="",
    ),
    "assemble": PhaseSpec(
        "assemble", "Assemble manuscript", PROJECT,
        rule_file=None,
        gate_phase=False,
        fallback_prompt="",
    ),
    "adversarial": PhaseSpec(
        "adversarial", "Adversarial read (full manuscript)", PROJECT,
        rule_file="rules-adversarial-reader.md",
        gate_phase=False,
        fallback_prompt=(
            "You are the ADVERSARIAL READER. Read the FULL assembled manuscript as a reader "
            "would. Hunt for the fingerprints of machine prose, continuity breaks, unearned "
            "emotional turns, and padded beats. Produce located findings (quote + position) "
            "and a dimensional score out of 10."
        ),
    ),
    "finalize": PhaseSpec(
        "finalize", "Finalize (the gate)", PROJECT,
        rule_file=None,
        gate_phase=True,
        fallback_prompt="",
    ),
}


# ── Run state ────────────────────────────────────────────────────────────────

@dataclass
class RunState:
    project_path: str
    project_name: str
    started_at: str
    status: str = "running"             # running | paused | complete | failed
    current_phase: str = "bible"
    current_unit_index: int = 0         # index into units[]
    units: list[int] = field(default_factory=list)   # chapter numbers, e.g. [1,2,3]
    word_floor: int = 800
    instructions: str = ""              # user's creative brief / instructions
    phase_results: dict[str, dict] = field(default_factory=dict)     # project + closing
    unit_results: dict[int, dict] = field(default_factory=dict)      # chapter -> phase -> result
    last_error: Optional[str] = None
    updated_at: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        # JSON keys must be strings; unit_results uses int keys.
        d["unit_results"] = {str(k): v for k, v in self.unit_results.items()}
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "RunState":
        unit_results = {int(k): v for k, v in d.get("unit_results", {}).items()}
        return cls(
            project_path=d["project_path"],
            project_name=d.get("project_name", ""),
            started_at=d["started_at"],
            status=d.get("status", "running"),
            current_phase=d.get("current_phase", "bible"),
            current_unit_index=d.get("current_unit_index", 0),
            units=list(d.get("units", [])),
            word_floor=d.get("word_floor", 800),
            instructions=d.get("instructions", ""),
            phase_results=dict(d.get("phase_results", {})),
            unit_results=unit_results,
            last_error=d.get("last_error"),
            updated_at=d.get("updated_at", ""),
        )


# ── Persistence ──────────────────────────────────────────────────────────────

def _run_state_path(project: str) -> str:
    return os.path.join(project, RUN_STATE_REL)


def load_run_state(project: str) -> Optional[RunState]:
    path = _run_state_path(project)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return RunState.from_dict(json.load(f))


def save_run_state(state: RunState) -> None:
    state.updated_at = datetime.now().isoformat()
    path = _run_state_path(state.project_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)


# ── Prompt loading ───────────────────────────────────────────────────────────

def system_prompt_for(phase_key: str) -> str:
    spec = PHASE_SPECS[phase_key]
    if spec.rule_file:
        candidate = os.path.join(_RULE_DIR, spec.rule_file)
        if os.path.isfile(candidate):
            with open(candidate, "r", encoding="utf-8-sig") as f:
                return f.read()
    return spec.fallback_prompt


# ── Helpers ──────────────────────────────────────────────────────────────────

def _read_file(rel: str, project: str) -> str:
    path = os.path.join(project, rel)
    if not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read().replace("\ufeff", "")


def _write_file(rel: str, project: str, content: str) -> str:
    path = os.path.join(project, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return rel


def _chapter_rel(chapter_number: int, project: Optional[str] = None) -> str:
    """Relative path for a chapter file.

    The manifest verifier matches chapters via a glob ``{NNN}_*.md`` (note the
    underscore), so the orchestrator must both WRITE and READ files that match
    that pattern. When ``project`` is given and a matching file already exists
    on disk, return it; otherwise default to ``{NNN}_chapter.md``.
    """
    import glob as _glob
    default = os.path.join("manuscript", "chapters", f"{chapter_number:03d}_chapter.md")
    if not project:
        return default
    matches = sorted(_glob.glob(os.path.join(
        project, "manuscript", "chapters", f"{chapter_number:03d}_*.md"
    )))
    return os.path.relpath(matches[0], project) if matches else default


def _bible_context(project: str) -> str:
    """Concatenate the bible files + voice spec as planning context."""
    parts = []
    for rel in ("bible/01_concept.md", "bible/04_outline.md",
                "bible/07_format_rules.md", "bible/LOCKED_VOICE_SPEC.md"):
        text = _read_file(rel, project)
        if text:
            parts.append(f"--- {rel} ---\n{text}\n")
    return "\n".join(parts)


def _with_instructions(user_prompt: str, state: RunState) -> str:
    """Append the user's creative instructions to a phase prompt, if any."""
    if not state.instructions:
        return user_prompt
    return (
        f"{user_prompt}\n\n"
        f"--- WRITER'S INSTRUCTIONS (HONOR THESE) ---\n"
        f"{state.instructions}\n"
        f"--- END INSTRUCTIONS ---"
    )


def _phase_index(phase_key: str) -> int:
    return ALL_PHASES.index(phase_key)


def next_phase(state: RunState) -> Optional[str]:
    """Return the next phase key, or None if the run is complete."""
    cur = state.current_phase
    idx = _phase_index(cur)
    # Within per-unit loop, advance to next unit before moving to closing.
    if cur in UNIT_PHASES:
        if cur == UNIT_PHASES[-1]:           # last unit phase -> next unit or assemble
            if state.current_unit_index + 1 < len(state.units):
                return UNIT_PHASES[0]        # next chapter, back to architect
            return CLOSING_PHASES[0]         # assemble
        return UNIT_PHASES[idx - _phase_index(UNIT_PHASES[0]) + 1]
    # Project or closing phases: linear advance.
    if idx + 1 < len(ALL_PHASES):
        return ALL_PHASES[idx + 1]
    return None


# ── Gate checks ──────────────────────────────────────────────────────────────

def _gate_for_chapter(project: str, chapter_number: int, state: RunState) -> dict:
    """Run verify_completion and report a PASS/FAIL gate for one chapter."""
    manifest_path = os.path.join(project, "state", "completion_manifest.json")
    if not os.path.isfile(manifest_path):
        return {"verdict": "FAIL", "reason": "completion_manifest.json missing"}
    with open(manifest_path, "r", encoding="utf-8-sig") as f:
        manifest = json.load(f)
    expected = verify_completion._auto_detect_chapters(project) or len(state.units)
    all_pass, total, passed, failed, failures, _ = verify_completion.verify_manifest(
        project, manifest, expected, skip_lint=False
    )
    # Restrict the failures to this chapter's items so the gate isn't blocked by
    # later chapters that haven't been produced yet.
    chap_key = f"chapter_{chapter_number}"
    chap_failures = [f for f in failures if isinstance(f, dict) and f.get("chapter") == chapter_number]
    chap_failures += [f for f in failures if isinstance(f, str) and chap_key in f]
    verdict = "PASS" if not chap_failures else "FAIL"
    return {
        "verdict": verdict,
        "chapter": chapter_number,
        "chapter_failures": chap_failures,
        "manifest_total": total,
        "manifest_passed": passed,
        "manifest_failed": failed,
    }


# ── Phase executors ──────────────────────────────────────────────────────────
# Each returns a dict: {artifact, gate, meta...}

async def _exec_bible(state: RunState, project: str, model_call: ModelCall) -> dict:
    system = system_prompt_for("bible")
    user = _with_instructions(
        "Produce the bible for a new novel. Output three files delimited by markers "
        "of the form '---BIBLE-FILE: <relative path>---' followed by the file content. "
        "At minimum produce bible/01_concept.md, bible/04_outline.md, and "
        "bible/07_format_rules.md. The outline must use '## Chapter N' headings so the "
        "chapter count can be detected.",
        state,
    )
    reply = await model_call(system, user)
    artifacts = _split_bible_reply(reply, project)
    return {"artifacts": artifacts, "raw_preview": reply[:400]}


def _split_bible_reply(reply: str, project: str) -> list[str]:
    """Parse '---BIBLE-FILE: rel---' delimited sections and write each to disk.

    If no delimiters are found, write the whole reply to bible/04_outline.md so the
    manifest builder has something to count (best-effort fallback).
    """
    import re
    pattern = re.compile(r"-{2,}\s*BIBLE[- ]?FILE\s*[:=]\s*([^\n]+?)\s*-{2,}", re.IGNORECASE)
    parts = pattern.split(reply)
    artifacts: list[str] = []
    if len(parts) >= 3:
        # split yields [pre, path1, body1, path2, body2, ...]
        base = os.path.realpath(project) + os.sep
        i = 1
        while i + 1 < len(parts):
            rel = parts[i].strip().lstrip("/").strip()
            body = parts[i + 1].strip()
            # Sanitize: keep only the path-like first token.
            rel = rel.split()[0] if rel else rel
            # Bounds-check: the resolved path must stay inside the project.
            # Catches embedded traversal (bible/../../etc), absolute paths,
            # and UNC/drive paths the LLM might emit.
            if rel:
                target = os.path.realpath(os.path.join(project, rel))
                if target.startswith(base):
                    artifacts.append(_write_file(rel, project, body + "\n"))
            i += 2
    if not artifacts:
        artifacts.append(_write_file("bible/04_outline.md", project, reply.strip() + "\n"))
    return artifacts


async def _exec_voice(state: RunState, project: str, model_call: ModelCall) -> dict:
    system = system_prompt_for("voice")
    bible = _bible_context(project)
    user = _with_instructions(
        f"--- BIBLE ---\n{bible}\n--- END ---\n\n"
        "Produce a comprehensive LOCKED_VOICE_SPEC for this novel. The spec must cover:\n"
        "1. **Narrative POV** — first/third person, omniscient/limited, tense\n"
        "2. **Prose distance** — close (internal), middle (observational), or lyric (poetic)\n"
        "3. **Sentence rhythm** — short/punchy vs. long/flowing, paragraph density\n"
        "4. **Dialogue style** — how characters speak, register differences between characters\n"
        "5. **Description conventions** — body anchors (hands, spine, throat), sensory priorities\n"
        "6. **Thematic vocabulary** — recurring words, metaphors, tonal palette\n"
        "7. **Chapter structure** — scene/sequel ratio, opening/closing conventions\n"
        "8. **Example passage** — 2-3 paragraphs demonstrating the locked voice\n\n"
        "Write the full spec to bible/LOCKED_VOICE_SPEC.md. Be thorough — this spec "
        "governs every chapter the writer produces.",
        state,
    )
    reply = await model_call(system, user)
    rel = _write_file("bible/LOCKED_VOICE_SPEC.md", project, reply.strip() + "\n")
    return {"artifact": rel, "raw_preview": reply[:400]}


async def _exec_editorial_lock(state: RunState, project: str, model_call: ModelCall) -> dict:
    system = system_prompt_for("editorial_lock")
    bible = _bible_context(project)
    user = _with_instructions(
        f"--- BIBLE ---\n{bible}\n--- END ---\n\nReview and lock the outline.",
        state,
    )
    reply = await model_call(system, user)
    rel = _write_file(os.path.join("coverage_reports", "editorial_outline_lock.md"),
                      project, reply.strip() + "\n")
    # Build the manifest now that the outline is locked.
    outline = _locate_outline(project)
    chapter_count = build_manifest.count_chapters_in_outline(outline) if outline else 0
    manifest_built = None
    if chapter_count > 0:
        manifest = build_manifest.build_manifest(
            chapter_count, state.project_name, "novel", state.word_floor
        )
        mpath = os.path.join(project, "state", "completion_manifest.json")
        os.makedirs(os.path.dirname(mpath), exist_ok=True)
        with open(mpath, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        state.units = list(range(1, chapter_count + 1))
        manifest_built = {
            "chapters_detected": chapter_count,
            "total_items": sum(len(s["items"]) for s in manifest["sections"]),
            "manifest_path": os.path.relpath(mpath, project),
        }
    return {"artifact": rel, "manifest": manifest_built, "raw_preview": reply[:400]}


def _locate_outline(project: str) -> Optional[str]:
    for cand in (os.path.join(project, "bible", "04_outline.md"),
                 os.path.join(project, "bible", "04_season_arc.md")):
        if os.path.isfile(cand):
            return cand
    return None


def _prior_chapter_tail(project: str, chapter_number: int) -> str:
    if chapter_number <= 1:
        return ""
    prev = chapter_number - 1
    text = _read_file(_chapter_rel(prev, project), project)
    if not text:
        return ""
    return text[-1200:]


async def _exec_architect(state: RunState, project: str, model_call: ModelCall) -> dict:
    chapter = state.units[state.current_unit_index]
    system = system_prompt_for("architect")
    characters = profile_context.character_context(project, "architect")
    user = _with_instructions(
        f"--- BIBLE ---\n{_bible_context(project)}\n--- END ---\n\n"
        f"{characters + chr(10)*2 if characters else ''}"
        f"--- PRIOR CHAPTER TAIL ---\n{_prior_chapter_tail(project, chapter)}\n--- END ---\n\n"
        f"Plan chapter {chapter} now.",
        state,
    )
    reply = await model_call(system, user)
    rel = _write_file(os.path.join("critic_outputs", f"chapter_{chapter}_plan.md"),
                      project, reply.strip() + "\n")
    return {"artifact": rel, "chapter": chapter, "raw_preview": reply[:400]}


async def _exec_writer(state: RunState, project: str, model_call: ModelCall) -> dict:
    chapter = state.units[state.current_unit_index]
    system = system_prompt_for("writer")
    plan = _read_file(os.path.join("critic_outputs", f"chapter_{chapter}_plan.md"), project)
    characters = profile_context.character_context(project, "writer")
    user = _with_instructions(
        f"--- ARCHITECT PLAN ---\n{plan}\n--- END ---\n\n"
        f"{characters + chr(10)*2 if characters else ''}"
        f"--- PRIOR CHAPTER TAIL ---\n{_prior_chapter_tail(project, chapter)}\n--- END ---\n\n"
        f"Write the full prose for chapter {chapter} now.",
        state,
    )
    reply = await model_call(system, user)
    body = strip_artifacts(reply).strip() + "\n"
    rel = _write_file(_chapter_rel(chapter), project, body)
    from .word_count import count_words
    wc = count_words(os.path.join(project, rel))
    return {"artifact": rel, "chapter": chapter, "word_count": wc, "raw_preview": reply[:400]}


async def _exec_critics(state: RunState, project: str, model_call: ModelCall) -> dict:
    """Run all five critics + editorial via the existing critic runner contract.

    Reuses app.pipeline.critics.compose_artifact so the artifacts are gate-valid
    (hash embedded, located findings, the right on-disk path). The model reply
    for each critic comes from the injected ``model_call`` so tests need no key.
    """
    from .lint_suite import hash_chapter
    from . import critics as critics_mod

    chapter = state.units[state.current_unit_index]
    chapter_path = os.path.join(project, _chapter_rel(chapter, project))
    chash = hash_chapter(chapter_path)
    # Phase G: per-critic profile context. The voice critic checks dialogue
    # against DECLARED voice registers; the continuity critic gets continuity
    # profile context (core/present/hidden). Other critics are blinded (chapter
    # text + rubric only), per the Open-Write critic architecture.
    per_critic_context = {
        "voice": profile_context.voice_registers_context(project),
        "continuity": profile_context.character_context(project, "continuity"),
    }
    results = []
    for ctype in (*critics_mod.CRITIC_TYPES, critics_mod.EDITORIAL_TYPE):
        system = critics_mod._SYSTEM_PROMPTS[ctype]
        # Build the chapter context the critic runner would have assembled.
        from .word_count import strip_artifacts as _sa
        chapter_text = _sa(_read_file(_chapter_rel(chapter, project), project))
        ctx = per_critic_context.get(ctype, "")
        ctx_block = f"\n{ctx}\n" if ctx else ""
        user = (
            f"chapter_hash: {chash}\n\n{ctx_block}"
            f"--- CHAPTER ---\n{chapter_text}\n--- END CHAPTER ---\n\n"
            f"Review this chapter now. Begin your report with 'chapter_hash: {chash}', "
            f"include a ## Findings section with at least three located findings "
            f"(Line N + quoted span), then VERDICT."
        )
        reply = await model_call(system, user)
        comp = critics_mod.compose_artifact(ctype, chapter, reply, chash, project)
        results.append(comp)
    return {"critics": results, "chapter": chapter}


async def _exec_editorial(state: RunState, project: str, model_call: ModelCall) -> dict:
    # The editorial critic is already run inside _exec_critics; this phase is a
    # structural placeholder that confirms the editorial artifact exists. We keep
    # it as a distinct phase so the frontend can surface a human-approval gate.
    chapter = state.units[state.current_unit_index]
    rel = os.path.join("coverage_reports", f"editorial_report_ch{chapter}.md")
    return {"artifact": rel, "chapter": chapter, "note": "editorial already produced during critics phase"}


async def _exec_verify_unit(state: RunState, project: str, model_call: ModelCall) -> dict:
    chapter = state.units[state.current_unit_index]
    gate = _gate_for_chapter(project, chapter, state)
    return {"gate": gate, "chapter": chapter}


async def _exec_assemble(state: RunState, project: str, model_call: ModelCall) -> dict:
    """Concatenate chapter files into manuscript/novel.md (title block + chapters)."""
    parts = [f"# {state.project_name}\n"]
    for ch in state.units:
        text = _read_file(_chapter_rel(ch), project)
        parts.append(f"\n---\n\n## Chapter {ch}\n\n{text.strip()}\n")
    assembled = "\n".join(parts) + "\n"
    rel = _write_file(os.path.join("manuscript", "novel.md"), project, assembled)
    from .word_count import count_words
    wc = count_words(os.path.join(project, rel))
    return {"artifact": rel, "word_count": wc}


async def _exec_adversarial(state: RunState, project: str, model_call: ModelCall) -> dict:
    system = system_prompt_for("adversarial")
    manuscript = _read_file("manuscript/novel.md", project)
    user = _with_instructions(
        f"--- FULL MANUSCRIPT ---\n{manuscript}\n--- END ---\n\n"
        "Read the full manuscript and produce the adversarial report with located "
        "findings and a dimensional score out of 10.",
        state,
    )
    reply = await model_call(system, user)
    rel = _write_file(os.path.join("coverage_reports", "adversarial_read.md"),
                      project, reply.strip() + "\n")
    return {"artifact": rel, "raw_preview": reply[:400]}


async def _exec_finalize(state: RunState, project: str, model_call: ModelCall) -> dict:
    result = finalize_mod.finalize(project)
    return {"finalize_result": result}


_EXECUTORS: dict[str, Callable] = {
    "bible": _exec_bible,
    "voice": _exec_voice,
    "editorial_lock": _exec_editorial_lock,
    "architect": _exec_architect,
    "writer": _exec_writer,
    "critics": _exec_critics,
    "editorial": _exec_editorial,
    "verify_unit": _exec_verify_unit,
    "assemble": _exec_assemble,
    "adversarial": _exec_adversarial,
    "finalize": _exec_finalize,
}


# ── Public API ───────────────────────────────────────────────────────────────

def start_run(project: str, project_name: str = "", word_floor: int = 800,
              units: Optional[list[int]] = None, instructions: str = "") -> RunState:
    """Initialize (or reset) a pipeline run. Returns the fresh RunState."""
    project = os.path.abspath(project)
    name = project_name or os.path.basename(project.rstrip("/\\"))
    state = RunState(
        project_path=project,
        project_name=name,
        started_at=datetime.now().isoformat(),
        word_floor=word_floor,
        instructions=instructions.strip(),
        current_phase="bible",
        current_unit_index=0,
    )
    # If a manifest already exists, pre-populate the unit list from it.
    manifest_path = os.path.join(project, "state", "completion_manifest.json")
    if units:
        state.units = list(units)
    elif os.path.isfile(manifest_path):
        outline = _locate_outline(project)
        if outline:
            n = build_manifest.count_chapters_in_outline(outline)
            state.units = list(range(1, n + 1))
    save_run_state(state)
    return state


# Phases that author prose/plan run on the "author" model; critic/editorial
# phases run on the "critic" model (Open-Write A/B: a different model for
# critics attacks self-recognition bias). verify_unit/finalize make no call.
AUTHOR_PHASES = {"bible", "voice", "editorial_lock", "architect", "writer",
                 "assemble", "adversarial"}
CRITIC_PHASES = {"critics", "editorial"}


def role_for_phase(phase: str) -> str:
    """Map a phase key to a model role ("author" | "critic")."""
    return "critic" if phase in CRITIC_PHASES else "author"


# A resolver maps a role tag to a model call. The orchestrator stays
# provider-agnostic -- the route layer builds this from provider config.
ModelResolver = Callable[[str], ModelCall]


async def advance_phase(project: str, resolve_call: ModelResolver) -> dict:
    """Run exactly ONE phase (the current one) and return its result + gate.

    ``resolve_call`` maps a role ("author" or "critic") to an async
    ``model_call(system, user) -> str``. The author model drives bible/voice/
    architect/writer/assemble/adversarial; the critic model drives the critic
    and editorial phases (Open-Write A/B).

    Persists the updated RunState. Sets state.status to "failed" on an exception
    and re-raises after recording. On success, advances current_phase (and the
    unit index when leaving the per-unit loop) so the next call continues.
    """
    project = os.path.abspath(project)
    state = load_run_state(project)
    if state is None:
        raise RuntimeError("No pipeline run in progress. Call start_run first.")
    if state.status == "complete":
        return {"phase": "complete", "message": "Run already complete.", "state": state.to_dict()}

    phase = state.current_phase
    # Guard: per-unit phases need a non-empty chapter list. If editorial_lock
    # failed to detect chapters (e.g. the bible outline used a non-standard
    # heading style), fail the run with an actionable message instead of an
    # IndexError deep inside an executor.
    if phase in UNIT_PHASES and not state.units:
        msg = ("Cannot run a per-unit phase: no chapters detected. Ensure the "
               "outline uses '## Chapter N' headings so the manifest builder "
               "can count chapters, then restart the run.")
        state.status = "failed"
        state.last_error = msg
        save_run_state(state)
        raise RuntimeError(msg)

    model_call = resolve_call(role_for_phase(phase))
    executor = _EXECUTORS[phase]
    try:
        result = await executor(state, project, model_call)
    except Exception as exc:
        state.status = "failed"
        state.last_error = f"{type(exc).__name__}: {exc}"
        save_run_state(state)
        raise

    # Record the result.
    _record_result(state, phase, result)

    # Run the gate for gate_phase entries (verify_unit/finalize already embed it).
    spec = PHASE_SPECS[phase]
    gate = result.get("gate")
    if spec.gate_phase and gate is None:
        # writer / critics / editorial: gate is chapter verify for the current unit.
        if phase in ("writer", "critics", "editorial"):
            chapter = state.units[state.current_unit_index]
            gate = _gate_for_chapter(project, chapter, state)
        elif phase == "finalize":
            gate = result.get("finalize_result")
    result["gate"] = gate

    # Advance the cursor for the next call.
    nxt = next_phase(state)
    if nxt is None:
        state.status = "complete"
    else:
        # If we're crossing from the last unit phase to the next chapter's first,
        # increment the unit index.
        if phase == "verify_unit" and nxt == UNIT_PHASES[0]:
            state.current_unit_index += 1
        # If we're crossing from project phases into the per-unit loop, reset index.
        if phase in PROJECT_PHASES and nxt == UNIT_PHASES[0]:
            state.current_unit_index = 0
        state.current_phase = nxt
    save_run_state(state)

    return {
        "phase": phase,
        "phase_label": PHASE_SPECS[phase].label,
        "result": result,
        "next_phase": nxt,
        "next_phase_label": PHASE_SPECS[nxt].label if nxt else None,
        "state": state.to_dict(),
    }


def _record_result(state: RunState, phase: str, result: dict) -> None:
    if phase in PROJECT_PHASES or phase in CLOSING_PHASES:
        state.phase_results[phase] = result
    else:
        chapter = state.units[state.current_unit_index]
        bucket = state.unit_results.setdefault(chapter, {})
        bucket[phase] = result


def get_phase_output(project: str, phase: str, chapter: Optional[int] = None) -> dict:
    """Return the recorded result for a phase (optionally for a specific chapter)."""
    project = os.path.abspath(project)
    state = load_run_state(project)
    if state is None:
        return {}
    if phase in PROJECT_PHASES or phase in CLOSING_PHASES:
        return state.phase_results.get(phase, {})
    if chapter is not None:
        return state.unit_results.get(chapter, {}).get(phase, {})
    return {}
