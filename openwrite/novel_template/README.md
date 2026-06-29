# Novel Template — How to Write a Novel from Scratch

*A self-contained template for AI-assisted novel production. Validated on produced novels through iterative revision and professional coverage.*

---

## What This Template Is

This folder contains everything a bot needs to write a novel from scratch: bible templates, state tracking, Python tools, craft guidance, and a step-by-step workflow. It is derived from a production system that produced a 75,000+ word dual-track novel that received an Acquisition Recommendation from professional coverage.

The template is self-contained. A bot with access to only this directory should have everything it needs to produce a complete novel.

---

## Step-by-Step Workflow

### Phase 1: Foundation (Read Everything First)

1. **Read this file** (`README.md`) — you're doing it now.
2. **Read [`skills/start_here.md`](skills/start_here.md)** — the full onboarding guide for novel production.
3. **Read [`skills/critic_architecture.md`](skills/critic_architecture.md)** — understand the 12-mode production system.
4. **Read [`skills/voice_experiment_protocol.md`](skills/voice_experiment_protocol.md)** — understand how to select and lock a writing voice.

### Phase 2: Build the Bible

5. **Fill [`bible/01_concept.md`](bible/01_concept.md)** — thematic frame, logline, central question, structural misdirections.
6. **Fill [`bible/02_mythology.md`](bible/02_mythology.md)** — world-building, rules of the fictional universe.
7. **Create character profiles in [`bible/03_characters/`](bible/03_characters/)** — use [`_template.md`](bible/03_characters/_template.md) as the starting point. Create one file per major character.
8. **Fill [`bible/04_outline.md`](bible/04_outline.md)** — chapter-by-chapter outline with emotional palettes, callback seeds, and reader-state tracking.
9. **Fill [`bible/05_ending_notes.md`](bible/05_ending_notes.md)** — how the ending should be interpreted, ambiguous readings.
10. **Fill [`bible/06_craft_feeling.md`](bible/06_craft_feeling.md)** — emotional execution standards (the most important bible file).
11. **Fill [`bible/07_format_rules.md`](bible/07_format_rules.md)** — prose discipline, AI tic scrub list, dialogue rules.

### Phase 3: Voice Selection

12. **Run the Voice Experiment Protocol** ([`skills/voice_experiment_protocol.md`](skills/voice_experiment_protocol.md)):
    - Define 5 candidate voices
    - Write test passages (same scene in each voice, 3 runs per voice)
    - Have an adversarial reader evaluate cold
    - Rank by ceiling (best single run), not average
    - Refine top 2, then lock the winner
    - Create a locked voice spec for your project

### Phase 4: Pre-Generation Review

13. **Run the Editorial Review Protocol** ([`skills/editorial_review_protocol.md`](skills/editorial_review_protocol.md)):
    - Present the outline to 3 editorial personas (Lara Marsh, Dr. Elena Vasquez, Marcus Webb)
    - Synthesize feedback, revise, re-present
    - Lock the outline when all 3 return positive verdicts
14. **Run the Bible Auditor** — check for contradictions, knowledge gaps, logic bugs before any prose is generated.

### Phase 5: Write the Novel

