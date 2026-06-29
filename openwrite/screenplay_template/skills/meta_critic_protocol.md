# Meta-Critic Protocol — Screenplay

*A cross-scene review synthesis system that improves critic quality through pattern identification and calibration feedback. Adapted from the Co-Scientist meta-review agent architecture.*

---

## Purpose

Individual critics run in isolation — they cannot detect patterns that only emerge across scenes. The meta-critic fills this gap by analyzing critic outputs over batches of 5-8 scenes, identifying recurring issues, hollow reviews, and blind spots, then producing calibration notes that improve subsequent review passes.

---

## When It Runs

After every 5-8 scenes have completed the full critic pipeline. The producer dispatches the meta-critic with a scene range.

For a 60-scene screenplay: approximately 8-12 meta-critic runs.

---

## What It Reads

- All critic outputs in `critic_outputs/` for the specified scene range
- Previous meta-critic notes in `state/meta_critic_notes.md`
- Does NOT read script files, bible, or state files

---

## What It Produces

### 1. Synthesis Report

Written to `coverage_reports/meta_review_scenes[N-M].md`. Contains:

- **Critic quality table:** Hollow outputs, average findings per review, worst scene
- **Recurring issues:** Patterns appearing in 2+ scenes with severity
- **Critic blind spots:** Categories no critic covers
- **Resolved patterns:** Issues from earlier batches now fixed
- **Refinement notes:** Specific instructions for subsequent critics

### 2. Persistent Notes

Appended to `state/meta_critic_notes.md`. Accumulates across the full screenplay.

---

## Refinement Notes Format

Refinement notes are specific, actionable instructions.

**Good:** "Continuity critic for scenes 12-18: Scenes 5-11 continuity critics produced hollow outputs (bare ADVANCE, 0 located findings). For scenes 12-18, the continuity critic MUST include at least 3 located findings per review."

**Bad:** "Continue doing good work on continuity checking."

---

## Analysis Categories

### Critic Substance Check
- Does it have located findings (quoted text + position)?
- Or is it a bare PASS/ADVANCE with zero evidence?

### Cross-Critic Pattern Detection
- **Convergent findings:** Multiple critics flag the same passage → high-confidence real issue
- **Divergent findings:** One critic flags what another misses → coverage gap
- **Escalating patterns:** Same issue getting worse across scenes
- **Resolved patterns:** Issue in early scenes, fixed in later scenes
