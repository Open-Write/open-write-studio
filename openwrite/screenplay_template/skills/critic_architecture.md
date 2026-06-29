# Critic Architecture v2.0 — How the Review System Works

*The multi-mode critic system validated through production use. Transferable architecture.*

---

## Overview

This system uses a multi-mode review system where each mode has a specific role, specific file access rules, and specific output format. The modes are designed to catch different categories of failure that single-pass writing cannot prevent.

**Every scene runs through every critic — no exceptions, no batching, no shortcuts.**

**Every critic is blinded** — reads only the scene text + its specific rubric. Critics do NOT read the architect plan, writer's intentions, or other critic outputs. This prevents rubber-stamp consensus.

**Every critic output must contain located findings** — quoted text with position. A bare PASS with zero evidence is a failed review, not a clean scene.

---

## Cardinal Rules

1. **Every scene gets identical rigor.** No batch mode, no fast path, no abbreviation for later scenes.
2. **No self-reported completion.** Files must exist on disk. Word counts come from `word_count.py`.
3. **"Reduce context" = reset-and-continue at full rigor.** Never abbreviate.
4. **Full-screenplay reviews read the entire script.** No sampling.
5. **Critics are blinded.** Each reads only the scene + its rubric. No cross-pollination.
6. **Located findings are mandatory.** Every flagged issue must cite quoted text + position.
7. **Revise-then-recheck.** Each finding marked resolved with before/after, then the scene re-linted.

---

## The Modes

### Architect
**Role:** Plans scenes before they are written. Strictest quality gate in the system.
**Reads:** Bible chunks (N±2), character profiles, state files, callback ledger, audience state, voice spec.
**Writes:** `critic_outputs/scene_N_plan.md`
**Must include:** Character architecture depth (motivation, contradiction, blind spot, interiority method) for every principal character, knowledge deltas, causal logic verification.
**Does NOT write Fountain.** The plan is the quality gate before generation.
**Verification:** Plan file must exist on disk before screenwriter runs.

### Screenwriter
**Role:** Executes the architect's plan in Fountain markup.
**Reads:** Format rules (every scene), architect plan, character profiles, prior scene, voice spec.
**Writes:** `script/scenes/N_*.fountain`
**Key discipline:** No camera directions, no emotional parentheticals, no interiority in action lines, subtext not statement, AI tic avoidance.

### Show-Don't-Tell Critic (BLINDED)
**Role:** Mechanical enforcement of format rules.
**Reads:** Scene file + `bible/07_format_rules.md` ONLY. Does NOT read architect plan or other critics.
**Categories:** Emotional state names, adverbs in dialogue tags, emotion-directing parentheticals, interiority in action lines, characters saying what they mean, over-described action, camera directions, **invisible information** (durations, off-screen knowledge, historical interiority), pure summary.
**Output:** `critic_outputs/scene_N_show_dont_tell.md`
**Must include:** scene_hash, located findings (quoted text + line number). Bare PASS fails.

### Voice Critic (BLINDED)
**Role:** Per-character voice consistency review. One call per character in the scene.
**Reads:** Scene file + one character's voice profile ONLY.
**Evaluates:** Register identification, register coherence, register bleed-through, voice distinctiveness, subtext quality.
**Output:** `critic_outputs/scene_N_voice_{character}.md`
**Must include:** scene_hash, located findings.
**Key principle:** Combined calls let critics elide weak coverage of secondary characters. Always one call per character.

### Palette Critic (BLINDED)
**Role:** Emotional palette verification.
**Reads:** Scene file + scene's palette from outline ONLY.
**Bar:** "Palette lands" not just "palette present." Would a contest reader feel this?
**Evaluates:** Palette achievement, emotional tension, restraint, specificity.
**Output:** `critic_outputs/scene_N_palette.md`
**Must include:** scene_hash, located findings (quoted passages).

### Continuity Critic (BLINDED)
**Role:** State/timeline/callback/audience-state review with deep verification.
**Reads:** Scene file + state files ONLY. Does NOT read other critics.
**Highest priority check:** Knowledge-delta — what each character knows in this scene vs. prior scenes.
**Checks:** Character knowledge, callbacks, timeline, audience-state misdirection, props/motifs.
**Deep verification:** Decomposes scene into narrative claims, cross-references sub-assumptions against state files, assesses severity of any contradictions.
**Output:** `critic_outputs/scene_N_continuity.md`
**Must include:** scene_hash, located findings, deep verification analysis.

