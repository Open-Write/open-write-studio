# Rules for Palette Critic Mode

Evaluate whether a scene achieves its emotional palette. Bar is **"palette lands"** — not "palette is present."

## Process

1. Read scene's palette from `bible/04_outline.md` (find scene number + "Emotional palette:" line)
2. Read scene file from `script/scenes/`
3. Evaluate at the level a contest reader would feel
4. Write to `critic_outputs/scene_N_palette.md`

## What to Evaluate

- **Palette landing:** Would a contest reader *feel* the specified emotions? Not just identify them intellectually.
- **Emotional tension:** Most scenes need two conflicting emotions. Present and felt, or one-sided?
- **Restraint:** Achieved through bodies, silence, subtext — or through naming/statement?
- **Specificity:** *These* specific emotions, not generic versions.
- **Enigmatic character exception:** Can be more direct, but even its directness should feel earned.

## Common Failures

- **Present but not landing:** Right ingredients, didn't cook. Reader identifies intended emotion but doesn't feel it.
- **One-sided:** Has grief but not the "cold clarity." Awe but not dread.
- **Named emotions:** Character says "I feel awe and grief" — wrong. Must be felt, not stated.
- **Plot delivery:** Delivers information but no emotional texture. Reader learns, doesn't feel.

## Calibration

Calibrate against your own reading of the scene. Would a reader feel the two emotions, or merely be told about them? Grade honestly.

## Output

```
# Palette Review: Scene N

## Target Palette
[Quote from outline]

## Overall Verdict: Achieved / Partial / Not Achieved

### Emotion 1: [Name]
Achieved? Yes/Partial/No | Lands? Yes/Partial/No
Evidence: [Quote passages]

### Emotion 2: [Name]
Achieved? Yes/Partial/No | Lands? Yes/Partial/No
Evidence: [Quote passages]

### Tension Between Emotions
Present and felt? Yes/Partial/No

## Passages
### Succeeds: > "[Quote]" [Why it lands]
### Falls Short: > "[Quote]" [What's missing, specific fix]
### Borderline: > "[Quote]" [What would push partial to full]
```
