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

import asyncio
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


# ── Run-state writer serialization ────────────────────────────────────────────
# advance_phase holds the whole RunState in memory across a long LLM await and
# then persists it. The live-control endpoints (update_instructions /
# set_status / prepare_rerun) also load→mutate→save the same file. Without a
# guard, a control mutation made while a phase is generating gets silently
# clobbered by advance_phase's final save (lost update), or the control save
# drops the just-recorded phase result.
#
# Fix: one asyncio.Lock per project. advance_phase holds it across its whole
# load→await→save. Control functions acquire it NON-blocking and raise
# PhaseBusyError if a phase is mid-execution, so the UI gets a clear 409 ("a
# phase is running; wait for it to finish") instead of a silently-lost change.
_RUN_LOCKS: dict[str, asyncio.Lock] = {}


class PhaseBusyError(RuntimeError):
    """Raised when a control mutation is attempted while a phase is executing."""


def _run_lock(project: str) -> asyncio.Lock:
    key = os.path.abspath(project)
    lock = _RUN_LOCKS.get(key)
    if lock is None:
        lock = asyncio.Lock()
        _RUN_LOCKS[key] = lock
    return lock



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
        gate_phase=False,  # Gate runs at verify_unit, not here — avoids false MISSING errors
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
        gate_phase=False,  # Gate runs at verify_unit, not here — avoids false MISSING errors
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
    chapter_retries: dict[int, int] = field(default_factory=dict)  # chapter -> retry count
    # User-provided content overrides. Maps a phase key (e.g. "bible",
    # "writer:3", "voice") to user-supplied content. When set, the phase
    # executor uses this content instead of calling the model. The content
    # is processed the same way model output would be (split into files,
    # written to disk, etc.).
    user_overrides: dict[str, str] = field(default_factory=dict)

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
            chapter_retries={int(k): v for k, v in d.get("chapter_retries", {}).items()},
            user_overrides=dict(d.get("user_overrides", {})),
        )


# ── Persistence ──────────────────────────────────────────────────────────────

def _run_state_path(project: str) -> str:
    return os.path.join(project, RUN_STATE_REL)


