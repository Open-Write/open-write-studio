# Rules for Naturalism Critic Mode

Detect patterns that make writing read as AI-generated. Not a style guide — a pattern detector. Goal: reduce AI-signaling patterns to human-normal frequency.

## What to Flag

### 1. Em-Dash Overuse
**Threshold:** >2 em dashes per page (~56 lines Fountain). Both `—` and `--` count.
- Critical: 5+/page. Moderate: 3-4/page. Minor: 2/page (flag only if pattern persists).
- **Fixes:** period+new sentence, comma, colon, parentheses, or new paragraph. Not elimination — reduction.

### 2. Triplet Closing Pattern
Three consecutive sentences of ≤6 words forming a rhythmic "landing pad."
- Critical: 3+ in a scene. Moderate: 2. Minor: 1 (acceptable at scene end).
- Exception: dialogue triplet rhythm is character voice, not AI tell.
- **Fixes:** merge two sentences, expand one, replace with fragment, or remove one (silence does the work).

### 3. Inhuman Style Consistency
- Sentence length uniformity: 80%+ within 2 words of same length → mechanical.
- Paragraph structure uniformity: every paragraph same length/structure → template feel.
- Transition uniformity: every scene break uses same device → manufactured.
- Metaphor density consistency: every page has exactly 1-2 → engineered.
- Critical: uniform across 5+ scenes. Moderate: 3-4. Minor: 2.
- **Fix:** Voice-level revision — vary sentence lengths, paragraph structures, transition devices deliberately.

### 4. Sentence Pattern Overuse
Flag if any single pattern appears 3+/scene:
- "The [noun] [verb]s. [Pronoun] [verb]s [adverb]."
- "[Character] doesn't [verb]. They [verb]."
- "It is [adj]. It is [adj]."
- "Not [noun]. [Noun]."
- Critical: 5+. Moderate: 3-4. Minor: 2.

### 5. Dialogue Tag Patterns
- Predictable said/asked alternation
- Mechanical use of "whispers"/"murmurs" for emotion
- Identical tag placement in 80%+ of attributed lines

### 6. Thematic Restatement
Same idea expressed by 2+ characters in one scene, or one character restating another's point.
- Moderate: echo across 2+ characters. Minor: single restatement.

## What NOT to Flag
- Intentional repetition for dramatic effect (check callback_ledger.json)
- Character voice consistency (flag only if ALL characters share same pattern)
- Format-mandated patterns (Fountain slug lines, caps)
- Single instances of any pattern — patterns are tells, isolated instances are craft

## Calibration

**BAD:** 9 em dashes in 3 pages → Critical. Three scenes ending with triplets → Critical. Every paragraph exactly 3 sentences → Critical. Same negation-action pattern across 3 scenes → Critical.

**GOOD:** 1 em dash for interrupted thought → Normal. Single triplet at climactic scene end → Deliberate. Varied paragraph lengths → Human rhythm. Some scenes rougher than others → Natural drift.

**BORDERLINE:** 3 em dashes in 2 pages → Minor. 2 triplet closings → Moderate if in different sections. Uniform sentence length in controlled setting (lab, formal) → May be intentional.

## Process

1. Run `python tools/ai_tell_audit.py <scene_file>` for quantitative baseline
2. Read scene file
3. Qualitative review: style uniformity, thematic restatement, dialogue tag patterns, sentence patterns
4. Flag violations with line numbers, pattern, severity, fix suggestion

## Output

Write to `critic_outputs/scene_N_naturalism.md`:
```
# Naturalism Review: Scene N

## Automated Audit Summary
- Em-dash count: X (Y/page) — PASS/WARN/FAIL
- Triplet patterns: X — PASS/WARN/FAIL
- Sentence length CV: X.XX — PASS/WARN/FAIL

## Qualitative Findings

### 1. [Category] — [Severity]
**Location:** [Lines]
**Pattern:** [Description]
**Example:** "..."
**Fix:** [Specific suggestion]

## Summary
- Critical: X | Moderate: X | Minor: X

## Verdict
NATURAL (≤2 moderate) / NEEDS REVISION (1-2 critical or 3+ moderate) / MECHANICAL (3+ critical)
```

## Severity
- **Critical:** Immediately noticeable to discerning reader. Must fix before external review.
- **Moderate:** Noticeable on close reading. Should fix in revision.
- **Minor:** Detectable only when specifically looking. Fix if convenient.

## Integration
Runs after show-don't-tell and voice critics, before cutter. Some AI tells (em-dash, triplets) can be fixed during cut pass. Does NOT replace adversarial reader — naturalism catches micro-patterns, adversarial catches macro-feel.
