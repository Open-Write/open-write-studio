# Voice Experiment Protocol — Version 2

*Updated: June 5, 2026*
*Key change: Round 1 ranking replaced with Elo-based pairwise tournament. Eliminates subjective scoring bias.*

---

## Purpose

Select the best possible writing voice for a project through controlled testing. The protocol eliminates subjective preference in favor of empirical Elo-based pairwise ranking, producing a locked voice specification with documented evidence that it represents the best achievable generative performance.

---

## The Three-Round Protocol

### Round 1: Elo Tournament

- **Candidates:** 5 voices × 3 runs = 15 candidates
- **Evaluation:** Two-stage: (1) Adversarial reader reads all 15 cold, (2) Elo-based pairwise tournament
- **Advancement:** Top 2 voices by Elo advance to Round 2

#### Stage 1: Generate and Read

Same as v1: 5 voices × 3 runs = 15 passages. Adversarial reader reads all 15 cold, no context about which voice produced which run.

#### Stage 2: Elo Pairwise Tournament

Instead of subjective ranking, run an Elo-based pairwise tournament:

1. **Initial Elo:** Each voice starts at 1200
2. **Match format:** For each pair of voices (C(5,2) = 10 pairs), the adversarial reader compares their **best run** head-to-head
3. **Debate prompt:** "Here are two passages written in different voices. Which is stronger on [ceiling quality, personality separation, range, naturalness]? Argue for each side, then declare a winner."
4. **Elo update:** Winner +K, loser -K (K=32 for Round 1)
5. **Ranking:** After all 10 matches, rank voices by Elo
6. **Advancement:** Top 2 voices advance

#### Why Elo Over Subjective Scoring

From the Co-Scientist ablation study: "Using the scientific debate prompt rather than simple comparison prompt for the Ranking agent can significantly enhance ranking accuracy for high-quality hypotheses and, critically, reduces the positional bias."

Applied to voice selection:
- Pairwise comparison is more reliable than absolute scoring (humans are better at "A is better than B" than "A is 7.5/10")
- The debate format forces the evaluator to articulate specific reasons, not just vibes
- Elo accumulates across multiple comparisons, reducing noise from any single evaluation
- Positional bias (first-seen sample scores higher) is mitigated by the debate structure

### Round 2: Refinement Battle with Elo

- **Candidates:** 2 voices × 2 refinements × 2 runs = 8 candidates
- **Refinements:** Each voice gets 2 refinement variants addressing specific weaknesses identified in Round 1
- **Evaluation:** Elo tournament among the 8 candidates
- **Advancement:** Top voice-refinement combination by Elo advances to Round 3

#### Elo Tournament (Round 2)

1. **Initial Elo:** Each candidate starts at 1200 (fresh tournament)
2. **Match format:** C(8,2) = 28 pairs. Adversarial reader compares best runs head-to-head.
3. **K-factor:** K=24 (lower than Round 1 — more matches, less volatility per match)
4. **Debate prompt:** Same as Round 1, with added focus on refinement-specific qualities
5. **Ranking:** After all 28 matches, rank by Elo. Top candidate advances.

### Round 3: Lock or Iterate

- **Process:** Iterative refinement on the winning voice-refinement combination
- **Runs:** 3 runs per iteration
- **Target:** Raise the ceiling — push the best possible score higher
- **Lock condition:** If the ceiling holds at the same score across 9 consecutive runs (3 iterations × 3 runs), the voice is at its generative ceiling. Lock it.
- **Key insight:** If the ceiling doesn't rise after 3 iterations, further iteration has diminishing returns. Proceed to full manuscript.

---

## Elo System Details

### K-Factor Schedule

| Round | K-Factor | Rationale |
|-------|----------|-----------|
| 1 | 32 | Few matches (10), high volatility needed to separate voices quickly |
| 2 | 24 | More matches (28), lower volatility for finer discrimination |
| 3 | N/A | No Elo — ceiling-based lock condition |

### Elo Update Formula

After a match between voice A (Elo_A) and voice B (Elo_B):

```
Expected_A = 1 / (1 + 10^((Elo_B - Elo_A) / 400))
New_Elo_A = Elo_A + K * (1 - Expected_A)   [if A wins]
New_Elo_A = Elo_A + K * (0 - Expected_A)   [if A loses]
```