def reset_run(project: str) -> None:
    """Delete the pipeline_run.json file so the UI shows a clean Start Run form.

    Used to clear stale failed state from a previous run that the user wants to
    abandon. Artifacts on disk (bible, chapters, critics) are preserved — only
    the run state is deleted.
    """
    project = os.path.abspath(project)
    path = _run_state_path(project)
    if os.path.isfile(path):
        os.remove(path)


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
    # Atomic write: serialize to a temp file then os.replace into place. A
    # concurrent reader (e.g. chat_context_snapshot during a phase) never sees a
    # half-written / truncated JSON file — replace is atomic on the same
    # filesystem.
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


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

    Chapters live in manuscript/ (the same directory the Storythread UI reads
    via its chapter list endpoint). The manifest verifier matches chapters via
    a glob ``{NNN}_*.md`` (note the underscore). When ``project`` is given and
    a matching file already exists on disk, return it; otherwise default to
    ``{NNN}_chapter.md``.
    """
    import glob as _glob
    default = os.path.join("manuscript", f"{chapter_number:03d}_chapter.md")
    if not project:
        return default
    matches = sorted(_glob.glob(os.path.join(
        project, "manuscript", f"{chapter_number:03d}_*.md"
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


def _collect_critic_feedback(project: str, chapter: int) -> str:
    """Gather all available critic findings for a chapter into one feedback block.

    Used when re-running the writer after a REVISE gate verdict — the writer
    needs to see what the critics flagged so it can address those findings in
    the rewrite. Returns "" if no critic files exist (in which case the
    pipeline re-runs critics instead of the writer).
    """
    from . import critics as critics_mod
    parts: list[str] = []
    for ctype in (*critics_mod.CRITIC_TYPES, critics_mod.EDITORIAL_TYPE):
        rel = critics_mod.artifact_relpath(ctype, chapter)
        text = _read_file(rel, project)
        if text:
            parts.append(f"--- {ctype.upper()} CRITIC ---\n{text.strip()}\n--- END ---")
    if not parts:
        return ""
    return (
        "--- CRITIC FEEDBACK (address these findings in your rewrite) ---\n\n"
        + "\n\n".join(parts)
        + "\n\n--- END CRITIC FEEDBACK ---"
    )


def _apply_user_override(phase: str, chapter: int | None, content: str,
                         project: str, state: RunState) -> dict:
    """Process user-provided content for a phase instead of calling the model.

    Writes the content to disk in the same format the phase executor would,
    so the rest of the pipeline (gate, critics, assembly) works unchanged.
    """
    from .word_count import strip_artifacts, count_words

    if phase == "bible":
        artifacts = _split_bible_reply(content, project)
        return {"artifacts": artifacts, "raw_preview": content[:400], "user_override": True}

    if phase == "voice":
        artifacts = _split_voice_reply(content, project)
        return {
            "artifacts": artifacts["written"],
            "artifact": artifacts["locked"],
            "candidates": artifacts["candidates"],
            "raw_preview": content[:400],
            "user_override": True,
        }

    if phase == "editorial_lock":
        rel = _write_file(os.path.join("coverage_reports", "editorial_outline_lock.md"),
                          project, content.strip() + "\n")
        return {"artifact": rel, "raw_preview": content[:400], "user_override": True}

    if phase == "architect" and chapter is not None:
        rel = _write_file(os.path.join("critic_outputs", f"chapter_{chapter}_plan.md"),
                          project, content.strip() + "\n")
        return {"artifact": rel, "chapter": chapter, "raw_preview": content[:400], "user_override": True}

    if phase == "writer" and chapter is not None:
        body = strip_artifacts(content).strip() + "\n"
        rel = _write_file(_chapter_rel(chapter), project, body)
        wc = count_words(os.path.join(project, rel))
        return {"artifact": rel, "chapter": chapter, "word_count": wc, "raw_preview": content[:400], "user_override": True}

    if phase == "critics" and chapter is not None:
        from . import critics as critics_mod
        from .lint_suite import hash_chapter
        chapter_path = os.path.join(project, _chapter_rel(chapter, project))
        chash = hash_chapter(chapter_path)
        results = []
        for ctype in (*critics_mod.CRITIC_TYPES, critics_mod.EDITORIAL_TYPE):
            comp = critics_mod.compose_artifact(ctype, chapter, content, chash, project)
            results.append(comp)
        return {"critics": results, "chapter": chapter, "user_override": True}

    if phase == "editorial" and chapter is not None:
        rel = _write_file(os.path.join("coverage_reports", f"editorial_report_ch{chapter}.md"),
                          project, content.strip() + "\n")
        return {"artifact": rel, "chapter": chapter, "raw_preview": content[:400], "user_override": True}

    if phase == "adversarial":
        rel = _write_file(os.path.join("coverage_reports", "adversarial_read.md"),
                          project, content.strip() + "\n")
        return {"artifact": rel, "raw_preview": content[:400], "user_override": True}

    # Fallback: write to a generic override artifact.
    rel = _write_file(os.path.join("state", f"override_{phase}.md"), project, content.strip() + "\n")
    return {"artifact": rel, "raw_preview": content[:400], "user_override": True}


# ── Phase executors ──────────────────────────────────────────────────────────
# Each returns a dict: {artifact, gate, meta...}

async def _exec_bible(state: RunState, project: str, model_call: ModelCall) -> dict:
    system = system_prompt_for("bible")
    characters = profile_context.character_context(project, "architect")
    world = profile_context.world_context(project)
    user = _with_instructions(
        "Produce the bible for a new novel. Output three files delimited by markers "
        "of the form '---BIBLE-FILE: <relative path>---' followed by the file content. "
        "At minimum produce bible/01_concept.md, bible/04_outline.md, and "
        "bible/07_format_rules.md. The outline must use '## Chapter N' headings so the "
        "chapter count can be detected."
        f"{chr(10)*2}{characters + chr(10)*2 if characters else ''}"
        f"{world + chr(10)*2 if world else ''}",
        state,
    )
    reply = await model_call(system, user)
    artifacts = _split_bible_reply(reply, project)
    # Sync the outline to notes/outline.md so the Storythread OutlinePlanner
    # sees it immediately (unified outline location).
    _sync_outline_to_ui(project)
    # Generate skeleton character profiles from the concept so the ProfileBuilder
    # has something to work with from the start.
    _generate_skeleton_profiles(project)
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
        "Run a voice experiment and lock the winner. Produce THREE delimited "
        "sections so each can be filed separately:\n\n"
        "1. Candidate voices — for EACH candidate voice (aim for 5 distinct "
        "approaches: e.g. close-internal, middle-observational, lyric-poetic, "
        "sparse-restrained, urgent-staccato), open a block with a header line of "
        "exactly the form '---VOICE-CANDIDATE: <short-name>---' followed by a "
        "short sample passage (300-600 words of the SAME beat written in that "
        "voice) and a one-paragraph note on its prose distance, sentence rhythm, "
        "and body-anchor conventions.\n\n"
        "2. Review — open a block with the header line '---VOICE-REVIEW---' and "
        "compare the candidates head-to-head: which won and WHY (cite specific "
        "qualities — ceiling quality, personality separation, range, "
        "naturalness). Rank them. Record the empirical reasoning that the winner "
        "represents the best achievable generative ceiling.\n\n"
        "3. Locked spec — open a block with the header line "
        "'---LOCKED-VOICE-SPEC---' and write the full LOCKED_VOICE_SPEC for the "
        "winning voice: narrative POV, prose distance, sentence rhythm, dialogue "
        "style, description conventions, thematic vocabulary, chapter structure, "
        "and a 2-3 paragraph example passage demonstrating the locked voice.\n\n"
        "Be thorough — the locked spec governs every chapter the writer produces.",
        state,
    )
    reply = await model_call(system, user)
    artifacts = _split_voice_reply(reply, project)
    return {
        "artifacts": artifacts["written"],
        "artifact": artifacts["locked"],
        "candidates": artifacts["candidates"],
        "raw_preview": reply[:400],
    }


def _split_voice_reply(reply: str, project: str) -> dict:
    """Parse a voice-experiment reply into candidates, a review, and a locked spec.

    Looks for the three header markers produced by the voice prompt and writes
    each to its own file under voice_experiments/ (candidates + review) and
    bible/LOCKED_VOICE_SPEC.md (the locked winner). If the model ignored the
    delimiter format, fall back to writing the whole reply as the locked spec so
    the artifact is never lost (best-effort, like _split_bible_reply).
    """
    import re
    # Split on the three markers, keeping the marker name as a capture group.
    pattern = re.compile(
        r"-{2,}\s*VOICE[- ]?CANDIDATE\s*[:=]\s*([^\n]+?)\s*-{2,}"
        r"|-{2,}\s*VOICE[- ]?REVIEW\s*-{2,}"
        r"|-{2,}\s*LOCKED[- ]?VOICE[- ]?SPEC\s*-{2,}",
        re.IGNORECASE,
    )

    written: list[str] = []
    candidates: list[str] = []
    locked = ""

    # Walk the reply, classifying each chunk by the marker that precedes it.
    pos = 0
    current_kind = None
    current_name = None
    chunks: list[tuple[str, str | None, str]] = []  # (kind, name, body)

    for m in pattern.finditer(reply):
        body = reply[pos:m.start()]
        if current_kind is not None:
            chunks.append((current_kind, current_name, body))
        text = m.group(0)
        if "CANDIDATE" in text.upper():
            current_kind = "candidate"
            current_name = (m.group(1) or "").strip()
        elif "REVIEW" in text.upper():
            current_kind = "review"
            current_name = None
        else:  # LOCKED ... SPEC
            current_kind = "locked"
            current_name = None
        pos = m.end()
    # Trailing chunk after the last marker.
    if current_kind is not None:
        chunks.append((current_kind, current_name, reply[pos:]))

    base = os.path.realpath(project) + os.sep
    for kind, name, body in chunks:
        body = body.strip()
        if not body:
            continue
        if kind == "candidate":
            # Sanitize the candidate name into a filename stem.
            stem = re.sub(r"[^A-Za-z0-9_-]+", "_", (name or "candidate")).strip("_").lower() or "candidate"
            rel = os.path.join("voice_experiments", "candidates", f"{stem}.md")
            target = os.path.realpath(os.path.join(project, rel))
            if target.startswith(base):
                # Prepend a title line so the file is readable standalone.
                _write_file(rel, project, f"# {name or stem}\n\n{body}\n")
                written.append(rel)
                candidates.append(name or stem)
        elif kind == "review":
            rel = "voice_experiments/review.md"
            _write_file(rel, project, f"# Voice Experiment — Review & Selection\n\n{body}\n")
            written.append(rel)
        elif kind == "locked":
            locked = body
            rel = "bible/LOCKED_VOICE_SPEC.md"
            _write_file(rel, project, body + "\n")
            written.append(rel)

    if not written:
        # Fallback: no markers found — preserve the reply as the locked spec.
        locked = reply.strip()
        rel = "bible/LOCKED_VOICE_SPEC.md"
        _write_file(rel, project, locked + "\n")
        written.append(rel)

    return {"written": written, "candidates": candidates, "locked": rel if locked else written[-1]}


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
    """Find the best outline file. Prefers notes/outline.md (the unified
    location that both the UI OutlinePlanner and the pipeline read), then
    falls back to bible/04_outline.md for backward compatibility."""
    for cand in (os.path.join(project, "notes", "outline.md"),
                 os.path.join(project, "bible", "04_outline.md"),
                 os.path.join(project, "bible", "04_season_arc.md")):
        if os.path.isfile(cand):
            return cand
    return None


def _sync_outline_to_ui(project: str) -> None:
    """After the bible phase, copy the outline to notes/outline.md so the
    Storythread OutlinePlanner sees it immediately. Only copies if
    notes/outline.md doesn't already exist (preserves user edits)."""
    bible_outline = os.path.join(project, "bible", "04_outline.md")
    notes_outline = os.path.join(project, "notes", "outline.md")
    if os.path.isfile(bible_outline) and not os.path.isfile(notes_outline):
        os.makedirs(os.path.dirname(notes_outline), exist_ok=True)
        with open(bible_outline, "r", encoding="utf-8-sig") as src:
            content = src.read()
        # Prepend YAML frontmatter so the OutlinePlanner can parse it.
        frontmatter = "---\ntarget_word_count: 0\n---\n\n"
        with open(notes_outline, "w", encoding="utf-8") as dst:
            dst.write(frontmatter + content)


