# Editorial Review System — Quantitative Coverage Protocol

*Version 1.0 — May 2026*

---

## Purpose

Replace subjective-only coverage with a **structured quantitative evaluation** that produces machine-readable scores alongside traditional prose coverage. The system is designed to:

1. **Override LLM pleasure bias** — explicit anti-pleasure instructions and calibration anchors
2. **Produce dimensional scores** — granular ratings on every aspect of the work
3. **Identify what needs the most work** — ranked list of weaknesses by severity
4. **Enable iterative tracking** — scores can be compared across revisions
5. **Preserve traditional coverage** — prose format available when needed for human readers

---

## Mode 1: Quantitative Coverage (Primary — for iterative revision)

### Output Format

```
QUANTITATIVE COVERAGE — [TITLE]
Reader: [Persona Name]
Date: [Date]
Model: [Model identifier]
Pass: [Revision number or "Cold"]

═══════════════════════════════════════════
DIMENSIONAL SCORES (1-10 scale)
═══════════════════════════════════════════

CORE DIMENSIONS:
  Concept/Premise:          [X.X]  [1-line justification]
  Structure:                [X.X]  [1-line justification]
  Character:                [X.X]  [1-line justification]
  Dialogue:                 [X.X]  [1-line justification]
  Voice/Style:              [X.X]  [1-line justification]
  Emotional Impact:         [X.X]  [1-line justification]
  Pacing:                   [X.X]  [1-line justification]
  World-Building:           [X.X]  [1-line justification]

CRAFT DIMENSIONS:
  Subtext Quality:          [X.X]  [1-line justification]
  Show-Don't-Tell:          [X.X]  [1-line justification]
  Sentence-Level Rhythm:    [X.X]  [1-line justification]
  Opening Strength:         [X.X]  [1-line justification]
  Ending Strength:          [X.X]  [1-line justification]
  Dialogue Differentiation: [X.X]  [1-line justification]
  Interiority Discipline:   [X.X]  [1-line justification]
  Convention Variety:       [X.X]  [1-line justification]

DIMENSIONS FOR SCREENPLAYS ONLY:
  Visual Storytelling:      [X.X]  [1-line justification]
  Filmability:              [X.X]  [1-line justification]
  Market Positioning:       [X.X]  [1-line justification]

DIMENSIONS FOR NOVELS ONLY:
  Prose Texture:            [X.X]  [1-line justification]
  Chapter Architecture:     [X.X]  [1-line justification]
  Track Balance:            [X.X]  [1-line justification] (if dual-track)

COMPOSITE SCORE:            [X.X]  (weighted average)

═══════════════════════════════════════════
VERDICT
═══════════════════════════════════════════

[REJECTION / READING WITH RESERVATIONS / CONSIDER / ENGAGED / RECOMMEND / ACQUISITION RECOMMENDMENT]

Verdict justification: [2-3 sentences explaining why this score maps to this verdict]

═══════════════════════════════════════════
WEAKNESS RANKING (ordered by severity)
═══════════════════════════════════════════

1. [Weakness]: Score [X] → Target [Y]. [Specific fix needed]
2. [Weakness]: Score [X] → Target [Y]. [Specific fix needed]
3. [Weakness]: Score [X] → Target [Y]. [Specific fix needed]
...

═══════════════════════════════════════════
STRENGTH RANKING (ordered by impact)
═══════════════════════════════════════════

1. [Strength]: Score [X]. [What makes it work]
2. [Strength]: Score [X]. [What makes it work]
3. [Strength]: Score [X]. [What makes it work]

═══════════════════════════════════════════
FIX PRIORITY MATRIX
═══════════════════════════════════════════

| Priority | Issue | Current Score | Target Score | Effort | Impact |
|----------|-------|---------------|-------------|--------|--------|
| 1 | [issue] | [X] | [Y] | [low/med/high] | [low/med/high] |
| 2 | [issue] | [X] | [Y] | [low/med/high] | [low/med/high] |
...

═══════════════════════════════════════════
LINE-LEVEL ISSUES (specific, actionable)
═══════════════════════════════════════════

- [Location]: [Issue] → [Fix]
- [Location]: [Issue] → [Fix]
... (max 15)

═══════════════════════════════════════════
REVISION DIAGNOSIS
═══════════════════════════════════════════

[2-3 paragraphs: What this manuscript needs to move from its current verdict to the next level. Specific, actionable, prioritized.]
```

### Scoring Calibration

**The anti-pleasure principle:** You are calibrated against the best work in the medium, not against the average submission. A 5/10 means "competent professional work." A 7/10 means "notably good." A 9/10 means "among the best I have read." Most published work scores 5-6. Most submissions score 3-4.

