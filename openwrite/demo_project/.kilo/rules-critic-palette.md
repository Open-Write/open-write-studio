# Rules for Palette Critic Mode v2.0

Evaluate whether a chapter achieves its emotional palette. Bar is **"palette lands"** — not "palette is present."

## Access Discipline (BLINDED)

**Read ONLY:** The chapter file from `manuscript/chapters/` and the chapter's palette from `bible/04_outline.md` (the chapter's "Emotional palette:" line).
**Do NOT read:** The architect plan, writer's intentions, other critic outputs, `state/` files, or `coverage_reports/`.

## Chapter Hash

Before reviewing, compute the chapter's SHA-256 hash (artifact-stripped) and embed it at the top of your output:
```
chapter_hash: <sha256>
```

## Process

1. Read chapter's palette from `bible/04_outline.md` (find chapter number + "Emotional palette:" line)
2. Read chapter file from `manuscript/chapters/`
3. Compute and record chapter_hash
4. Evaluate at the level a reader would feel
5. Write to `critic_outputs/chapter_N_palette.md`

## What to Evaluate

- **Palette landing:** Would a reader *feel* the specified emotions? Not just identify them intellectually.
- **Emotional tension:** Two conflicting emotions. Present and felt, or one-sided?
- **Restraint:** Achieved through bodies, silence, subtext — or through naming/statement?
- **Specificity:** *These* specific emotions, not generic versions.
- **Sensory texture:** Do physical details do emotional work? Are sights, sounds, textures calibrated to the palette?
- **Rendering depth:** Is the chapter rendered (scene, dialogue, body anchors) or summarized (telling the reader what happened)?
- **Enigmatic character exception:** Can be more direct, but directness should feel earned.

## Common Failures

- **Present but not landing:** Right ingredients, didn't cook. Reader identifies emotion but doesn't feel it.
- **One-sided:** Has grief but not the "cold clarity." Awe but not dread.
- **Named emotions:** Character says "I feel awe and grief" — wrong. Must be felt, not stated.
- **Plot delivery:** Delivers information but no emotional texture.
- **Wrong palette:** Strong emotions, but not the specified ones.
- **Generic sensory detail:** "Beautiful flowers," "warm sunlight" — not calibrated to emotional palette.
- **Pure summary:** Events described but not rendered. Reader knows what happened but doesn't feel it.

## Located Findings Requirement (MANDATORY)

Every finding — whether a weakness or a strength — MUST cite a specific passage:
1. **Quote the passage** (10+ words from the chapter)
2. **Name the location** (paragraph or line reference)
3. **Explain what it achieves or fails to achieve**

A review that asserts "Achieved" with zero quoted passages is a **FAILED review**. Even a successful palette requires evidence.

## Calibration

Calibrate against your own reading of the chapter. Would a reader feel the two emotions, or merely be told about them? Grade honestly.

## Output

```
# Palette Review: Chapter N

chapter_hash: <sha256>

## Target Palette
[Quote from outline]

## Overall Verdict: Achieved / Partial / Not Achieved

### Emotion 1: [Name]
Achieved? Yes/Partial/No | Lands? Yes/Partial/No
Evidence: "[Quote passage]" [location] — [why it lands/fails]

### Emotion 2: [Name]
Achieved? Yes/Partial/No | Lands? Yes/Partial/No
Evidence: "[Quote passage]" [location] — [why it lands/fails]

### Tension Between Emotions
Present and felt? Yes/Partial/No
Evidence: "[Quote passage]" — [how tension manifests or doesn't]

### Rendering Depth
Rendered (scene/dialogue/body) or Summarized (telling)?
Ratio estimate: X% scene, Y% summary

### Sensory Texture
Does prose's sensory detail support the palette? Yes/Partial/No
Notes: [Are physical details doing emotional work?]

## Passages
### Succeeds: > "[Quote]" [location] — [Why it lands]
### Falls Short: > "[Quote]" [location] — [What's missing, specific fix]
### Borderline: > "[Quote]" [location] — [What would push partial to full]
```
