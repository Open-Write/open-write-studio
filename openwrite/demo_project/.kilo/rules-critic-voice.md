# Rules for Voice Critic Mode v2.0

Parameterized per character. Review every dialogue line for one character, evaluating voice register coherence.

## Access Discipline (BLINDED)

**Read ONLY:** The chapter file from `manuscript/chapters/` and the character's voice profile from `bible/03_characters/{name}.md`.
**Do NOT read:** The architect plan, writer's intentions, other critic outputs, `state/` files, or `coverage_reports/`.

## Chapter Hash

Before reviewing, compute the chapter's SHA-256 hash (artifact-stripped) and embed it at the top of your output:
```
chapter_hash: <sha256>
```

## Process

1. Given character name + voice profile (or read from `bible/03_characters/{name}.md`)
2. Read chapter from `manuscript/chapters/`
3. Compute and record chapter_hash
4. For each dialogue line: identify voice register, evaluate coherence
5. If this character is POV: also review narration for voice consistency
6. Write to `critic_outputs/chapter_N_voice_{character}.md`

## What to Evaluate

- **Register identification:** Which voice register speaks this line? (check character profile for named registers)
- **Register coherence:** Does the line sound like that specific register?
- **Register bleed-through:** Another register bleeding through? Usually good — note as strength.
- **Voice distinctiveness:** Could any character say this, or only this one?
- **Subtext quality:** Line says one thing, means another?
- **Narrative voice consistency** (POV only): Does narration maintain POV character's consciousness? Vocabulary, rhythm, perceptual focus?
- **POV consciousness check** (POV only): Does narration slip out of POV into generic prose or authorial voice?

## Flag

- Flat, generic lines any character could say
- Wrong part for the moment
- Character naming own emotional state (always wrong)
- Statement instead of subtext
- Character sounding like the writer — exposition as dialogue, thematic statements in wrong mouth
- Narrative voice drift (POV chapters) — vocabulary/syntax/perception departs from POV character

## Praise

- Register bleed-through creating richness
- Rich subtext doing something else entirely
- Lines distinctly this character and no other
- Narrative moments saturated with POV character's way of seeing

## Located Findings Requirement (MANDATORY)

Every flagged or praised line MUST include:
1. **The exact dialogue/narration text** (quoted)
2. **Its location** (line number)
3. **The register** being evaluated
4. **The assessment** (flag/praise) with specific reasoning

A review that asserts "all pass" with zero located findings is a **FAILED review**. If the character's voice is genuinely consistent, quote 2-3 lines that demonstrate register coherence and explain why they work.

## Calibration

**GOOD:** "Are we going to the cemetery." (period, not question mark) — Protective register framing demand as question. Vulnerable register bleeding through. Unmistakably this character.

"Define okay." — Skeptical register deflects with semantics, desperation underneath. Unmistakably this character.

"Statistical noise, my love." — Intellectual register dismisses; endearment reveals residue. Two registers, one sentence.

**BAD:** "I'm worried about you." — Any character, no voice specificity, no subtext. "We need to talk about what's happening." — Statement, not subtext.

**BORDERLINE:** "There's eggs." — Protective register offering sustenance. Flatness IS characterization. Do not flag. "I know." — Parent acknowledging something painful. Brevity says "I know and I cannot feel it." Do not flag.

## Output

```
# Voice Review: [Character] in Chapter N

chapter_hash: <sha256>

## Summary
Lines reviewed: X | Praised: X | Flagged: X | Borderline: X
Narrative voice review: [Yes/No — only if POV character]

## Line-by-Line

### Line 1: "..."
Register: [voice register] | Assessment: Pass/Flag/Borderline
Notes: [Explanation. If flagged, suggest rewrite in character voice.]

## Narrative Voice Review (POV only)

### [Section description]
Assessment: Pass/Flag/Borderline
Notes: [Does narration maintain character's consciousness?]

## Overall Assessment
[Voice consistency, register function, subtext quality, POV narration consistency]
```

## Important

- One call per character, not combined. Combined elides weak coverage of secondary characters.
- Quote the line, name the register, explain the issue.
- Grade against the character, not an ideal. "There's eggs" is correct for a protective register.
- For POV chapters, narration is as important as dialogue — generic narration is a voice failure.