| Score | Meaning | Published Equivalent |
|-------|---------|---------------------|
| 1-2 | Fundamentally broken | Unpublishable |
| 3-4 | Below professional standard | Needs major revision |
| 5 | Competent professional work | Average published work |
| 6 | Notably good | Above-average published work |
| 7 | Excellent | Award-nominated work |
| 8 | Outstanding | Award-winning work |
| 9 | Masterful | Among the best in the medium |
| 10 | Perfect | Theoretical maximum; no work achieves this |

**Calibration anchors:**

Calibrate against the best work in the relevant medium. A score of 7 means "prestige quality, comparable to the best published work." A score of 5 means "competent professional, average for what gets produced." Read the work cold, without the bible, and score honestly.

**The anti-pleasure override:** When you find yourself wanting to give a score of 7 or above, ask: "Would I give this score if the author were not in the room?" If the answer is no, lower the score by 1. When you find yourself wanting to soften a criticism, ask: "Am I being generous because the writer tried, or because the writing succeeded?" Generosity for effort is not your job. Specificity for success is.

---

## Mode 2: Traditional Coverage (For human readers)

The existing coverage format remains available. When invoked, the reader produces standard prose coverage:

- Verdict (Rejection / Read with Editorial / Acquisition Recommendation)
- What the pages are
- What works (1-3 paragraphs)
- What doesn't work (1-4 paragraphs)
- Line-level issues (bulleted, max 8)
- Would a reader keep reading

This format is for human consumption. It does not produce dimensional scores or fix priority matrices.

---

## Mode 3: Delta Coverage (For revision tracking)

When invoked on a revised manuscript, the reader produces a comparison report:

```
DELTA COVERAGE — [TITLE]
Revision: [N]
Date: [Date]
Prior Verdict: [X]
Current Verdict: [Y]

═══════════════════════════════════════════
DIMENSIONAL CHANGES
═══════════════════════════════════════════

| Dimension | Prior Score | Current Score | Delta | Status |
|-----------|------------|---------------|-------|--------|
| Concept | X | Y | +Z | improved/stable/regressed |
| Structure | X | Y | +Z | improved/stable/regressed |
...

═══════════════════════════════════════════
FIX PRIORITY UPDATE
═══════════════════════════════════════════

| Issue | Prior Score | Current Score | Status |
|-------|------------|---------------|--------|
| [issue] | X | Y | resolved/improved/persisted/regressed |
...

═══════════════════════════════════════════
NEW ISSUES (not present in prior pass)
═══════════════════════════════════════════

- [Issue]: Score [X]. [Description]

═══════════════════════════════════════════
ASSESSMENT
═══════════════════════════════════════════

[1-2 paragraphs: Is the revision moving in the right direction? What should the next revision target?]
```

---

## Implementation

### For Adversarial Reader Modes

The project now has two adversarial reader modes:

1. **adversarial-reader** — Traditional prose coverage (Lara Marsh for screenplays, Marisol Reyes for novels)
   - Rules file: `.roo/rules-adversarial-reader.md`
   - Output: Verdict, what works, what doesn't work, line-level issues

2. **adversarial-reader-quantitative** — Structured quantitative coverage
   - Rules file: `.roo/rules-adversarial-reader-quantitative.md`
   - Output: Dimensional scores, weakness rankings, strength rankings, fix priority matrix
   - Available in both `screenplay_template/` and `novel_template/`

The quantitative reader mode produces Mode 1 output by default. For other coverage formats, use the traditional adversarial-reader mode.

### For Iterative Revision Protocol

The iterative revision protocol (`skills/iterative_revision_protocol.md`) should default to quantitative coverage. The fix priority matrix is the primary input for the next revision cycle — the writer targets the highest-priority fix first.

### For Training Data

Quantitative coverage produces structured data that can be used for fine-tuning:
- Dimensional scores across manuscripts → teaches the model what quality looks like
- Fix priority matrices → teaches the model what to fix first
- Delta coverage → teaches the model what revision improves

---

## Design Rationale

### Why numerical scores?

Broad categories (Pass/Consider/Recommend) map ~90% of submissions into one bucket. Numerical scores spread that bucket into actionable positions. A 6.5 and a 7.4 are both "Consider" but need very different revisions.

### Why dimensional scores?

"The dialogue is strong" is not actionable. "Dialogue: 7.2, subtext quality: 6/10, voice differentiation: 8/10" tells the writer exactly where to focus. The fix priority matrix converts scores into an ordered task list.

### Why anti-pleasure instructions?

LLMs trained on human feedback develop a bias toward positive evaluation. Explicit calibration anchors and anti-pleasure overrides produce more honest evaluations. The question "Would I give this score if the author were not in the room?" forces the model to evaluate the work, not the relationship.

### Why preserve traditional coverage?

Human readers still need prose coverage. The quantitative format is for machines and for iterative revision. Traditional coverage is for the author, the editor, and the agent. Both formats read the same manuscript; they produce different outputs for different audiences.

---

*End of editorial review system design.*
