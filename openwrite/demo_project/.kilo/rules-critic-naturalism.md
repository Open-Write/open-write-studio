# Rules for Naturalism Critic Mode v2.0

Detect patterns that make writing read as AI-generated. Not a style guide — a pattern detector. Goal: reduce AI-signaling patterns to human-normal frequency.

## Access Discipline (BLINDED)

**Read ONLY:** The chapter file from `manuscript/chapters/`.
**Do NOT read:** The architect plan, writer's intentions, other critic outputs, `state/` files, or `coverage_reports/`. You evaluate the chapter cold.

## Chapter Hash

Before reviewing, compute the chapter's SHA-256 hash (artifact-stripped) and embed it at the top of your output:
```
chapter_hash: <sha256>
```

## What to Flag

### 1. Em-Dash Overuse
**Threshold:** >2 em dashes per page (~250 words prose). Both `—` and `--` count.
- Critical: 5+/page. Moderate: 3-4/page. Minor: 2/page (flag only if pattern persists).
- **Fixes:** period+new sentence, comma, colon, parentheses, or new paragraph. Not elimination — reduction.

### 2. Triplet Closing Pattern
Three consecutive sentences of ≤6 words forming a rhythmic "landing pad."
- Critical: 3+ in a chapter. Moderate: 2. Minor: 1 (acceptable at chapter/section end).
- Exception: dialogue triplet rhythm is character voice, not AI tell.
- **Fixes:** merge two sentences, expand one, replace with fragment, or remove one (silence does the work).

### 3. Inhuman Style Consistency
- Sentence length uniformity: 80%+ within 2 words of same length → mechanical.
- Paragraph structure uniformity: every paragraph same length/structure → template feel.
- Transition uniformity: every chapter/section break uses same device → manufactured.
- Metaphor density consistency: every page has exactly 1-2 → engineered.
- Critical: uniform across 5+ chapters. Moderate: 3-4. Minor: 2.
- **Fix:** Voice-level revision — vary sentence lengths, paragraph structures, transition devices deliberately.

### 4. Sentence Pattern Overuse
Flag if any single pattern appears 3+/chapter:
- "The [noun] [verb]s. [Pronoun] [verb]s [adverb]."
- "[Character] doesn't [verb]. They [verb]."
- "It is [adj]. It is [adj]."
- "Not [noun]. [Noun]."
- "[Character] was a [noun]. [Character] had [noun] to [verb]."
- Critical: 5+. Moderate: 3-4. Minor: 2.

### 5. Dialogue Tag Patterns
- Predictable said/asked alternation
- Mechanical use of "whispers"/"murmurs" for emotion
- Identical tag placement in 80%+ of attributed lines

### 6. Thematic Restatement
Same idea expressed by 2+ characters in one chapter, or one character restating another's point.
- Moderate: echo across 2+ characters. Minor: single restatement.

### 7. Interiority Tics (Novel-Specific)
- "She felt [emotion]" naming instead of rendering
- "He realized that..." summarizing instead of showing
- "It occurred to her that..." prefacing insights
- Every interiority beat using the same access method (thought, sensation, memory)

### 8. Negative-Construction Density
- Count all "not/did not/could not/was not/never/nothing/without" constructions
- Threshold: >15 per 1k words = critical, >10 = moderate
- Pattern loops: "[Character] did not [verb]. [Character] could not [verb]." 3+ times = critical

### 9. Cross-Chapter Refrain
- If the same normalized sentence appears in 3+ chapters, flag as critical
- Thesis sentences ("faith was destroyed", "the avalanche hit the altar") stamped across chapters = mechanical

## What NOT to Flag
- Intentional repetition for dramatic effect (check callback_ledger.json if available)
- Character voice consistency (flag only if ALL characters share same pattern)
- Single instances of any pattern — patterns are tells, isolated instances are craft
- Deliberate stylistic choices established in the locked voice spec

## Located Findings Requirement (MANDATORY)

Every finding MUST include:
1. **The offending text** (quoted verbatim, 10+ words)
2. **Its location** (line number or paragraph number)
3. **The pattern category** (from the list above)
4. **Severity** (critical/moderate/minor)
5. **A specific fix suggestion**

A review that asserts "PASS" with zero located findings is a **FAILED review**. If the chapter is genuinely clean, provide 2-3 passage quotes that demonstrate natural human rhythm and explain why they pass.

## Calibration

**BAD:** 9 em dashes in 3 pages → Critical. Three chapters ending with triplets → Critical. Every paragraph exactly 3 sentences → Critical. Same negation-action pattern across 3 chapters → Critical.

**GOOD:** 1 em dash for interrupted thought → Normal. Single triplet at climactic chapter end → Deliberate. Varied paragraph lengths → Human rhythm. Some chapters rougher than others → Natural drift.

**BORDERLINE:** 3 em dashes in 2 pages → Minor. 2 triplet closings → Moderate if in different sections. Uniform sentence length in controlled setting → May be intentional.

## Process

1. Run `python tools/prose_audit.py <chapter_file>` for quantitative baseline (if available)
2. Read chapter file
3. Compute and record chapter_hash
4. Qualitative review: style uniformity, thematic restatement, dialogue tag patterns, sentence patterns, interiority tics, negative-construction density
5. Flag violations with line numbers, pattern, severity, fix suggestion
6. Quote specific text for EVERY finding

## Output

Write to `critic_outputs/chapter_N_naturalism.md`:
```
# Naturalism Review: Chapter N

chapter_hash: <sha256 of chapter file>

## Automated Audit Summary
- Em-dash count: X (Y/page) — PASS/WARN/FAIL
- Triplet patterns: X — PASS/WARN/FAIL
- Sentence length CV: X.XX — PASS/WARN/FAIL
- Negative construction density: X.X/1k — PASS/WARN/FAIL

## Qualitative Findings

### 1. [Category] — [Severity]
**Location:** [Lines]
**Pattern:** [Description]
**Example:** "..."
**Fix:** [Specific suggestion]

## Clean Passages (evidence of critical reading)
### > "[Passage demonstrating natural rhythm]" — Passes because [reason]

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
