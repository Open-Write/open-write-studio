# TV Critic Architecture — How the Review System Works

*The 14-mode critic system for episodic television production. Adapted from the screenplay and novel critic architectures.*

---

## Overview

The TV production system uses a 14-mode review system where each mode has a specific role, specific file access rules, and specific output format. The modes are designed to catch different categories of failure that single-pass writing cannot prevent — with TV-specific additions for cross-episode continuity, season-level coherence, and multi-writer voice consistency.

## How TV Critics Differ from Screenplay Critics

| Aspect | Screenplay Critics | TV Critics |
|--------|-------------------|------------|
| Scope | Single script (54-72 scenes) | Multiple episodes (10 episodes × 8-12 scenes each) |
| Continuity | Within one script | Across all episodes in the season |
| Voice consistency | One writer, one script | Simulated multi-writer, 600+ pages |
| Callback tracking | Intra-script only | Cross-episode, cross-season |
| State tracking | Character knowledge in one story | Character knowledge, physical states, relationships across episodes |
| Pacing | Three-act structure | Episode rhythm + season rhythm |
| Output naming | `scene_N_*.md` | `S01EXX_scene_NN_*.md` |

## The Modes

### Showrunner (tv-showrunner)
**Role:** Pipeline management, quality control, final creative authority before the human creator.
**Reads:** All files (bible, state, scripts, critic outputs).
**Writes:** Approvals, escalations, production decisions.
**Does NOT write scripts or plans.** Oversight only.

### Season Architect (tv-season-architect)
**Role:** Plans season-level arcs. Creates the season outline, tracks A/B/C story threads across episodes, manages callback seeds and payoffs.
**Reads:** Bible files, state files.
**Writes:** `bible/04_season_arc.md`, `bible/05_episode_outlines/`
**Does NOT write scripts.** Season architecture only.

### Episode Architect (tv-episode-architect)
**Role:** Plans individual episodes scene by scene. Ensures each scene serves the A/B/C stories, the season arc, and the episode's emotional arc.
**Reads:** Episode outline, season arc, character profiles, state files, format rules.
**Writes:** `critic_outputs/S01EXX_plan.md`
**Does NOT write scripts.** Episode planning only.

### Episode Writer (tv-episode-writer)
**Role:** Executes the episode architect's plan in Fountain markup.
**Reads:** Format rules (every scene), episode plan, character profiles, prior scene, state files.
**Writes:** `scripts/scenes/S01EXX/NN_scene_title.fountain`
**Key discipline:** No camera directions, no emotional parentheticals, no interiority, subtext not statement. Cross-episode voice consistency.

### Cutter (tv-cutter)
**Role:** Conditional — removes only material flagged by critics or editorial. **Separate model state from writer.**
**Principle:** Remove, don't rewrite. The compressed version is almost always better.
**Focus:** Action lines. Scenes that don't serve A/B/C stories. Dialogue rarely cut unless redundant.
**TV-specific:** Preserves act break cliffhangers, cold open hooks, callback payoffs.
**Output:** Overwrites script files + `critic_outputs/S01EXX_cuts.md`

### Show-Don't-Tell Critic (critic-show-tv)
**Role:** Mechanical enforcement of format rules.
**Categories:** Emotional state names, adverbs in dialogue tags, emotion-directing parentheticals, interiority in action lines, characters saying what they mean, over-described action, camera directions, invisible information.
**Output:** `critic_outputs/S01EXX_scene_NN_show_dont_tell.md`
**Calibration anchors:** Includes clearly good, clearly bad, and borderline examples with explicit reasoning.

### Voice Critic (critic-voice-tv)
**Role:** Per-character voice consistency review with cross-episode consistency checking. One call per character in the scene.
**Reads:** Scene file + one character's voice profile + prior episodes for cross-episode comparison.
**Evaluates:** Register identification, register coherence, register bleed-through, voice distinctiveness, subtext quality, **cross-episode voice consistency**.
**Output:** `critic_outputs/S01EXX_scene_NN_voice_{character}.md`
**TV-specific:** Checks that the character sounds the same in Episode 5 as they did in Episode 1. Voice drift across episodes is a critical TV failure mode.
**Key principle:** Combined calls let critics elide weak coverage of secondary characters. Always one call per character.

