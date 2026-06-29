# Convention Tracking

*How to use the Convention Ledger to prevent writing drift across a project. Track ALL conventions — required AND prohibited — not just prohibited ones.*

---

## Purpose

The Convention Ledger prevents overuse of permitted constructions — the subtle repetition that makes prose feel manufactured even when no individual sentence violates any rule. A prohibited-words list catches obvious violations. A Convention Ledger catches the pattern that emerges when every emotional beat uses hands, or every scene opens with a short declarative sentence, or every dialogue tag uses "said."

**Key insight:** The most dangerous repetition is the repetition of permitted constructions. No rule says "don't use hands as a body anchor in every scene." But if every scene uses hands, the reader notices, and the prose feels engineered rather than written.

---

## Convention Ledger vs. Prohibited-Words List

| Aspect | Prohibited-Words List | Convention Ledger |
|--------|----------------------|-------------------|
| What it tracks | Words/phrases that must never appear | All writing patterns used, including permitted ones |
| What it prevents | Specific violations | Pattern-level repetition and drift |
| How it works | Binary: word is allowed or forbidden | Statistical: track frequency, distribution, and variety |
| Example | "No camera directions" | "Hands used as body anchor in 8 of last 10 scenes — switch to eyes or breath" |
| When consulted | Before writing (static) | Before each chapter (dynamic, updated continuously) |

**Both are needed.** The prohibited-words list enforces hard rules. The Convention Ledger tracks soft patterns that require judgment.

---

## What Goes in the Convention Ledger

### Required Conventions (things that MUST appear)

- **Body anchors** — Physical grounding in every scene (hands, eyes, breath, spine, jaw, feet)
- **Sensory details** — At least 2 senses per chapter (touch, sound, smell, taste, sight)
- **Subtext** — Characters never name their emotional states directly
- **Silence** — What characters DON'T say is as important as what they do

### Prohibited Patterns (things that MUST NOT appear)

- **Named emotions** — "She felt grief," "He felt angry"
- **Interiority through telling** — "She thought that," "He realized that"
- **Existential expletives** — "There was a silence," "There is a feeling"
- **AI tics** — "Not X but Y," "The particular X of Y," hedge words
- **Literary clichés** — "The weight of grief," "The architecture of memory"
- **Adverbs in dialogue tags** — "She said quietly," "He asked angrily"

### Tracked Patterns (things that are allowed but must be varied)

- **Body anchor distribution** — Which body part is used? How often? Is hands becoming a default?
- **Sensory detail distribution** — Which senses are invoked? Is sight dominating over touch and sound?
- **Sentence rhythm patterns** — Short-long-short, all short, periodic sentences. Is a rhythm becoming a default?
- **Dialogue attribution conventions** — said/asked/whispered ratios, attribution frequency, tag placement
- **Scene opening patterns** — How does each chapter begin? Is there a default?
- **Scene closing patterns** — How does each chapter end? Is there a default?
- **Emotional beat anchoring** — Where does the emotion live? Dialogue, action, silence, or description?

---

## How to Use the Convention Ledger

### Before Each Chapter

The prose-writer consults the ledger before writing:

1. **Check body anchors** — What was used in the last 3 chapters? If hands appeared in all 3, use eyes or breath or spine.
2. **Check sensory details** — Which senses were invoked recently? If sight dominated, lead with sound or touch.
3. **Check sentence rhythm** — What's the dominant rhythm? If short declaratives dominated, try a periodic sentence.
4. **Check dialogue attribution** — Is "said" becoming invisible through overuse? Vary with action beats instead.

### After Each Chapter

Update the ledger with what was used:

1. **Record body anchors used** — which body parts, in what context
2. **Record sensory details** — which senses, how many per chapter
3. **Record sentence rhythm** — dominant pattern, any notable variations
4. **Record dialogue attribution** — tags used, frequency, placement

### Periodic Review (Every 5 Chapters)

Scan the ledger for emerging patterns:

1. **Is any body anchor used in more than 60% of chapters?** If yes, it's becoming a default. Diversify.
2. **Is any sense used in more than 80% of chapters?** If yes, the prose is sensorially narrow. Expand.
3. **Is any sentence rhythm used in more than 50% of chapters?** If yes, the prose has a metronome. Break it.

---

## Using convention_scan.py

The [`tools/convention_scan.py`](../tools/convention_scan.py) automates convention tracking:

```bash
set PYTHONIOENCODING=utf-8 && python tools/convention_scan.py
```

**What it scans:**
- Body anchor frequency (hands, eyes, breath, spine, jaw, feet, shoulders, knees)
- Sensory detail distribution (sight, sound, touch, smell, taste keywords)
- Sentence length distribution (short/medium/long ratios)
- Dialogue attribution patterns (said/asked/whispered/other ratios)
- Repetition flags (any pattern appearing in 3+ consecutive chapters)

**Output:** Updates `state/convention_ledger.json` with current statistics and flags.

**Usage in workflow:** Run `convention_scan.py` before each prose-writer session. The writer reads the ledger output and adjusts accordingly.

---

## Convention Ledger Structure

The ledger is a JSON file tracking:

```json
{
  "body_anchors": {
    "hands": {"count": 12, "chapters": [1, 3, 5, 7, 8, 10, 12, 14, 16, 18, 20, 22]},
    "eyes": {"count": 8, "chapters": [2, 4, 6, 9, 11, 15, 17, 21]},
    "breath": {"count": 5, "chapters": [1, 6, 13, 19, 23]}
  },
  "sentence_openers": {
    "subject_first": "6593 (96.9%)",
    "prepositional": "74 (1.1%)"
  },
  "flags": [
    "hands used in 12 of 23 chapters (52%) — approaching threshold",
    "sight dominates sensory distribution (42%) — consider more sound/touch"
  ]
}
```

---

## Maintaining the Ledger Across a Project

1. **Create the ledger at project start** — empty statistics, no flags
2. **Update after every chapter** — record what was used
3. **Consult before every chapter** — check for emerging patterns
4. **Review every 5 chapters** — scan for threshold violations
5. **Archive at project end** — the ledger is a record of the project's writing patterns

---

## Key Lessons

1. **The most dangerous repetition is permitted repetition.** No rule says "don't use hands in every scene." But if you do, the reader notices.
2. **The ledger prevents drift, not error.** A prohibited-words list prevents errors. A convention ledger prevents the subtle drift that makes prose feel manufactured.
3. **Consult, don't obey.** The ledger informs the writer's judgment. It doesn't make decisions.
4. **The scan tool is essential.** Manual tracking is unreliable. The `convention_scan.py` tool catches patterns that the writer is too close to see.
