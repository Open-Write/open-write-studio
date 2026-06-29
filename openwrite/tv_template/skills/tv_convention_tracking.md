# TV Convention Tracking

*How to use the Convention Ledger to prevent writing drift across a TV season. Track ALL conventions — required AND prohibited — not just prohibited ones. Adapted from the screenplay/novel convention tracking system for episodic television.*

---

## Purpose

The Convention Ledger prevents overuse of permitted constructions across a TV season — the subtle repetition that makes scripts feel manufactured even when no individual sentence violates any rule. In TV, this risk is amplified: 10 episodes × 60 pages = 600+ pages of script. Patterns that are invisible in a single episode become glaring across a season.

**Key insight:** The most dangerous repetition is the repetition of permitted constructions. No rule says "don't use hands as a body anchor in every scene." But if every scene in every episode uses hands, the viewer notices, and the show feels engineered rather than written.

---

## Convention Ledger vs. Prohibited-Words List

| Aspect | Prohibited-Words List | Convention Ledger |
|--------|----------------------|-------------------|
| What it tracks | Words/phrases that must never appear | All writing patterns used, including permitted ones |
| What it prevents | Specific violations | Pattern-level repetition and drift |
| How it works | Binary: word is allowed or forbidden | Statistical: track frequency, distribution, and variety |
| Example | "No camera directions" | "Hands used as body anchor in 8 of last 10 scenes — switch to eyes or breath" |
| When consulted | Before writing (static) | Before each scene (dynamic, updated continuously) |

**Both are needed.** The prohibited-words list enforces hard rules. The Convention Ledger tracks soft patterns that require judgment.

---

## What Goes in the Convention Ledger

### Required Conventions (things that MUST appear)

- **Body anchors** — Physical grounding in every scene (hands, eyes, breath, spine, jaw, feet)
- **Sensory details** — At least 2 senses per scene (touch, sound, smell, taste, sight)
- **Subtext** — Characters never name their emotional states directly
- **Silence** — What characters DON'T say is as important as what they do
- **Cold open hook** — Every episode must open with something that demands attention
- **Act break cliffhanger** — Every act break must compel forward momentum
- **Final image** — Every episode must end with an image that lingers

### Prohibited Patterns (things that MUST NOT appear)

- **Camera directions** — "we see," "the camera," "close on"
- **Emotional parentheticals** — (angrily), (sadly), (quietly)
- **Interiority in action lines** — "Lena remembers," "Marcus thinks"
- **Voice register names in action lines** — "The Analyst takes over"
- **Adverbs in dialogue tags** — "she says quietly"
- **Invisible information** — durations, off-screen knowledge, historical interiority
- **"Previously on" dialogue** — characters restating prior episodes for the audience

### Tracked Patterns (things that are allowed but must be varied)

- **Body anchor distribution** — Which body part is used? How often? Is hands becoming a default?
- **Sensory detail distribution** — Which senses are invoked? Is sight dominating over touch and sound?
- **Sentence rhythm patterns** — Short-long-short, all short, periodic sentences. Is a rhythm becoming a default?
- **Dialogue attribution conventions** — said/asked/whispered ratios, attribution frequency, tag placement
- **Scene opening patterns** — How does each scene begin? Is there a default (action, dialogue, description)?
- **Scene closing patterns** — How does each scene end? Is there a default (image, silence, question)?
- **Emotional beat anchoring** — Where does the emotion live? Dialogue, action, silence, or description?

### TV-Specific Tracked Patterns

- **Cold open patterns** — How does each episode's cold open work? Is there a default (in medias res, dramatic irony, character revelation)?
- **Act break patterns** — What kind of cliffhanger is used? Is there a default (revelation, threat, emotional turn)?
- **Tag patterns** — How does each episode end? Is there a default (quiet moment, callback, twist)?
- **A/B/C story balance** — Is the A-story getting too much screen time? Is the B-story being neglected?
- **Case-of-the-week patterns** — If applicable, is the procedural engine becoming formulaic?
- **Character introduction patterns** — How are new characters introduced? Is there a default?
- **Location variety** — Are the same locations being used too often? Is the show visually monotonous?
- **Time-of-day patterns** — Is every scene at NIGHT? Is there enough variety in temporal setting?