### Palette Critic (critic-palette-tv)
**Role:** Emotional palette verification.
**Bar:** "Palette lands" not just "palette present." Would a viewer feel this?
**Evaluates:** Palette achievement, emotional tension, restraint, specificity.
**Output:** `critic_outputs/S01EXX_palette.md`

### Continuity Critic (critic-continuity-tv)
**Role:** Cross-episode state/timeline/callback/audience-state review with deep verification.
**Highest priority check:** Knowledge-delta — what each character knows in this episode vs. all prior episodes.
**Checks:**
- Character knowledge (across all prior episodes)
- Physical state consistency (injuries, illnesses, conditions)
- Relationship state consistency (trust, conflict, alliances)
- Callbacks (seeds and payoffs across the season)
- Timeline consistency (time references across episodes)
- Audience-state misdirection (what the audience should believe)
- Props and set dressing consistency
**Deep verification:** Decomposes episode into narrative claims, cross-references sub-assumptions against state files AND prior episode scripts, assesses severity.
**Output:** `critic_outputs/S01EXX_continuity.md`
**TV-specific:** Unlike the screenplay version which tracks within one script, this critic tracks across ALL episodes in the season.

### Naturalism Critic (critic-naturalism-tv)
**Role:** AI-tell detection. Reviews scenes for patterns that make writing read as AI-generated.
**Reads:** Scene files + automated audit output from `tools/ai_tell_audit.py`.
**Checks:**
- Em-dash density (threshold: >2 per page warning, >5 critical)
- Triplet closing patterns
- Sentence length uniformity (CV below 0.35 signals AI uniformity)
- Paragraph structure uniformity
- Negation-action pairs
- Style consistency across scenes within the episode
- Thematic restatement through multiple characters
**Output:** `critic_outputs/S01EXX_naturalism.md`
**Verdict scale:** NATURAL / NEEDS REVISION / MECHANICAL
**TV-specific:** TV has more pages per episode than a film scene, so AI tells accumulate faster. Run on each episode after assembly.

### Adversarial Reader (adversarial-reader-tv)
**Role:** Cold coverage without bible access. Reads scripts only.
**Persona:** Lara Marsh, 14 years, calibrated against prestige cable drama.
**Verdict scale:** Would Stop / Would Continue / Engaged (partial drafts) or Pass / Consider / Recommend (full episodes/seasons).
**TV-specific criteria:**
- Cold open effectiveness
- Act break quality
- Episode pacing (does it feel like a complete episode or an incomplete chapter?)
- Season arc progress (is the serialized story advancing?)
- Character development across episodes
- Case-of-the-week engine (if applicable)
- The "would I watch the next episode?" test
**Output:** `coverage_reports/`
**Key value:** Catches issues that bible-aware critics miss because it reads what's on the page, not what was intended.

### Continuity Editor (continuity-editor)
**Role:** TV-specific mode. Maintains the cross-episode state tracking files.
**Reads:** Finalized episode scripts, all state files.
**Writes:** `state/character_state_tracker.json`, `state/season_arc_tracker.json`, `state/callback_ledger.json`, `state/audience_state.json`
**Key principle:** Single source of truth for what has happened in the show's world. Errors here cascade into every subsequent episode.

### Meta-Critic (critic-meta-tv) (reads critic outputs only)
**Role:** Cross-episode review synthesis. Reviews the critics, not the scripts.
**Reads:** All critic outputs in `critic_outputs/` for a batch of 2-3 episodes. Previous meta-critic notes in `state/meta_critic_notes.md`.
**Does NOT read:** Scripts, bible, or state files.
**Output:** `coverage_reports/meta_review_S01E[range].md` + updated `state/meta_critic_notes.md`
**Runs after:** Every 2-3 episodes have completed the full critic pipeline.
**Produces:** Critic quality summary, recurring issues, critic blind spots, voice drift detection, continuity cascade detection, refinement notes.
**TV-specific:** Especially important for detecting cross-episode patterns: voice drift, continuity cascades, callback timing issues.
**Full protocol:** [`skills/meta_critic_protocol.md`](meta_critic_protocol.md)

