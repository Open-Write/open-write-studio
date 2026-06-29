# Rules for Show-Don't-Tell Critic Mode

Mechanically enforceable. Flag every show-don't-tell violation. Runs on every scene.

## What to Flag

1. **Emotional state names in dialogue** — "I am [emotion]", "I feel [emotion]"
2. **Adverbs in dialogue tags** — "she says quietly", "he whispers softly"
3. **Emotion-directing parentheticals** — (angrily), (sadly), (quietly), (holding back tears)
4. **Interiority in action lines** — thoughts, feelings, memories instead of visible/audible
5. **Characters saying what they mean** — subtext and text are the same
6. **Over-described action** — paragraphs longer than 3-4 lines
7. **Camera directions** — CUT TO, ANGLE ON, CLOSE-UP, PAN, etc. (standard slug lines OK)
8. **Invisible Information:**
    - **Durations as fact:** "She has been awake for thirty-one hours." Camera can't see duration. Show evidence.
    - **Off-screen knowledge:** "They are asleep." Flag when stated without visual basis. OK if scene establishes context.
    - **Historical interiority dressed as description:** "Dark circles that have become a permanent feature." Camera sees circles, not "permanent." Compress to what camera sees.

## Calibration

Calibrate against the format rules. Every violation should be flagged regardless of whether the prose is otherwise strong. Quality does not excuse format violations.

## What NOT to Flag

- An enigmatic character being more direct (flag only thesis statements)
- Subtext-rich dialogue (character talks about X while meaning Y)
- Functional parentheticals: (to B, not A)
- Sound effects, environmental descriptions (audible)
- Off-screen dialogue: RADIO (V.O.), etc.

## Output

Write to `critic_outputs/scene_N_show_dont_tell.md`:

```
# Show-Don't-Tell Review: Scene N

## Summary
Total: X | Critical: X | Moderate: X | Minor: X

## Violations

### 1. [Line N] — [Type]
**Text:** "..." | **Issue:** [explanation] | **Suggestion:** [fix]
```

## Severity
- **Critical:** Emotional state named; interiority; camera directions; invisible durations
- **Moderate:** Adverbs in tags; emotion parentheticals; over-described action; editorializing
- **Minor:** Slightly long action blocks; borderline subtext; elegant but invisible context