---

## How to Use the Convention Ledger

### Before Each Scene

The episode writer consults the ledger before writing:

1. **Check body anchors** — What was used in the last 3 scenes? If hands appeared in all 3, use eyes or breath or spine.
2. **Check sensory details** — Which senses were invoked recently? If sight dominated, lead with sound or touch.
3. **Check sentence rhythm** — What's the dominant rhythm? If short declaratives dominated, try a periodic sentence.
4. **Check dialogue attribution** — Is "said" becoming invisible through overuse? Vary with action beats instead.

### Before Each Episode

The episode writer and episode architect consult the ledger for episode-level patterns:

1. **Check cold open patterns** — How have the last 3 episodes opened? Vary the approach.
2. **Check act break patterns** — What kind of cliffhangers have been used? Vary the type.
3. **Check tag patterns** — How have episodes ended? Vary the closing approach.
4. **Check A/B/C balance** — Is the B-story getting enough screen time this season?
5. **Check location variety** — Are we visiting new locations or revisiting the same ones?

### After Each Scene

Update the ledger with what was used:

1. **Record body anchors used** — which body parts, in what context
2. **Record sensory details** — which senses, how many per scene
3. **Record sentence rhythm** — dominant pattern, any notable variations
4. **Record dialogue attribution** — tags used, frequency, placement

### After Each Episode

Update the ledger with episode-level patterns:

1. **Record cold open approach** — what pattern was used
2. **Record act break cliffhangers** — what type was used at each break
3. **Record tag approach** — how the episode ended
4. **Record A/B/C screen time** — approximate page counts per thread
5. **Record locations used** — which locations appeared
6. **Record new characters introduced** — how they were introduced

### Periodic Review (Every 3 Episodes)

Scan the ledger for emerging patterns:

1. **Is any body anchor used in more than 60% of scenes?** If yes, it's becoming a default. Diversify.
2. **Is any sense used in more than 80% of scenes?** If yes, the scripts are sensorially narrow. Expand.
3. **Is any sentence rhythm used in more than 50% of scenes?** If yes, the scripts have a metronome. Break it.
4. **Is "said" used for more than 80% of dialogue tags?** This is actually fine — "said" is invisible. But if whispered/asked/muttered are climbing, they're becoming noticeable.
5. **Are cold opens becoming formulaic?** If the last 3 episodes opened the same way, change the approach.
6. **Are act breaks using the same cliffhanger type?** Vary the type across the season.
7. **Is the B-story getting enough screen time?** If it's been under 20% for 3 episodes, rebalance.
8. **Are we visiting new locations?** If the same 3 locations dominate, expand the show's visual world.

---

## Using convention_scan.py

The `tools/convention_scan.py` automates convention tracking:

```bash
set PYTHONIOENCODING=utf-8 && python tools\convention_scan.py
```

**What it scans:**
- Body anchor frequency (hands, eyes, breath, spine, jaw, feet, shoulders, knees)
- Sensory detail distribution (sight, sound, touch, smell, taste keywords)
- Sentence length distribution (short/medium/long ratios)
- Dialogue attribution patterns (said/asked/whispered/other ratios)
- Repetition flags (any pattern appearing in 3+ consecutive scenes)
- TV-specific: cold open patterns, act break patterns, tag patterns

**Output:** Updates `state/convention_ledger.json` with current statistics and flags.

**Usage in workflow:** Run `convention_scan.py` before each episode writer session. The writer reads the ledger output and adjusts accordingly.

---

## Convention Ledger Structure

The ledger is a JSON file tracking:

```json
{
  "body_anchors": {
    "hands": {"count": 12, "scenes": ["S01E01_03", "S01E01_07", "S01E02_02", "S01E02_05"]},
    "eyes": {"count": 8, "scenes": ["S01E01_05", "S01E02_01", "S01E02_08"]},
    "breath": {"count": 5, "scenes": ["S01E01_02", "S01E02_04"]}
  },
  "sensory_distribution": {
    "sight": {"count": 45, "percentage": 42},
    "sound": {"count": 28, "percentage": 26},
    "touch": {"count": 22, "percentage": 21},
    "smell": {"count": 8, "percentage": 7},
    "taste": {"count": 4, "percentage": 4}
  },
  "sentence_rhythm": {
    "short_declarative": {"count": 120, "percentage": 55},
    "periodic": {"count": 45, "percentage": 21},
    "compound": {"count": 52, "percentage": 24}
  },
  "dialogue_attribution": {
    "said": {"count": 89, "percentage": 78},
    "asked": {"count": 12, "percentage": 11},
    "action_beat": {"count": 13, "percentage": 11}
  },
  "tv_patterns": {
    "cold_open_types": {
      "in_medias_res": {"count": 2, "episodes": ["S01E01", "S01E03"]},
      "dramatic_irony": {"count": 1, "episodes": ["S01E02"]},
      "character_revelation": {"count": 1, "episodes": ["S01E04"]}
    },
    "act_break_types": {
      "revelation": {"count": 3, "episodes": ["S01E01", "S01E02", "S01E04"]},
      "threat": {"count": 2, "episodes": ["S01E01", "S01E03"]},
      "emotional_turn": {"count": 1, "episodes": ["S01E03"]}
    },
    "tag_types": {
      "quiet_moment": {"count": 2, "episodes": ["S01E01", "S01E03"]},
      "callback": {"count": 1, "episodes": ["S01E02"]},
      "twist": {"count": 1, "episodes": ["S01E04"]}
    },
    "a_story_percentage": {"average": 62, "range": [55, 70]},
    "b_story_percentage": {"average": 25, "range": [18, 32]},
    "c_story_percentage": {"average": 13, "range": [5, 20]}
  },
  "flags": [
    "hands used in 12 of 20 scenes (60%) — at threshold",
    "sight dominates sensory distribution (42%) — consider more sound/touch",
    "revelation used for 3 of 8 act breaks (37%) — vary the cliffhanger type",
    "B-story below 20% in S01E03 — rebalance in S01E04"
  ]
}
```

---

## Per-Episode and Per-Season Tracking

### Per-Episode Tracking

After each episode, the convention ledger records:
- Body anchors used in this episode
- Sensory distribution for this episode
- Sentence rhythm for this episode
- Dialogue attribution for this episode
- Cold open, act break, and tag patterns for this episode
- A/B/C story balance for this episode

### Per-Season Tracking

The convention ledger accumulates across the season:
- Running totals for all patterns
- Episode-by-episode comparison
- Trend detection (is a pattern becoming a default?)
- Threshold alerts (has a pattern crossed the 60% or 80% threshold?)

### Cross-Episode Convention Consistency

The convention ledger also checks for consistency:
- Is the show's tonal register consistent across episodes?
- Are the dialogue conventions consistent (formal vs. informal, naturalistic vs. heightened)?
- Are the action line conventions consistent (sparse vs. detailed)?
- If different "writers" are simulated, do their conventions align?

---

## Maintaining the Ledger Across a Season

1. **Create the ledger at season start** — empty statistics, no flags
2. **Update after every scene** — record what was used
3. **Consult before every scene** — check for emerging patterns
4. **Review every 3 episodes** — scan for threshold violations
5. **Archive at season end** — the ledger is a record of the season's writing patterns

The ledger is a living document. It changes as the season evolves. Early episodes may establish patterns that later episodes diversify. The ledger tracks this evolution.

---

## Key Lessons

1. **The most dangerous repetition is permitted repetition.** No rule says "don't use hands in every scene." But if you do, the viewer notices.
2. **The ledger prevents drift, not error.** A prohibited-words list prevents errors. A convention ledger prevents the subtle drift that makes scripts feel manufactured.
3. **Consult, don't obey.** The ledger informs the writer's judgment. It doesn't make decisions. If a scene needs hands, use hands — but know that you're using hands again.
4. **TV amplifies the risk.** 600+ pages across a season means patterns accumulate faster. Run the convention scan more frequently.
5. **The scan tool is essential.** Manual tracking is unreliable. The `convention_scan.py` tool catches patterns that the writer is too close to see.
6. **Track TV-specific patterns.** Cold opens, act breaks, tags, A/B/C balance — these are the structural conventions that make a show feel formulaic if not varied.