15. **For each chapter:**
    - Architect plans the chapter (bible chunks N±2, character profiles, state files)
    - Prose-writer executes the plan
    - Run prose audit ([`tools/prose_audit.py`](tools/prose_audit.py)) — AI tic detection
    - Run convention scan ([`tools/convention_scan.py`](tools/convention_scan.py)) — pattern tracking
    - Run critics (show-don't-tell, voice, palette, continuity)
    - Run cutter if critics flag material (conditional, no target percentage)
    - Update state files (callback ledger, chapter outline)

### Phase 6: Revision (Diminishing Returns)

16. **Run the Iterative Revision Protocol** ([`skills/iterative_revision_protocol.md`](skills/iterative_revision_protocol.md) Version 2):

**Revision continues until diminishing returns, not just until target verdict.**

Before each revision, assess feedback scope:
- **Surface**: line-level fixes (interiority violations, repetitive tics, hedge words)
- **Scene**: scene-level restructuring (pacing, exposition loops, underdeveloped scenes)
- **Structural**: outline-level changes (act structure, scene additions/deletions, character arc redesign)
- **Voice**: voice-level adjustments (monotony, register mismatch, convention overuse)

**Scope matching:**
- If feedback points to fundamental structural problems → go back to the outline
- If feedback suggests superficial work → stay at line level

**Stopping rules** (stop when ANY of):
- Delta ≤ 0.2 for **two consecutive iterations** (diminishing returns confirmed)
- Worst dimension unchanged for 3 consecutive iterations
- Composite score > 8.5 (approaching ceiling)
- Maximum iterations reached (configurable, default 7)

**The goal is the best work the system is capable of, not just hitting a target verdict.**

17. **Track progress** in a diminishing returns table:
| Iteration | Composite | Delta | Verdict | Notes |
|-----------|-----------|-------|---------|-------|
| 1 | 6.2 | — | PASS | Initial evaluation |
| 2 | 6.8 | +0.6 | PASS | Meaningful improvement |
| 3 | 7.0 | +0.2 | PASS | Marginal improvement |
| 4 | 7.1 | +0.1 | PASS | No improvement — STOP |

18. **Run the Adversarial Reader** after each iteration — Lara Marsh, cold coverage, no bible access. Use [`skills/editorial_review_system.md`](skills/editorial_review_system.md) Mode 1 for quantitative coverage with dimensional scores.

### Phase 7: Export

18. **Assemble the manuscript** ([`tools/assemble.py`](tools/assemble.py))
19. **Export to PDF** ([`tools/export_formats.py`](tools/export_formats.py), [`tools/novel_chapter_export.py`](tools/novel_chapter_export.py))
20. **Verify word count** ([`tools/word_count.py`](tools/word_count.py))
21. **Check track balance** ([`tools/track_balance.py`](tools/track_balance.py)) — for dual-track novels
22. **Build cumulative summaries** ([`tools/build_cumulative_summaries.py`](tools/build_cumulative_summaries.py))

---

## Adaptation Workflow

If you're adapting a screenplay (or other source material) into a novel, use the **Adaptation Protocol** instead of the standard workflow. The adaptation protocol is a 3-phase pipeline that:

1. **Extracts narrative DNA** from the source material
2. **Designs and tests voice candidates** calibrated to the source
3. **Drafts the novel** with iterative review until RECOMMEND

See [`adaptation_template/README.md`](adaptation_template/README.md) for the full adaptation workflow.

**Quick start:**
1. Place your source screenplay in `source/`
2. Set your adaptation configuration (target length, autonomous mode, etc.)
3. Tell the system: "Adapt this screenplay into a novel."

The adaptation protocol can run autonomously (no pauses) or interactively (pause at each phase boundary for your review).

---

## Key Principles

### 1. Voice Experiment Protocol
Don't guess at the writing voice. Test 5 candidates empirically, rank by ceiling, refine the top 2, lock the winner. The locked voice spec is the single most important document for prose consistency.

### 2. Convention Ledger
Track ALL writing conventions — not just prohibited ones. The [`convention_scan.py`](tools/convention_scan.py) tool prevents the subtle repetition that makes prose feel manufactured. Body anchors, sensory distribution, sentence rhythm, dialogue attribution — all tracked.

### 3. Iterative Revision
Each revision iteration is targeted, not general. The adversarial reader identifies specific issues; the revision addresses those issues and nothing else. Five iterations is the sweet spot.

### 4. Cut-Ten-to-Twenty-Percent Rule
The cutter runs only when critics or editorial flag extraneous material. No target percentage. Chapter length follows the scene and the outline beat.

### 5. The Prose Discipline Document
[`bible/07_format_rules.md`](bible/07_format_rules.md) must be reloaded before every chapter. Without it, the prose swells. Key rules:
- Scene vs. summary (70%+ scene)
- Prose distance modulation (close-up, middle, compressed lyric)
- AI tic scrub list (Tier 1 banned, Tier 2 flagged)
- Interiority must do work (specific to character, specific to moment)
- Dialogue is subtext, not statement

### 6. The Critic Architecture
13 specialized modes catch different failure categories. Run at least 2 models on every critical pass. Take the union of flagged issues, not the intersection.

### 7. The Adversarial Reader
The most valuable critic reads cold, without the bible. Named persona (Lara Marsh, 14 years coverage experience) produces genuinely different coverage than generic prompts.

---

## Example: Locked Voice Spec

After empirical testing, a locked voice spec should capture these characteristics:

- **Close-third POV** with disciplined modulation between extreme close-up and compressed lyric distance
- **Body-anchor discipline** — hands, eyes, breath, spine, jaw. Specific physical details carry emotional weight.
- **Rendered interiority** — never "she felt grief." Instead: "The kitchen had not changed since the morning Sofia stopped wanting toast."
- **Subtext over statement** — characters talk about something else. The emotion lives in what they don't say.
- **Silence as architecture** — white space is structural. A single sentence alone on its line is a deliberate choice.
- **Sentence rhythm variation** — no 5+ consecutive sentences of similar length. Short declaratives alternate with periodic sentences.
- **Said/asked as defaults** for dialogue tags. Action beats preferred over tags. No adverbial dialogue tags.

---

## Directory Structure

```
novel_template/
├── README.md                    — This file (entry point)
├── bible/
│   ├── 01_concept.md            — Thematic frame, logline, central question
│   ├── 02_mythology.md          — World-building, fictional rules
│   ├── 03_characters/           — Character profiles
│   │   └── _template.md         — Blank character profile template
│   ├── 04_outline.md            — Chapter outline with emotional palettes
│   ├── 05_ending_notes.md       — Ending interpretation guidance
│   ├── 06_craft_feeling.md      — Emotional execution standards
│   └── 07_format_rules.md       — Prose discipline, AI tic scrub list
├── manuscript/                  — Where chapter .md files go
├── state/
│   ├── chapter_outline.json     — Chapter outline state tracking
│   ├── callback_ledger.json     — Callback seed/payoff tracking
│   └── convention_ledger.json   — Writing convention tracking
├── tools/
│   ├── word_count.py            — Word count by chapter and track
│   ├── prose_audit.py           — AI tic and prose discipline detection
│   ├── callback_check.py        — Callback ledger status checker
│   ├── convention_scan.py       — Convention ledger scanner
│   ├── assemble.py              — Chapter assembly into full manuscript
│   ├── export_formats.py        — Multi-format export (TXT, PDF)
│   ├── novel_chapter_export.py  — Per-chapter PDF export
│   ├── build_cumulative_summaries.py — Cumulative chapter summaries
│   └── track_balance.py         — Track A/B/interlude balance checker
├── reference/                   — Voice cards, world-building references
├── coverage_reports/            — Adversarial reader coverage output
├── critic_outputs/              — Critic pass outputs
└── skills/
    ├── start_here.md            — Novel-specific onboarding
    ├── novel_craft.md           — Prose craft guidance (adapted from screenplay craft)
    ├── critic_architecture.md   — 8-mode review system
    ├── voice_experiment_protocol.md — Voice selection protocol
    ├── editorial_review_protocol.md — Pre-generation editorial review
    ├── iterative_revision_protocol.md — 5-iteration revision methodology
    ├── convention_tracking.md   — Convention ledger usage guide
    └── pdf_export.md            — Novel export guidance
```

---

## Validation

This template was validated during the production of a 75,000+ word dual-track literary science fiction novel:

| Metric | Value |
|--------|-------|
| Word count | 75,000+ |
| Chapters | 39+ |
| Verdict | Acquisition Recommendation |
| Revision iterations | 5 (CONSIDER → RECOMMEND) |
| Coverage reads | Multiple independent readers |

The novel interleaved two narratives: a contemporary literary fiction track (close-third POV) and an alien civilization track (elevated register). The two tracks converged in the final act.

---

## Tools Quick Reference

| Tool | Command | Purpose |
|------|---------|---------|
| Word count | `python tools/word_count.py` | Count words by chapter and track |
| Prose audit | `python tools/prose_audit.py` | Detect AI tics and prose violations |
| Callback check | `python tools/callback_check.py` | Check callback ledger status |
| Convention scan | `python tools/convention_scan.py` | Scan manuscript for convention patterns |
| Assemble | `python tools/assemble.py --title "Title" --author "Author"` | Assemble chapters into full manuscript |
| Export formats | `python tools/export_formats.py` | Export to TXT and PDF |
| Chapter export | `python tools/novel_chapter_export.py` | Export per-chapter PDFs |
| Cumulative summaries | `python tools/build_cumulative_summaries.py` | Build cumulative chapter summaries |
| Track balance | `python tools/track_balance.py` | Check Track A/B/interlude ratios |

**Note:** Always set `PYTHONIOENCODING=utf-8` before running tools. Example: `set PYTHONIOENCODING=utf-8 && python tools/word_count.py`

---

## Skills Files Reference

| Skill | File | When to Read |
|-------|------|--------------|
| Onboarding | [`skills/start_here.md`](skills/start_here.md) | First thing — before any work |
| Novel Craft | [`skills/novel_craft.md`](skills/novel_craft.md) | When writing or revising prose |
| Critic Architecture | [`skills/critic_architecture.md`](skills/critic_architecture.md) | When setting up the review system |
| Voice Experiment | [`skills/voice_experiment_protocol.md`](skills/voice_experiment_protocol.md) | When selecting a writing voice |
| Editorial Review | [`skills/editorial_review_protocol.md`](skills/editorial_review_protocol.md) | Before any generation begins |
| Iterative Revision | [`skills/iterative_revision_protocol.md`](skills/iterative_revision_protocol.md) | When revising a completed draft |
| Convention Tracking | [`skills/convention_tracking.md`](skills/convention_tracking.md) | When tracking writing patterns |
| PDF Export | [`skills/pdf_export.md`](skills/pdf_export.md) | When exporting to PDF |

---

*All protocols validated against production use.*
