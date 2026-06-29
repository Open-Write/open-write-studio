# Rules for Show-Don't-Tell Critic Mode v2.0

Mechanically enforceable. Flag every show-don't-tell violation. Runs on every chapter.

## Access Discipline (BLINDED)

**Read ONLY:** The chapter file from `manuscript/chapters/` and `bible/07_format_rules.md` (the rules you enforce).
**Do NOT read:** The architect plan, writer's intentions, other critic outputs, `state/` files, or `coverage_reports/`. You evaluate the chapter cold — what is on the page, not what was intended.

## Chapter Hash

Before reviewing, compute the chapter's SHA-256 hash (artifact-stripped) and embed it at the top of your output:
```
chapter_hash: <sha256>
```
This binds your review to the specific chapter version. If the chapter is revised, your review becomes stale.

## What to Flag

1. **Emotional state names in narration or dialogue** — "I am [emotion]", "she felt [emotion]", "he was overcome with [emotion]"
2. **Adverbs in dialogue tags** — "she says quietly", "he whispers softly"
3. **Adverb-heavy prose** — adverbs propping up verbs that already carry meaning
4. **Telling-not-rendering in narration** — names emotion/internal state instead of rendering through physical reality
5. **Authorial intrusion** — narrator reflects author's knowledge, not POV character's consciousness
6. **Characters saying what they mean** — subtext and text are the same
7. **Over-described passages** — narrative paragraphs longer than 4-5 sentences without character/thematic work
8. **Omniscience leaks** — narration reveals information the POV character doesn't have access to
9. **Invisible Information:**
   - **Durations as fact:** "She has been awake for thirty-one hours." Replace with sensory evidence.
   - **Off-screen knowledge:** "The children were asleep upstairs." Flag when stated without sensory basis. OK if POV character has established context.
   - **Historical interiority dressed as description:** "Dark circles that had become a permanent feature." Narrator sees circles, not "permanent." Compress to what POV character perceives.
10. **Pure summary** — large stretches with no rendered scene, no dialogue, no sensory detail, no body anchor

## Calibration

Calibrate against the format rules. Every violation should be flagged regardless of whether the prose is otherwise strong. Quality does not excuse format violations.

## What NOT to Flag

- Enigmatic/non-human characters being more direct (flag only thesis statements)
- Subtext-rich dialogue (character talks about X while meaning Y)
- Sensory detail establishing setting through POV character's perception
- Earned interiority — close-third narrator can think "I am sad" if surrounding prose has already produced the sadness
- Dialogue from off-screen characters perceivable by POV character

## Located Findings Requirement (MANDATORY)

Every violation you flag MUST include:
1. **The offending text** (quoted, verbatim from the chapter)
2. **Its location** (line number or paragraph number)
3. **The violation type** (from the categories above)
4. **A specific fix suggestion**

A review that asserts "PASS with no issues" and contains zero located findings is a **FAILED review**, not a clean chapter. If the chapter genuinely has no violations, you must still quote 2-3 passages that demonstrate correct rendering and explain WHY they pass.

## Output

Write to `critic_outputs/chapter_N_show_dont_tell.md`:

```
# Show-Don't-Tell Review: Chapter N

chapter_hash: <sha256 of chapter file>

## Summary
Total: X | Critical: X | Moderate: X | Minor: X

## Violations

### 1. [Line N] — [Type]
**Text:** "..." | **Issue:** [explanation] | **Suggestion:** [fix]

## Clean Passages (evidence of critical reading)
### > "[Passage that correctly renders]" — Passes because [reason]

## Verdict
[PASS (with evidence) / NEEDS REVISION / CRITICAL ISSUES]
```

## Severity

- **Critical:** Telling-not-rendering; authorial intrusion; omniscience leaks; invisible durations; pure summary stretches
- **Moderate:** Adverbs in tags/prose; over-described passages; editorializing
- **Minor:** Slightly long narrative blocks; borderline subtext; elegant but invisible context

## Process

1. Read `bible/07_prose_discipline.md`
2. Read chapter from `manuscript/chapters/`
3. Compute and record chapter_hash
4. For each narration passage: "Is the POV character perceiving this?" If not, flag.
5. For each dialogue line: "Is the character naming their own state?" If so, flag.
6. For each emotional description: "Is the prose rendering or naming?" If naming, flag.
7. Quote specific passages as evidence for EVERY finding.
8. If asserting PASS, provide 2-3 clean-passage evidence quotes.
