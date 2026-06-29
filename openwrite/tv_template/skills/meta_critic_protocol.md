# Meta-Critic Protocol — TV

*A cross-episode review synthesis system that improves critic quality through pattern identification and calibration feedback. Adapted from the Co-Scientist meta-review agent architecture.*

---

## Purpose

Individual critics run in isolation — they cannot detect patterns that only emerge across episodes. The meta-critic fills this gap by analyzing critic outputs over batches of 2-3 episodes, identifying recurring issues, hollow reviews, and blind spots, then producing calibration notes that improve subsequent review passes.

In TV, the meta-critic is critical: with 10 episodes per season, a critic blind spot that goes undetected can contaminate multiple episodes.

---

## When It Runs

After every 2-3 episodes have completed the full critic pipeline. The showrunner dispatches the meta-critic with an episode range.

For a 10-episode season: 3-5 meta-critic runs.

---

## What It Reads

- All critic outputs in `critic_outputs/` for the specified episode range
- Previous meta-critic notes in `state/meta_critic_notes.md`
- Does NOT read scripts, bible, or state files

---

## What It Produces

### 1. Synthesis Report

Written to `coverage_reports/meta_review_S01E[range].md`. Contains:

- **Critic quality table:** Hollow outputs, average findings per review, worst episode
- **Recurring issues:** Patterns appearing in 2+ episodes with severity
- **Critic blind spots:** Categories no critic covers
- **Cross-episode failures:** Errors that propagated across episodes
- **Voice drift:** Characters sounding different across episodes
- **Refinement notes:** Specific instructions for subsequent critics

### 2. Persistent Notes

Appended to `state/meta_critic_notes.md`. Accumulates across the full season.

---

## TV-Specific Analysis

### Voice Drift Detection

Track whether the voice critic catches character voice changes across episodes. If Character X sounds different in Episode 5 than Episode 1, and the voice critic didn't flag it, that's a critic blind spot.

### Continuity Cascade Detection

Identify errors in early episodes that propagate to later ones. Example: A state error in Episode 3 that the continuity critic missed, which then gets embedded in Episodes 4-8 because the state tracker was updated incorrectly.

### Callback Timing

Track whether callbacks are landing on schedule across the season. The continuity critic should flag overdue callbacks, but the meta-critic can detect patterns (e.g., "callbacks in the B-story are consistently late").

---

## Refinement Notes Format

**Good:** "Continuity critic for episodes 4-6: Episodes 1-3 continuity critics did not check physical state consistency (injuries, conditions). For episodes 4-6, the continuity critic MUST verify physical state claims against `state/character_state_tracker.json`."

**Bad:** "Keep up the good work on continuity."
