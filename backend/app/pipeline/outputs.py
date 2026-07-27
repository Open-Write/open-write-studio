"""
outputs.py — read-only catalog + reader for Open-Write pipeline artifacts.

The pipeline (orchestrator.py) writes a rich set of artifacts to disk during a
run (bible, voice spec, architect plans, chapter prose, the five critics per
chapter, editorial/adversarial coverage, the manifest, the run state). Until
now the only way to see them was the transient "last advance" payload that
Pipeline.tsx renders. This module turns those on-disk files into a structured,
browsable catalog grouped by category so the UI can present a real Output
Library (Bible / Voice / Design / Prose / Reviews / Manifest).

This is strictly read-only and path-traversal-safe: every path is resolved and
bounded to the project root before it is read. It never writes anything and
never grades the run (verification stays with verify_completion / finalize).

Path conventions (must match the orchestrator / critics writers):
  bible/01_concept.md, bible/04_outline.md, bible/07_format_rules.md,
  bible/LOCKED_VOICE_SPEC.md
  voice_experiments/candidates/voice_*.md, voice_experiments/review.md
  critic_outputs/chapter_{N}_plan.md            (architect plans)
  critic_outputs/chapter_{N}_{critic_type}.md   (5 critics: show/voice/palette/continuity/naturalism)
  coverage_reports/editorial_report_ch{N}.md    (per-chapter editorial)
  coverage_reports/editorial_outline_lock.md    (outline-lock coverage)
  coverage_reports/adversarial_read.md          (full-manuscript adversarial)
  manuscript/{NNN}_*.md                        (prose)
  manuscript/novel.md                           (assembled manuscript)
  state/completion_manifest.json, state/pipeline_run.json
"""

from __future__ import annotations

import glob
import os
import re
from datetime import datetime
from typing import Optional

from .word_count import count_words, count_prose_words_from_text


# ── Catalog category order (the order the UI presents them) ──────────────────
CATEGORY_ORDER = ["bible", "voice", "design", "prose", "reviews", "manifest"]

CATEGORY_LABELS = {
    "bible": "Bible",
    "voice": "Voice Experiment",
    "design": "Design Documents",
    "prose": "Prose (Manuscript)",
    "reviews": "Reviews",
    "manifest": "Manifest & State",
}

# Friendly labels for the five Open-Write critics (for display + grouping).
CRITIC_LABELS = {
    "show": "Critic — Show, Don't Tell",
    "voice": "Critic — Voice",
    "palette": "Critic — Palette",
    "continuity": "Critic — Continuity",
    "naturalism": "Critic — Naturalism",
}


# ── Path safety ──────────────────────────────────────────────────────────────

def _safe_realpath(project: str, rel: str) -> str:
    """Resolve ``rel`` under ``project`` and confirm it stays inside it.

    Returns the absolute real path, or raises ValueError if the path escapes the
    project folder. This is the same boundary used by the pipeline router and
    the manifest verifier, so a catalog read can never reach outside the project.
    """
    project = os.path.realpath(project)
    full = os.path.realpath(os.path.join(project, rel))
    if full != project and not full.startswith(project + os.sep):
        raise ValueError(f"Path escapes the project folder: {rel}")
    return full


# Module-level default for _stat_entry word counting. build_output_catalog
# sets this to False before building when only existence counts are needed
# (e.g. catalog_summary for the chat context snapshot).
_DEFAULT_WORD_COUNT = True


def _stat_entry(project: str, rel: str, *, word_count: bool | None = None, **extra) -> dict:
    """Build a catalog entry dict for one file path (relative to project).

    Always reports ``exists`` so the UI can show a placeholder row for an
    expected-but-missing artifact (e.g. the locked voice spec before the voice
    phase runs). When the file exists it also reports measured word count and
    mtime — measured, never self-reported (Open-Write rule).

    ``word_count=None`` (default) follows the module-level toggle set by
    ``build_output_catalog(word_counts=False)``. Explicit ``True``/``False``
    overrides the toggle.
    """
    if word_count is None:
        word_count = _DEFAULT_WORD_COUNT
    entry = {"path": rel.replace(os.sep, "/"), "exists": False, "words": None}
    entry.update(extra)
    try:
        full = _safe_realpath(project, rel)
    except ValueError:
        # A path that escapes the project is treated as non-existent rather
        # than crashing the whole catalog.
        return entry
    if os.path.isfile(full):
        entry["exists"] = True
        if word_count:
            try:
                entry["words"] = count_words(full)
            except Exception:
                entry["words"] = None
        try:
            entry["mtime"] = datetime.fromtimestamp(
                os.path.getmtime(full)
            ).isoformat()
        except Exception:
            pass
    return entry


