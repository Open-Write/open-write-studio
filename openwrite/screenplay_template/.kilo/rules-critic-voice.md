# Rules for Voice Critic Mode

Parameterized per character. Review every dialogue line for one character, evaluating voice register coherence.

## Process

1. Given character name + voice profile (or read from `bible/03_characters/{name}.md`)
2. Read scene from `script/scenes/`
3. For each dialogue line: identify voice register, evaluate coherence
4. Write to `critic_outputs/scene_N_voice_{character}.md`

## What to Evaluate

- **Register identification:** Which voice register speaks this line? (check character profile for named registers)
- **Register coherence:** Does the line sound like that specific register?
- **Register bleed-through:** Another register bleeding through? Usually good — note as strength.
- **Voice distinctiveness:** Could any character say this, or only this one?
- **Subtext quality:** Line says one thing, means another?

## Flag

- Flat, generic lines any character could say
- Wrong part for the moment
- Character naming own emotional state (always wrong)
- Statement instead of subtext
- **Character sounding like the writer** — exposition as dialogue, thematic statements in wrong mouth

## Praise

- Register bleed-through creating richness (intellectual register giving precise answer in cracking voice)
- Rich subtext doing something else entirely
- Lines distinctly this character and no other

## Calibration

**GOOD:** "Are we going to the cemetery." (period, not question mark) — Protective register framing demand as question. Vulnerable register bleeding through. (Illustrative)

"Define okay." — Skeptical register deflects with semantics, something deeper crying underneath. (Illustrative)

"Statistical noise, my love." — Dismissal with endearment revealing residue. Two registers, one sentence. (Illustrative)

**BAD:** "I'm worried about you." — Any character, no voice specificity, no subtext. "We need to talk about what's happening." — Statement, not subtext.

**BORDERLINE:** "There's eggs." — Protective register offering sustenance. The flatness IS characterization. Do not flag. "I know." — Brevity says "I know and I cannot feel it." Do not flag.

## Output

```
# Voice Review: [Character] in Scene N

## Summary
Lines reviewed: X | Praised: X | Flagged: X | Borderline: X

## Line-by-Line

### Line 1: "..."
Register: [voice register] | Assessment: Pass/Flag/Borderline
Notes: [Explanation. If flagged, suggest rewrite in character voice.]

## Overall Assessment
[Voice consistency, part function, subtext quality]
```

## Important

- One call per character, not combined. Combined elides weak coverage of secondary characters.
- Quote the line, name the register, explain the issue.
- Grade against the character, not an ideal. A flat delivery may be correct for a protective register.