### Naturalism Critic (BLINDED)
**Role:** AI-tell detection and naturalism review.
**Reads:** Scene file ONLY. Does NOT read architect plan, other critics, or state files.
**Detects:** Em-dash overuse, triplet closing patterns, inhuman style consistency, sentence pattern overuse, dialogue tag patterns, thematic restatement, interiority tics, negative-construction density, cross-scene refrain.
**Output:** `critic_outputs/scene_N_naturalism.md`
**Must include:** scene_hash, located findings.
**Runs on every scene** — not just when context allows. Naturalism catches micro-patterns that make writing read as AI-generated.

### Cutter
**Role:** Conditional — removes only material flagged by critics or editorial. **Separate model state from writer.**
**Principle:** Remove, don't rewrite. The compressed version is almost always better.
**Focus:** Action lines. Dialogue rarely cut unless redundant.
**Output:** Overwrites scene file + `critic_outputs/scene_N_cuts.md`

### Editorial Evaluation (BLINDED from other critics)
**Role:** Three-person panel (Vasquez, Webb, Marsh) reviewing finished scenes.
**Reads:** Scene file + bible ONLY. Does NOT read other critic outputs — evaluates independently.
**Includes:** Structural assessment (causal logic, arc progress, character architecture, callbacks) before prose evaluation.
**Routes:** Structural issues back to outline/bible, character issues back to character profiles, prose issues to scene file.
**Output:** `coverage_reports/editorial_report_scene[N].md`
**Must include:** scene_hash, located findings.

### Adversarial Reader (BLIND — no bible, no critics)
**Role:** Cold coverage without bible access. Reads script only.
**Persona:** Lara Marsh, 14 years, calibrated against literary character drama.
**Must read:** FULL assembled screenplay. No sampling, no "key scenes."
**Verdict scale:** Would Stop / Would Continue / Engaged (partial drafts) or Pass / Consider / Recommend (full scripts).
**Output:** `coverage_reports/`
**Must include:** Minimum 5 located weaknesses for any full-screenplay read (even Recommend). Bare APPROVE with zero findings is a FAILED read.
**Key value:** Catches issues that bible-aware critics miss because it reads what's on the page, not what was intended.

### Meta-Critic (reads critic outputs only)
**Role:** Cross-scene review synthesis. Reviews the critics, not the script.
**Reads:** All critic outputs in `critic_outputs/` for a batch of 5-8 scenes. Previous meta-critic notes in `state/meta_critic_notes.md`.
**Does NOT read:** Script files, bible, or state files.
**Output:** `coverage_reports/meta_review_scenes[N-M].md` + updated `state/meta_critic_notes.md`
**Runs after:** Every 5-8 scenes have completed the full critic pipeline.
**Produces:** Critic quality summary, recurring issues, critic blind spots, refinement notes for subsequent critics.
**Key value:** The feedback loop that makes critics improve over time. Catches hollow reviews, escalating patterns, and critic blind spots that individual critics cannot see in isolation.
**Full protocol:** [`meta_critic_protocol.md`](meta_critic_protocol.md)

---

## The Deterministic Lint Suite

Model-independent content lints that run on every scene and the assembly. The single-model substitute for cross-model validation.

**What it catches:** duplicate paragraphs, cross-scene refrain repetition, negative-construction density, banned constructions, round-number padding, pure summary, em-dash overuse, intra-scene refrain.

**Integration:** Runs after editorial evaluation, before final verification. Critical findings block advancement. The lint suite is the model-independent judge — no agent judgment enters.

**Tool:** `python tools/lint_suite.py --base-dir <project>`

---

## The Revise-Then-Recheck Protocol

When any critic flags a finding that requires a prose change:

1. Apply the fix to the scene file
2. Re-run the critic that flagged it
3. The re-run must verify: (a) the flagged text no longer appears, (b) no new violations introduced
4. Advance is blocked while any critical finding remains unresolved

This prevents the "flagged but shipped unfixed" failure mode observed in production.

---

## The Per-Scene Pipeline