# ── Category builders ────────────────────────────────────────────────────────

def _bible_entries(project: str) -> list[dict]:
    """The foundational bible documents (concept, outline, format rules).

    Also surfaces any additional bible/*.md files the architect produced beyond
    the three canonical ones, so nothing the pipeline wrote is hidden.
    """
    entries = [
        _stat_entry(project, "bible/01_concept.md", label="Concept", group="foundation"),
        _stat_entry(project, "bible/04_outline.md", label="Outline", group="foundation"),
        _stat_entry(project, "bible/07_format_rules.md", label="Format Rules", group="foundation"),
    ]
    # Surface extra bible docs (02/03/05/06 etc.) that aren't already listed.
    seen = {e["path"] for e in entries}
    for f in sorted(glob.glob(os.path.join(project, "bible", "*.md"))):
        rel = os.path.relpath(f, project).replace(os.sep, "/")
        if rel not in seen:
            label = os.path.splitext(os.path.basename(rel))[0]
            label = re.sub(r"^\d+[_\-\s]*", "", label).replace("_", " ").title() or rel
            entries.append(_stat_entry(project, rel, label=label, group="extra"))
    return entries


def _voice_entries(project: str) -> list[dict]:
    """Voice experiment outputs: candidates tested, the review, the locked spec.

    Mirrors the voice_experiment_protocol: many candidate voices are generated
    and compared, a review records which won and why, and the winner is locked
    into LOCKED_VOICE_SPEC.md. The catalog surfaces all three layers so the
    writer can audit the selection.
    """
    entries: list[dict] = []
    # Candidate voices tested (one file per candidate under voice_experiments/).
    cand_dir = os.path.join(project, "voice_experiments", "candidates")
    cands = sorted(glob.glob(os.path.join(cand_dir, "*.md")))
    for f in cands:
        rel = os.path.relpath(f, project).replace(os.sep, "/")
        base = os.path.splitext(os.path.basename(rel))[0]
        label = base.replace("_", " ").title()
        entries.append(_stat_entry(project, rel, label=label, group="candidates"))
    # The review / ranking record.
    entries.append(_stat_entry(
        project, "voice_experiments/review.md",
        label="Voice Review & Selection", group="review",
    ))
    # The locked specification (the actual thing every chapter is written to).
    entries.append(_stat_entry(
        project, "bible/LOCKED_VOICE_SPEC.md",
        label="Locked Voice Spec", group="locked",
    ))
    return entries


def _design_entries(project: str) -> list[dict]:
    """Design documents: the outline (structure) + per-chapter architect plans.

    The architect plan for each chapter is the strictest-gate planning document
    that the prose writer executes against. Surfacing them here lets the writer
    see the intended design before / alongside the prose.
    """
    entries: list[dict] = []
    # Outline is the top-level structural design doc (also lives in bible; we
    # surface it here too as the "structure" design artifact for discoverability).
    outline = _stat_entry(
        project, "bible/04_outline.md", label="Outline (structure)", group="structure",
    )
    entries.append(outline)
    # Per-chapter architect plans (chapter_N_plan.md). Sorted by chapter number.
    plans = sorted(glob.glob(os.path.join(project, "critic_outputs", "chapter_*_plan.md")))
    plan_re = re.compile(r"chapter_(\d+)_plan\.md$", re.IGNORECASE)
    for f in plans:
        rel = os.path.relpath(f, project).replace(os.sep, "/")
        m = plan_re.search(os.path.basename(rel))
        ch = int(m.group(1)) if m else None
        entries.append(_stat_entry(
            project, rel,
            label=f"Chapter {ch} — Architect Plan" if ch else rel,
            group="plans", chapter=ch,
        ))
    return entries


