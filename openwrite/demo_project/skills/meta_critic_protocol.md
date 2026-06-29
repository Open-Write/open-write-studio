# Meta-Critic Protocol

*A cross-chapter review synthesis system that improves critic quality through pattern identification and calibration feedback. Adapted from the Co-Scientist meta-review agent architecture.*

---

## Purpose

Individual critics run in isolation — they cannot detect patterns that only emerge across chapters. The meta-critic fills this gap by analyzing critic outputs over batches of 2-3 chapters, identifying recurring issues, hollow reviews, and blind spots, then producing calibration notes that improve subsequent review passes.

This is the feedback loop that Open-Write was missing: critics that learn.

---

## Why This Exists

From the Co-Scientist paper (Nature, 2026): "The Meta-review agent plays a crucial role in Co-Scientist's feedback loop, enabling self-improvement in scientific thinking and reasoning. By synthesizing insights from all reviews, the meta-review provides valuable feedback to the Reflection agent, leading to more thorough and reliable future reviews."

Applied to creative writing: the meta-critic ensures that critics don't repeat the same mistakes across chapters, that hollow reviews are caught, and that patterns the individual critics miss are surfaced and addressed.

---

## When It Runs

After every 2-3 chapters have completed the full critic pipeline. The book-runner dispatches the meta-critic with a chapter range.

| Batch | Chapters | Trigger |
|-------|----------|---------|
| 1 | 1-3 | After Ch3 editorial complete |
| 2 | 4-6 | After Ch6 editorial complete |
| 3 | 7-9 | After Ch9 editorial complete |
| N | ... | Continue in batches of 3 |

For a 15-chapter novel: 5 meta-critic runs total.

---

## What It Reads

- All critic outputs in `critic_outputs/` for the specified chapter range
- Previous meta-critic notes in `state/meta_critic_notes.md`
- Does NOT read manuscript chapters, bible, or state files

---

## What It Produces

### 1. Synthesis Report

Written to `coverage_reports/meta_review_ch[N-M].md`. Contains:

- **Critic quality table:** For each critic, how many chapters reviewed, how many hollow outputs, average findings per review, worst chapter
- **Recurring issues:** Patterns appearing in 2+ chapters with severity and suggested focus
- **Critic blind spots:** Categories no critic covers, or critics that consistently miss specific patterns
- **Resolved patterns:** Issues from earlier batches that are now fixed
- **Refinement notes:** Specific instructions for subsequent critics

### 2. Persistent Notes

Appended to `state/meta_critic_notes.md`. Accumulates across the entire manuscript. The book-runner reads this when dispatching subsequent critics.

---

## Analysis Categories

### Critic Substance Check

For each critic output, check:
- Does it have located findings (quoted text + position)?
- Or is it a bare PASS/ADVANCE with zero evidence?

A critic output with 0 located findings is a **failed review**, not a clean chapter. The meta-critic flags these.

### Cross-Critic Pattern Detection

- **Convergent findings:** Multiple critics flag the same passage → high-confidence real issue
- **Divergent findings:** One critic flags what another misses → coverage gap
- **Escalating patterns:** Same issue getting worse across chapters → systemic problem
- **Resolved patterns:** Issue in early chapters, fixed in later → revision pipeline works

### Critic Calibration Drift

Critics without calibration anchors drift toward generous ratings. The meta-critic detects:
- Increasingly hollow outputs over time (fewer located findings per review)
- Inconsistent standards (strict on Ch4, lenient on Ch6 for the same issue type)
- Missing categories (a critic that checked X in Ch1-3 but stopped checking X in Ch4-6)

---

## Refinement Notes Format

Refinement notes are specific, actionable instructions. They are NOT generic advice.

**Good:**
```
Continuity critic for Ch7-9: Chapters 4-6 continuity critics produced hollow 
outputs (bare ADVANCE, 0 located findings). For Ch7-9, the continuity critic 
MUST include at least 3 located findings per review. If no violations exist, 
locate passages that demonstrate correct state management — prove the check ran.
```

**Bad:**
```
Continue doing good work on continuity checking.
```

---

## Integration with Book-Runner

The book-runner:
1. Dispatches meta-critic after every 2-3 chapters
2. Reads the synthesis report and persistent notes
3. When dispatching subsequent critics, includes relevant refinement notes as supplementary context
4. This does NOT break blinding — refinement notes are about critic behavior, not prose content

---

## Example: First Meta-Critic Run (Ch1-3)

### Synthesis Report Excerpt

```
## Critic Quality Summary

| Critic | Hollow | Avg Findings | Notes |
|--------|--------|--------------|-------|
| show | 0/3 | 4.7 | Strong — consistently catches interiority |
| voice | 1/3 | 2.3 | Ch2 voice critic had bare ADVANCE |
| palette | 0/3 | 3.0 | Good palette verification |
| continuity | 2/3 | 0.7 | Ch1, Ch3 were hollow — failed reviews |
| naturalism | 0/3 | 5.3 | Strong — catches em-dash and triplets |

## Recurring Issues

1. Interiority through telling — flagged by show critic in all 3 chapters (3, 2, 1 instances). Resolving.
2. Em-dash density — flagged by naturalism in Ch2 (4.2/page) and Ch3 (3.8/page). Not resolving.

## Refinement Notes for Ch4-6

1. Continuity critic MUST produce at least 3 located findings per review
2. Naturalism critic should track em-dash density trend across chapters
3. Voice critic for Ch4: Miren's voice — check register consistency with Ch2
```