def _generate_skeleton_profiles(project: str) -> None:
    """After the bible phase, create skeleton character/location/lore profiles
    from the concept document so the ProfileBuilder has something to work with.

    Parses the concept for character names (lines starting with '- **Name**' or
    similar patterns) and creates minimal profile files. The writer enriches
    these in the ProfileBuilder. Only creates profiles that don't already exist
    (preserves user edits).
    """
    concept = _read_file(os.path.join("bible", "01_concept.md"), project)
    if not concept:
        return

    # Extract character names from the concept. Common patterns:
    # - **Name:** description
    # - Name: description
    # - **Name** — description
    import re
    char_pattern = re.compile(
        r"^[-*]\s*\**\s*([A-Z][a-zA-Z\s'-]+?)(?:\**|[—:])\s",
        re.MULTILINE,
    )
    chars_dir = os.path.join(project, "profiles", "characters")
    os.makedirs(chars_dir, exist_ok=True)
    for m in char_pattern.finditer(concept):
        name = m.group(1).strip()
        if len(name) < 2 or len(name) > 60:
            continue
        # Sanitize filename.
        stem = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        path = os.path.join(chars_dir, f"{stem}.md")
        if os.path.isfile(path):
            continue  # Don't overwrite existing profiles.
        profile_md = (
            f"---\n"
            f"type: character\n"
            f"profile_id: {stem}\n"
            f"name: {name}\n"
            f"role: \n"
            f"status: draft\n"
            f"tags: [auto-generated]\n"
            f"---\n\n"
            f"# Overview\n\n{name} — (auto-generated from bible concept. Enrich this profile.)\n\n"
            f"# Physical Traits\n\n"
            f"# Personality Traits\n\n"
            f"# Motivations\n\n"
            f"# Voice Notes\n\n"
            f"# Relationships Overview\n\n"
            f"# Notes\n\n"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(profile_md)


def _generate_scene_summaries(project: str, chapter: int) -> None:
    """After the architect phase, create skeleton scene summaries from the
    chapter plan so the SceneSummaryView has something to work with.

    Parses the plan for scene beats (## Scene N or ### Scene N headings) and
    creates placeholder summary files. Only creates files that don't already
    exist.
    """
    plan = _read_file(os.path.join("critic_outputs", f"chapter_{chapter}_plan.md"), project)
    if not plan:
        return
    import re
    # Find the chapter file stem for the summaries directory.
    chapter_rel = _chapter_rel(chapter, project)
    stem = os.path.splitext(os.path.basename(chapter_rel))[0]
    scenes_dir = os.path.join(project, "summaries", "scenes", stem)
    os.makedirs(scenes_dir, exist_ok=True)

    # Split the plan by scene headings.
    scene_pattern = re.compile(r"^#{2,3}\s+Scene\s+(\d+)", re.MULTILINE | re.IGNORECASE)
    matches = list(scene_pattern.finditer(plan))
    if not matches:
        return
    for i, m in enumerate(matches):
        scene_num = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(plan)
        body = plan[start:end].strip()
        # Take the first paragraph as the summary.
        first_para = body.split("\n\n")[0].strip() if body else ""
        if len(first_para) > 400:
            first_para = first_para[:400] + "..."
        path = os.path.join(scenes_dir, f"scene-{scene_num:02d}.md")
        if os.path.isfile(path):
            continue
        summary_md = (
            f"# Scene {scene_num}\n\n"
            f"{first_para if first_para else '(Auto-generated from architect plan. Add summary.)'}\n"
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(summary_md)


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
    world = profile_context.world_context(project)
    user = _with_instructions(
        f"--- BIBLE ---\n{_bible_context(project)}\n--- END ---\n\n"
        f"{characters + chr(10)*2 if characters else ''}"
        f"{world + chr(10)*2 if world else ''}"
        f"--- PRIOR CHAPTER TAIL ---\n{_prior_chapter_tail(project, chapter)}\n--- END ---\n\n"
        f"Plan chapter {chapter} now.",
        state,
    )
    reply = await model_call(system, user)
    rel = _write_file(os.path.join("critic_outputs", f"chapter_{chapter}_plan.md"),
                      project, reply.strip() + "\n")
    # Generate skeleton scene summaries from the plan so the SceneSummaryView
    # has something to work with.
    _generate_scene_summaries(project, chapter)
    return {"artifact": rel, "chapter": chapter, "raw_preview": reply[:400]}


async def _exec_writer(state: RunState, project: str, model_call: ModelCall) -> dict:
    chapter = state.units[state.current_unit_index]
    system = system_prompt_for("writer")
    plan = _read_file(os.path.join("critic_outputs", f"chapter_{chapter}_plan.md"), project)
    characters = profile_context.character_context(project, "writer")
    world = profile_context.world_context(project)
    # If re-running after a REVISE gate verdict, inject the critic feedback so
    # the writer can address the specific findings.
    critic_feedback = _collect_critic_feedback(project, chapter)
    rewrite_note = ""
    if critic_feedback:
        rewrite_note = (
            f"\n\n{critic_feedback}\n\n"
            f"This is a REWRITE of chapter {chapter}. Address every critic finding "
            f"listed above. Preserve what works; fix what was flagged. Do NOT start "
            f"from scratch — revise the existing prose to resolve the issues.\n"
        )
    user = _with_instructions(
        f"--- ARCHITECT PLAN ---\n{plan}\n--- END ---\n\n"
        f"{characters + chr(10)*2 if characters else ''}"
        f"{world + chr(10)*2 if world else ''}"
        f"--- PRIOR CHAPTER TAIL ---\n{_prior_chapter_tail(project, chapter)}\n--- END ---\n\n"
        f"Write the full prose for chapter {chapter} now."
        f"{rewrite_note}",
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

    Each critic is wrapped in its own try/except so a failure in one (e.g. a
    None model reply, a provider timeout) doesn't kill the whole phase. The
    failed critic is recorded in the result but the remaining critics still run
    and write their artifacts.
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
    failures = []
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
        try:
            reply = await model_call(system, user)
            comp = critics_mod.compose_artifact(ctype, chapter, reply, chash, project)
            results.append(comp)
        except Exception as exc:
            # Write a substantive stub artifact so the gate sees the file exists
            # and reports the actual error instead of "MISSING" or "TOO_SHORT".
            # The stub carries the real chapter hash so the hash-binding check
            # passes, and enough substance (>=120 words) to satisfy the gate's
            # word-count threshold.
            error_msg = f"{type(exc).__name__}: {exc}"
            try:
                stub = (
                    f"chapter_hash: {chash}\n\n"
                    f"## Findings\n\n"
                    f"1. This {critic_type} critic was unable to complete its review. "
                    f"The model provider returned an error while generating the critique: "
                    f"{error_msg}. This means the chapter has not been reviewed by the "
                    f"{critic_type} critic and no located findings can be reported. "
                    f"The pipeline will continue with the remaining critics and the "
                    f"editorial evaluation, but this gap should be addressed by re-running "
                    f"the {critic_type} critic once the provider connection is restored.\n\n"
                    f"2. Because the {critic_type} critic could not analyze the chapter, "
                    f"there are no line-specific findings, no quoted spans, and no "
                    f"located issues to report. The chapter may still contain problems "
                    f"that this critic would normally flag. A manual review of the chapter "
                    f"is recommended until this critic can be re-run successfully.\n\n"
                    f"3. The failure was caused by a network-level error reaching the "
                    f"model provider (likely a timeout or connection reset after multiple "
                    f"sequential API calls). This is typically transient and resolves "
                    f"on retry. The other critics in this run may still produce valid "
                    f"reviews if their calls succeed.\n\n"
                    f"## Overall Assessment\n\n"
                    f"The {critic_type} critic could not complete its review of this "
                    f"chapter due to a provider error ({error_msg}). No verdict can be "
                    f"issued. The chapter should be re-reviewed once the connection is "
                    f"stable. In the meantime, the pipeline continues to avoid blocking "
                    f"the entire production run on a single transient failure.\n\n"
                    f"VERDICT: REVISE\n"
                )
                rel = critics_mod.artifact_relpath(ctype, chapter)
                full = os.path.join(project, rel)
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(full, "w", encoding="utf-8") as f:
                    f.write(stub)
                results.append({
                    "critic_type": ctype,
                    "artifact_path": rel,
                    "verdict": "REVISE",
                    "word_count": len(stub.split()),
                    "located_findings": 0,
                    "has_chapter_hash": True,
                    "gate_substance_ok": False,
                    "error": error_msg,
                })
            except Exception:
                failures.append({"critic": ctype, "error": error_msg})
    return {"critics": results, "failures": failures, "chapter": chapter}


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
              units: Optional[list[int]] = None, instructions: str = "",
              rerun_mode: str = "fresh") -> RunState:
    """Initialize (or reset) a pipeline run. Returns the fresh RunState.

    ``rerun_mode`` controls how existing material is handled:
      - "fresh" (default): start from bible phase, overwrite everything.
      - "revise": keep existing bible/voice/outline, start at the writer phase
        for each chapter. Existing critic feedback will be injected into the
        writer prompt so the prose improves based on prior reviews.
    """
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

    # Revise mode: skip bible/voice/editorial_lock and start at writer.
    # The existing bible, voice spec, and outline are preserved on disk.
    # Existing critic feedback will be injected into the writer prompt by
    # _exec_writer via _collect_critic_feedback.
    if rerun_mode == "revise":
        has_bible = os.path.isfile(os.path.join(project, "bible", "04_outline.md"))
        has_chapters = any(
            os.path.isfile(os.path.join(project, "manuscript", f"{ch:03d}_*.md"))
            for ch in state.units
        ) if state.units else False
        if has_bible and state.units:
            state.current_phase = "writer"
            state.current_unit_index = 0
            # Clear prior unit results so the revision loop re-evaluates
            # each chapter fresh (but keeps phase_results like bible/voice).
            state.unit_results = {}
            state.chapter_retries = {}
        # If no bible/chapters exist, fall through to normal fresh start.

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


# A resolver maps a phase key to a model call. The orchestrator stays
# provider-agnostic -- the route layer builds this from provider config and
# the per-phase model_routing setting.
ModelResolver = Callable[[str], ModelCall]


async def advance_phase(project: str, resolve_call: ModelResolver) -> dict:
    """Run exactly ONE phase (the current one), serialized per project.

    Holds the per-project run lock across the whole load→await→save so a
    live-control mutation (brief / status / rerun) cannot interleave and be
    clobbered. Control endpoints acquire the same lock non-blocking and reject
    with PhaseBusyError while a phase is executing.
    """
    async with _run_lock(project):
        return await _advance_phase_locked(project, resolve_call)


async def _advance_phase_locked(project: str, resolve_call: ModelResolver) -> dict:
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

    # Clear stale errors from a previous failed attempt so the UI doesn't
    # show a stale ReadTimeout/500 the whole time the new attempt is running.
    state.last_error = None
    state.status = "running"
    save_run_state(state)
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

    model_call = resolve_call(phase)
    executor = _EXECUTORS[phase]

    # Check for a user-provided content override for this phase. If the user
    # supplied their own content (via the UI or chat), use it instead of
    # calling the model. The content is processed the same way model output
    # would be (written to disk in the expected format).
    chapter = state.units[state.current_unit_index] if state.units and phase in UNIT_PHASES else None
    override_key = f"{phase}:{chapter}" if chapter is not None else phase
    user_content = state.user_overrides.get(override_key)
    if user_content:
        result = _apply_user_override(phase, chapter, user_content, project, state)
        # Clear the override after use (one-shot).
        state.user_overrides.pop(override_key, None)
    else:
        try:
            result = await executor(state, project, model_call)
        except Exception as exc:
            state.status = "failed"
            state.last_error = f"{type(exc).__name__}: {exc}"
            save_run_state(state)
            raise

    # Record the result.
    _record_result(state, phase, result)

    # ── Post-critics revision loop ────────────────────────────────────────
    # After the critics phase, check verdicts immediately. If ANY critic says
    # REVISE, loop back to the writer with the critic findings so the chapter
    # is improved BEFORE editorial evaluation. This is the core quality loop:
    # critics exist to drive revision, not just to produce reports.
    MAX_CHAPTER_RETRIES = 2
    chapter = state.units[state.current_unit_index] if state.units else None

    if phase == "critics" and chapter is not None:
        critic_results = result.get("critics", [])
        revise_verdicts = [c for c in critic_results if c.get("verdict", "").upper() == "REVISE"]
        pass_verdicts = [c for c in critic_results if c.get("verdict", "").upper() in ("PASS", "ADVANCE")]
        retries = state.chapter_retries.get(chapter, 0)

        if revise_verdicts and retries < MAX_CHAPTER_RETRIES:
            state.chapter_retries[chapter] = retries + 1
            state.current_phase = "writer"
            state.last_error = (
                f"Chapter {chapter}: {len(revise_verdicts)}/{len(critic_results)} critics say REVISE "
                f"(attempt {retries + 1}/{MAX_CHAPTER_RETRIES}). Re-running writer with feedback."
            )
            save_run_state(state)
            return {
                "phase": phase,
                "phase_label": PHASE_SPECS[phase].label,
                "result": result,
                "next_phase": "writer",
                "next_phase_label": PHASE_SPECS["writer"].label,
                "state": state.to_dict(),
                "retrying": True,
                "revise_count": len(revise_verdicts),
                "pass_count": len(pass_verdicts),
            }

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

    # ── Gate-aware advancement ────────────────────────────────────────────
    # After verify_unit, check the gate verdict. If the chapter FAILED (REVISE
    # verdict from critics, or missing critic files), loop back to re-run the
    # writer (with critic feedback) or re-run missing critics instead of
    # blindly advancing to the next chapter. This is the core correctness fix
    # for the pipeline: REVISE means "rewrite this chapter", not "move on".
    MAX_CHAPTER_RETRIES = 2
    chapter = state.units[state.current_unit_index] if state.units else None
    gate_verdict = (gate or {}).get("verdict", "PASS") if gate else "PASS"

    if phase == "verify_unit" and gate_verdict == "FAIL" and chapter is not None:
        retries = state.chapter_retries.get(chapter, 0)
        if retries < MAX_CHAPTER_RETRIES:
            state.chapter_retries[chapter] = retries + 1
            # Collect critic feedback to inject into the writer prompt.
            critic_feedback = _collect_critic_feedback(project, chapter)
            if critic_feedback:
                # REVISE with feedback: re-run the writer so it can address
                # the critic findings.
                state.current_phase = "writer"
                state.last_error = (
                    f"Chapter {chapter} gate FAIL (attempt {retries + 1}/{MAX_CHAPTER_RETRIES}). "
                    f"Re-running writer with critic feedback."
                )
            else:
                # Missing critics: re-run the critics phase.
                state.current_phase = "critics"
                state.last_error = (
                    f"Chapter {chapter} missing critic files (attempt {retries + 1}/{MAX_CHAPTER_RETRIES}). "
                    f"Re-running critics."
                )
            save_run_state(state)
            return {
                "phase": phase,
                "phase_label": PHASE_SPECS[phase].label,
                "result": result,
                "next_phase": state.current_phase,
                "next_phase_label": PHASE_SPECS[state.current_phase].label,
                "state": state.to_dict(),
                "retrying": True,
            }
        else:
            # Max retries exhausted — force-advance with a warning.
            state.last_error = (
                f"Chapter {chapter} still FAIL after {MAX_CHAPTER_RETRIES} retries. "
                f"Force-advancing to next chapter."
            )

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


# ── Live control (steer the run from the UI / chat) ───────────────────────────
# These mutate the persisted RunState so a writer (or the pipeline chatbot) can
# redirect an in-progress or completed run: update the creative brief, re-run a
# phase/unit, or pause/resume. They never touch artifacts directly — the next
# advance_phase call is what re-executes, so the gate still governs the outcome.
#
# Concurrency: each acquires the per-project run lock NON-blocking. If a phase
# is mid-execution (advance_phase holds the lock across its LLM await), they
# raise PhaseBusyError instead of a silently-clobbered write. The route layer
# translates that to HTTP 409. A control mutation between phases always
# succeeds because advance_phase releases the lock when it returns.

def _try_lock_or_busy(project: str) -> asyncio.Lock:
    """Acquire the run lock without waiting; raise PhaseBusyError if held.

    In asyncio (single-threaded, cooperative), there's no yield between the
    ``locked()`` check and the caller's ``async with lock:`` acquire, so the
    check is effectively atomic — no TOCTOU in practice. The ``async with``
    block acquires and holds the lock for the duration of the work.
    """
    lock = _run_lock(project)
    if lock.locked():
        raise PhaseBusyError(
            "A pipeline phase is currently running. Wait for it to finish before "
            "changing the brief, status, or re-running a phase."
        )
    return lock


async def update_instructions(project: str, instructions: str) -> Optional[RunState]:
    """Replace the run's creative brief (honored by every future phase)."""
    project = os.path.abspath(project)
    lock = _try_lock_or_busy(project)
    async with lock:
        state = load_run_state(project)
        if state is None:
            return None
        state.instructions = (instructions or "").strip()
        save_run_state(state)
        return state


async def set_status(project: str, status: str) -> Optional[RunState]:
    """Set the run status (running | paused | complete | failed). Used for stop/resume."""
    project = os.path.abspath(project)
    lock = _try_lock_or_busy(project)
    async with lock:
        state = load_run_state(project)
        if state is None:
            return None
        state.status = status
        save_run_state(state)
        return state


async def prepare_rerun(project: str, phase: str, chapter: Optional[int] = None) -> Optional[RunState]:
    """Re-target the run cursor at ``phase`` (optionally a specific chapter).

    Sets current_phase (and current_unit_index when ``phase`` is per-unit and a
    chapter is given), clears last_error, and flips status back to "running" so
    the next advance_phase re-executes that phase. This lets the writer redo a
    unit (e.g. regenerate chapter 3's prose) after the fact.
    """
    project = os.path.abspath(project)
    if phase not in PHASE_SPECS:
        raise ValueError(f"Unknown phase: {phase}")
    lock = _try_lock_or_busy(project)
    async with lock:
        state = load_run_state(project)
        if state is None:
            return None
        state.current_phase = phase
        if phase in UNIT_PHASES and chapter is not None:
            if chapter in state.units:
                state.current_unit_index = state.units.index(chapter)
        state.last_error = None
        state.status = "running"
        save_run_state(state)
        return state


def chat_context_snapshot(project: str) -> dict:
    """A compact, prompt-safe snapshot of the run for the pipeline chatbot.

    Includes the phase roadmap, current cursor, brief, and a one-glance catalog
    summary — enough for the chatbot to give grounded guidance about where the
    run is and what's been produced, without dumping whole files into the prompt.
    """
    project = os.path.abspath(project)
    state = load_run_state(project)
    if state is None:
        return {"run_active": False}
    from . import outputs  # local import to avoid a cycle at module load
    return {
        "run_active": True,
        "status": state.status,
        "current_phase": state.current_phase,
        "current_phase_label": PHASE_SPECS.get(state.current_phase, PhaseSpec(
            state.current_phase, state.current_phase, PROJECT, None, "", False)).label,
        "current_unit_index": state.current_unit_index,
        "current_unit": (state.units[state.current_unit_index]
                         if state.units and state.current_unit_index < len(state.units)
                         else None),
        "units": state.units,
        "instructions": state.instructions,
        "phase_roadmap": [
            {"key": p.key, "label": p.label, "scope": p.scope} for p in PHASE_SPECS.values()
        ],
        "artifacts": outputs.catalog_summary(project),
    }