def _prose_entries(project: str) -> list[dict]:
    """The actual chapter prose + the assembled manuscript."""
    entries: list[dict] = []
    chapters_dir = os.path.join(project, "manuscript")
    files = sorted(glob.glob(os.path.join(chapters_dir, "*.md")))
    # Filter out novel.md (the assembled manuscript — listed separately below).
    files = [f for f in files if os.path.basename(f) != "novel.md"]
    num_re = re.compile(r"(\d+)")
    for f in files:
        rel = os.path.relpath(f, project).replace(os.sep, "/")
        base = os.path.basename(rel)
        m = num_re.match(base)
        ch = int(m.group(1)) if m else None
        # Humanize the filename into a chapter label.
        stem = os.path.splitext(base)[0]
        label = re.sub(r"^\d+[_\-\s]*", "", stem).replace("_", " ").strip()
        label = f"Chapter {ch}" + (f" — {label}" if label else "") if ch else stem
        entries.append(_stat_entry(
            project, rel, label=label, group="chapters", chapter=ch,
        ))
    # The assembled full manuscript (output of the assemble phase).
    entries.append(_stat_entry(
        project, "manuscript/novel.md",
        label="Assembled Manuscript", group="assembled",
    ))
    return entries


def _reviews_entries(project: str) -> list[dict]:
    """All review / coverage artifacts, grouped by kind.

    Per chapter: the 5 critics (critic_outputs/chapter_N_<type>.md) + the
    editorial report (coverage_reports/editorial_report_chN.md).
    Project scope: the outline-lock coverage and the full-manuscript adversarial
    read. These are the documents the gate and the writer use to revise.
    """
    entries: list[dict] = []

    # Per-chapter critic files: chapter_N_<type>.md for the five critic types.
    crit_re = re.compile(r"chapter_(\d+)_(show|voice|palette|continuity|naturalism)\.md$", re.IGNORECASE)
    critic_files: list[tuple[int, str, str]] = []  # (chapter, type, abspath)
    for f in sorted(glob.glob(os.path.join(project, "critic_outputs", "chapter_*.md"))):
        base = os.path.basename(f)
        # Skip architect plans — those are design docs, not reviews.
        if base.endswith("_plan.md"):
            continue
        m = crit_re.search(base)
        if m:
            critic_files.append((int(m.group(1)), m.group(2).lower(), f))
    critic_files.sort(key=lambda t: (t[0], t[1]))
    for ch, ctype, f in critic_files:
        rel = os.path.relpath(f, project).replace(os.sep, "/")
        entries.append(_stat_entry(
            project, rel,
            label=f"Chapter {ch} — {CRITIC_LABELS.get(ctype, ctype.title())}",
            group="critics", chapter=ch, critic_type=ctype,
        ))

    # Per-chapter editorial reports.
    ed_re = re.compile(r"editorial_report_ch(\d+)\.md$", re.IGNORECASE)
    for f in sorted(glob.glob(os.path.join(project, "coverage_reports", "editorial_report_ch*.md"))):
        rel = os.path.relpath(f, project).replace(os.sep, "/")
        m = ed_re.search(os.path.basename(rel))
        ch = int(m.group(1)) if m else None
        entries.append(_stat_entry(
            project, rel,
            label=f"Chapter {ch} — Editorial Eval" if ch else rel,
            group="editorial", chapter=ch,
        ))

    # Project-scope coverage.
    entries.append(_stat_entry(
        project, "coverage_reports/editorial_outline_lock.md",
        label="Outline Lock — Editorial Coverage", group="structural",
    ))
    entries.append(_stat_entry(
        project, "coverage_reports/adversarial_read.md",
        label="Adversarial Read (Full Manuscript)", group="structural",
    ))
    return entries