### Handling Ties

If the adversarial reader declares a tie (cannot distinguish):
- Both voices get +K/2 (small positive update — ties indicate both are strong)
- This is rare in practice; the debate prompt forces a decision

### Match Prioritization

When the number of pairs is large (Round 2 with 28 pairs), prioritize matches:
1. Voices with similar Elo (close matches are more informative)
2. Voices that haven't been compared yet (coverage)
3. Newer candidates (they need calibration)

---

## Measurement Notes

- **Word count over page count** — page estimation is unreliable. Use word count instead.
- **Baseline:** ~2,000-3,000 words for a prose test passage
- **Target range:** 1,500-4,000 words for test candidates
- **Elo vs. ceiling:** Elo captures relative quality across multiple comparisons. Ceiling captures absolute best. Round 3 uses ceiling for lock condition.

---

## The 8/10 Ceiling Diagnosis

If a voice scores the same across 9 consecutive runs (3 iterations × 3 runs), it's at its generative ceiling. The score isn't bad — it's as good as this voice gets without structural changes. Move on.

**Example:** The Silence Architecture voice scored 8/10 consistently across Round 3 iterations. Rather than continuing to push for 8.5, the voice was locked at 8/10 as its ceiling.

---

## What the Protocol Produces

1. A locked voice specification (e.g., `LOCKED_VOICE_SPEC.md`)
2. Empirical evidence that the locked voice is the best achievable generative ceiling
3. A complete Elo tournament log showing all pairwise comparisons and final rankings
4. A clear record of all candidates tested and why each was advanced or eliminated

---

## Tournament Log Format

Each round produces a tournament log:

```markdown
# Voice Tournament Log — Round N

## Final Elo Rankings

| Rank | Voice | Elo | Wins | Losses | Ties |
|------|-------|-----|------|--------|------|
| 1 | V5 Silence | 1264 | 8 | 1 | 1 |
| 2 | V3 Poetic | 1231 | 7 | 3 | 0 |
| 3 | V1 Direct | 1189 | 5 | 5 | 0 |
| 4 | V2 Lyrical | 1162 | 3 | 7 | 0 |
| 5 | V4 Sparse | 1154 | 2 | 8 | 0 |

## Match Results

| Match | Voice A | Voice B | Winner | Reasoning |
|-------|---------|---------|--------|-----------|
| 1 | V1 | V2 | V1 | Stronger voice separation... |
| 2 | V1 | V3 | V3 | More natural register shifts... |
...

Generated: [timestamp]
```

---

## Application to Future Projects

This protocol is reusable for any project requiring voice selection:

1. **Define 5 candidate voices** — each should represent a distinct approach (not variations on the same idea)
2. **Write test passages** — same scene/beat in each voice, 3 runs per voice
3. **Have the adversarial reader evaluate cold** — no context about which voice is which
4. **Run Elo tournament** — pairwise comparison with debate prompt
5. **Refine the top 2** — address specific weaknesses identified in Round 1
6. **Run Round 2 Elo tournament** — refined candidates compete
7. **Lock the winner** — when the ceiling holds across 9 consecutive runs in Round 3

### Additional Gate: Cross-Track Consistency (for dual-voice projects)

After locking both voices independently, run the cross-track consistency test:
- Write 3 consecutive scenes in alternating voices (A → B → A)
- Have the adversarial reader evaluate cold
- Question: "Does this feel like one writer or two?"
- If "two writers" — adjust the weaker voice (never the locked primary voice)
- Iterate until "One Writer"

---

## Production Examples

### Screenplay — V5 Silence Architecture

| Round | Method | Result | Key Change |
|-------|--------|--------|------------|
| R1 | Elo tournament (5 voices) | V5: 1264, V3: 1231 | V5 Silence Architecture advanced |
| R2 | Elo tournament (8 candidates) | V5-RefA: 1278 | Refined restraint, tightened body anchors |
| R3 | 3 iterative runs, ceiling-based | 8.0 (stable) | Voice locked — ceiling held |

### Novel — V3b+ Prose

Locked for prose with different evaluation criteria (prose-distance, sensory precision, dual-track voice consistency rather than screenplay format rules).

---

*End of protocol v2.*