```
PLAN (architect) → must exist on disk
  ↓
WRITE (screenwriter)
  ↓
CRITIQUE (all critics: show, voice, palette, continuity — with deep verification, naturalism — all BLINDED)
  ↓
CUT (cutter — conditional, only when critics flag material)
  ↓
REVISE-THEN-RECHECK (if critics flagged issues → fix → re-run affected critics)
  ↓
EVALUATE (editorial panel — BLINDED from other critics)
  ↓
LINT (deterministic lint suite — model-independent)
  ↓
VERIFY (disk check: all files exist, all have located findings, lints pass)
  ↓
Write resume file → next scene starts fresh

  After every 5-8 scenes:
  META-CRITIC → synthesis report + refinement notes for next batch
```

Every scene. No exceptions. No abbreviation.

---

## Calibration Anchors

Every critic mode includes calibration anchors: 2-3 worked examples of clearly good, clearly bad, and borderline cases with explicit reasoning. AI critics drift toward generous ratings without anchors. With anchors, they calibrate against the examples.

---

## What We Learned

1. **The show-don't-tell critic needed expansion.** "Invisible information" (durations, off-screen knowledge, historical interiority) is a distinct violation category that categorical checks miss.
2. **The palette critic needed a higher bar.** "Palette present" is not enough. "Palette lands" — would a contest reader feel this? — is the correct standard.
3. **The continuity critic needed knowledge-delta checking.** Cross-scene knowledge tracking prevents characters knowing things they shouldn't.
4. **The adversarial reader persona works.** Named persona with specific calibration produces genuinely different coverage than generic prompts.
5. **Same-model critics have self-recognition bias.** With single-model, the substitute is: (a) blinding each critic, (b) requiring located findings, (c) deterministic lints that catch what the model won't flag against itself.
6. **Naturalism must run every scene.** Skipping it lets AI tells accumulate.
7. **Structural issues must route to outline/bible level.** Patching structural problems at script level wastes time and doesn't fix the root cause.
8. **Character architecture is structural.** A character without contradiction, blind spot, and interiority method is a structural defect, not a script issue.
9. **Critics self-authoring their own output produces theater.** The fix: blinding + located-finding requirement + deterministic lint as model-independent judge.
10. **Bare PASS assertions are hollow.** A critic that says PASS with zero evidence is worse than no critic — it creates false confidence.
11. **Continuity critics need deep verification.** Surface-level state checking misses subtle contradictions. Decomposing narrative claims into testable sub-assumptions catches errors that pattern matching cannot.
12. **Critics need a feedback loop.** Without the meta-critic, critics run in isolation and cannot detect patterns that only emerge across scenes. The meta-critic is the missing self-improvement mechanism.
13. **Named revision strategies prevent vague revisions.** Grounding, Combination, Simplification, Divergent, and Coherence are specific tools, not generic "make it better" instructions.

---

## Pre-Script Editorial Review

**Testing regime for projects with structural complexity.** Before any generation, run the outline/bible through editorial personas. This prevents generating 120 pages against a flawed structure — catching structural problems when they're cheap to fix (in the outline) rather than expensive (in the full script).

### Personas

- **Lara Marsh** (contest/studio reader, 14 years) — Cold coverage of the outline as a structural document.
- **Dr. Elena Vasquez** (literary fiction editor, 20 years) — Evaluates thematic architecture.
- **Marcus Webb** (development executive, 12 years) — Evaluates marketability and producibility.

### Protocol

1. Present each outline option to each persona independently
2. Each persona produces coverage (verdict + specific issues)
3. Synthesize feedback across personas — identify overlapping concerns and unique perspectives
4. Revise the outline to address the synthesized feedback
5. Re-present the revised outline to all personas
6. Iterate until all personas return positive verdicts
7. Lock the outline — no structural changes after lock

Full protocol: [`editorial_review_protocol.md`](editorial_review_protocol.md)

---

## Voice Experiment Protocol

The systematic protocol for selecting and locking a writing voice through empirical evaluation.

**Structure:**
- Round 1: 5 voices × 3 runs = 15 candidates. Elo-based pairwise tournament (debate prompt). Top 2 by Elo advance.
- Round 2: Top 2 voices × 2 refinements × 2 runs = 8 candidates. Elo tournament.
- Round 3: Iterative refinement on winner. Lock when ceiling holds across 9 consecutive runs.

**Key insight:** Elo pairwise comparison eliminates subjective scoring bias. The debate prompt forces articulation of specific reasons.

Full protocol: [`voice_experiment_protocol.md`](voice_experiment_protocol.md)