def _manifest_entries(project: str) -> list[dict]:
    """The completion manifest + pipeline run state (JSON)."""
    entries = [
        _stat_entry(project, "state/completion_manifest.json",
                    label="Completion Manifest", group="manifest"),
        _stat_entry(project, "state/pipeline_run.json",
                    label="Pipeline Run State", group="run"),
    ]
    if os.path.isfile(os.path.join(project, "state", "COMPLETION_PASS.json")):
        entries.append(_stat_entry(
            project, "state/COMPLETION_PASS.json",
            label="Completion Certificate (PASS)", group="manifest",
        ))
    return entries


_BUILDERS = {
    "bible": _bible_entries,
    "voice": _voice_entries,
    "design": _design_entries,
    "prose": _prose_entries,
    "reviews": _reviews_entries,
    "manifest": _manifest_entries,
}


# ── Public API ───────────────────────────────────────────────────────────────

def build_output_catalog(project: str, *, word_counts: bool = True) -> dict:
    """Build the structured, browsable catalog of all pipeline artifacts.

    Returns a dict with one ``categories`` list (in CATEGORY_ORDER) where each
    category has {key, label, count, exists_count, entries}. The top level also
    reports whether a run is active so the UI can show a live badge.

    Set ``word_counts=False`` for existence-only cataloging (no per-file word
    counting). Used by ``catalog_summary`` where only existence counts matter
    and the full read + count for every file is wasted work.
    """
    global _DEFAULT_WORD_COUNT
    _DEFAULT_WORD_COUNT = word_counts
    project = os.path.realpath(project)
    categories = []
    try:
        for key in CATEGORY_ORDER:
            entries = _BUILDERS[key](project)
            exists_count = sum(1 for e in entries if e.get("exists"))
            categories.append({
                "key": key,
                "label": CATEGORY_LABELS[key],
                "count": len(entries),
                "exists_count": exists_count,
                "entries": entries,
            })
    finally:
        _DEFAULT_WORD_COUNT = True  # restore default
    return {
        "project_path": project,
        "generated_at": datetime.now().isoformat(),
        "categories": categories,
    }


def read_artifact(project: str, rel: str, max_chars: int | None = None) -> dict:
    """Read one artifact's content (path-traversal-safe).

    Returns {path, exists, content, words, kind}. ``kind`` is ``"json"`` for
    .json files and ``"markdown"`` otherwise so the UI can render appropriately.

    When ``max_chars`` is set, only the first ``max_chars`` characters are
    returned (no full word count — the caller doesn't need it). This keeps the
    /chat path from reading + word-counting a 100k-char assembled manuscript
    only to truncate it to 12k.
    """
    full = _safe_realpath(project, rel)
    kind = "json" if rel.lower().endswith(".json") else "markdown"
    if not os.path.isfile(full):
        return {"path": rel.replace(os.sep, "/"), "exists": False, "content": "",
                "words": None, "kind": kind}
    with open(full, "r", encoding="utf-8-sig") as f:
        if max_chars is not None:
            content = f.read(max_chars).replace("\ufeff", "")
        else:
            content = f.read().replace("\ufeff", "")
    words = None
    try:
        if kind == "markdown" and max_chars is None:
            words = count_prose_words_from_text(content)
    except Exception:
        pass
    return {
        "path": rel.replace(os.sep, "/"),
        "exists": True,
        "content": content,
        "words": words,
        "kind": kind,
    }


def catalog_summary(project: str) -> dict:
    """A compact one-glance summary for chat context / status badges.

    Returns per-category exists counts + total artifacts present. Builds the
    catalog in existence-only mode (no per-file word counting) so it's cheap
    to call on every chat message.
    """
    catalog = build_output_catalog(project, word_counts=False)
    summary = {}
    total_present = 0
    total_expected = 0
    for cat in catalog["categories"]:
        summary[cat["key"]] = {
            "present": cat["exists_count"],
            "expected": cat["count"],
        }
        total_present += cat["exists_count"]
        total_expected += cat["count"]
    return {
        "total_present": total_present,
        "total_expected": total_expected,
        "by_category": summary,
    }