---

## The Multi-Model Pattern

Same-model critics have self-recognition bias. The same principle from the screenplay system applies to TV:

- Run at least 2 models on every critical pass
- Take the union of flagged issues across models, not the intersection
- What one model catches, another may miss

**TV-specific consideration:** With 10 episodes per season, the temptation is to run critics on only a few episodes. Run them on every episode. A voice inconsistency in Episode 3 that isn't caught until Episode 8 has contaminated 5 episodes of script.

---

## TV-Specific Calibration Anchors

Calibrate against the best work in the television medium. Every critic mode should calibrate honestly — when in doubt about a score of 7 or above, ask: "Would I give this score if the showrunner were not in the room?" If the answer is no, lower the score by 1.

---

## Pre-Episode and Post-Episode Review Protocols

### Pre-Episode Review (Before Writing)

1. **Episode Architect** produces the scene-by-scene plan
2. **Showrunner** reviews the plan against the season arc
3. **Continuity check** — verify the plan doesn't violate prior episodes
4. **Callback check** — verify callbacks are landing on schedule
5. **Approve or revise** the plan before writing begins

### Post-Episode Review (After Writing)

1. **Show-don't-tell critic** — mechanical enforcement (every scene)
2. **Voice critic** — per-character voice consistency (every scene, one call per character)
3. **Palette critic** — emotional palette verification (every episode)
4. **Continuity critic** — cross-episode state/callback review (every episode)
5. **Naturalism critic** — AI-tell detection (every episode, after show-don't-tell and voice)
6. **Address all flagged issues** before moving to assembly
7. **Episode assembly** — combine scenes into single episode file
8. **Cutter** — Conditional — removes only flagged material
9. **Adversarial reader** — cold coverage
10. **Showrunner** — final approval or revision request
11. **Continuity editor** — update state files
12. **Episode lock**

### Cross-Episode Continuity Checking

The continuity critic operates differently in TV than in film:

**Film:** Checks state within one script. Character knowledge is tracked from Scene 1 to Scene 60.

**TV:** Checks state across ALL episodes. Character knowledge is tracked from Episode 1, Scene 1 to the current episode's last scene. Physical states, relationships, and timeline are all tracked across the full season.

This means the continuity critic must read prior episodes — not just the current one. The `state/character_state_tracker.json` file is the canonical record, but the critic should verify the tracker against the actual scripts.

---

## What We Learned (from production, applied to TV)

1. **The show-don't-tell critic needed expansion.** "Invisible information" is a distinct violation category that categorical checks miss.
2. **The palette critic needed a higher bar.** "Palette present" is not enough. "Palette lands" is the correct standard.
3. **The continuity critic needed knowledge-delta checking.** Cross-episode knowledge tracking prevents characters knowing things they shouldn't.
4. **The adversarial reader persona works.** Named persona with specific calibration produces genuinely different coverage than generic prompts.
5. **Pre-generation auditing catches cascading errors.** Reviewing the bible for contradictions before writing is 10x cheaper than post-generation revision.
6. **Cross-model evaluation is essential.** Same-model critics have self-recognition bias.
7. **TV adds a new failure mode: voice drift.** Characters sounding different across episodes is a real risk with 600+ pages. The voice critic must check cross-episode consistency.
8. **TV adds a new failure mode: continuity cascade.** An error in Episode 3 that isn't caught until Episode 8 has contaminated 5 episodes. Run critics on every episode, not just a sample.
9. **Continuity critics need deep verification.** Cross-episode state checking is complex. Decomposing narrative claims into testable sub-assumptions catches subtle errors that surface-level checking misses.
10. **Critics need a feedback loop.** Without the meta-critic, critics run in isolation and cannot detect patterns that only emerge across episodes. The meta-critic is especially important in TV where errors cascade.
11. **Named revision strategies prevent vague revisions.** Grounding, Combination, Simplification, Divergent, and Coherence are specific tools for structured revision.

---

*This document defines the review architecture for TV production. Every mode has a specific role, specific access, and specific output. The system is designed to catch failures that single-pass writing cannot prevent.*
