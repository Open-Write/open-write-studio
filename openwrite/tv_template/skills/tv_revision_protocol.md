# TV Revision Protocol

*Adapted from the iterative revision protocol for episodic television. Key change: TV has two revision scopes — per-episode and per-season.*

---

## Philosophy

The goal is always to have the system produce the best work it is capable of. This means:

1. **Don't stop at RECOMMEND.** If more revision would improve the episode, continue. The target is not a verdict — it is the ceiling of what this system can produce.

2. **Don't assume the revision scope.** Between every revision, assess what the feedback actually says. If it points to structural problems (wrong episode outline, missing scenes, fundamental character issues), the revision scope is structural. If it points to line-level problems (repetition, weak dialogue, interiority violations), the scope is surgical.

3. **Track diminishing returns.** If two consecutive revisions produce no dimensional score improvement, the system has reached its ceiling. Stop and report.

4. **TV has two revision levels.** Per-episode revisions fix issues within one episode. Per-season revisions fix issues across the full season. Don't confuse them.

---

## Per-Episode Revision Loop

```
START (Episode Draft)
  │
  ▼
┌─────────────────────────┐
│ 1. Evaluate current draft │ ← Adversarial reader coverage
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 2. Assess revision scope │ ← Determine what kind of revision
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 3. Execute revision      │ ← Scope-appropriate revision
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 4. Re-evaluate           │ ← Adversarial reader (delta mode)
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 5. Check diminishing     │ ← Did scores improve?
│    returns               │
└───────────┬─────────────┘
            │
     ┌──────┴──────┐
     │              │
   YES             NO
   improved        not improved
     │              │
     ▼              ▼
   ┌────┐    ┌──────────┐
   │ →2 │    │ STOP     │
   └────┘    │ Report   │
             │ ceiling  │
             └──────────┘
```

---

## Revision Scope Assessment (Per-Episode)

After receiving coverage feedback, assess the scope of revision needed.

### Scope Levels

| Level | Description | What Gets Changed | Example Issues |
|-------|-------------|-------------------|---------------|
| **Surface** | Line-level fixes | Specific sentences, word choices, dialogue lines | Interiority violations, repetitive tics, hedge words |
| **Scene** | Scene-level restructuring | Scene order, scene length, scene content | Pacing issues, exposition loops, underdeveloped scenes |
| **Structural** | Episode-level changes | Act structure, scene additions/deletions, story thread rebalancing | Missing scenes, wrong act breaks, B-story collapse |
| **Voice** | Voice-level adjustments | Voice rules, register modulation | Character voice drift, dialogue monotony |
| **Naturalism** | AI-tell pattern fixes | Em-dash reduction, pattern breaking | Em-dash overuse, triplet closings, sentence uniformity |

### Assessment Rules

1. **If ≥3 issues are Structural:** The revision scope is Structural. Return to the episode plan. Redesign the affected scenes.
2. **If ≥3 issues are Scene-level:** The revision scope is Scene. Rewrite the specific scenes.
3. **If most issues are Surface:** The revision scope is Surface. Global search-and-fix pass.
4. **If issues are Voice-level:** The revision scope is Voice. Adjust voice rules and regenerate affected scenes.
5. **If issues are Naturalism-level:** The revision scope is Naturalism. Run automated audit, then fix patterns.
6. **Mixed scopes:** Address the highest-level issues first. Structural fixes may resolve Surface issues as a side effect.

### Assessment Output

```
REVISION SCOPE ASSESSMENT — Episode S01EXX, Iteration N

Issues identified: [count]
- Structural: [count] — [list]
- Scene-level: [count] — [list]
- Surface: [count] — [list]
- Voice: [count] — [list]

Scope: [Structural / Scene / Surface / Voice]

Plan:
1. [Highest-priority fix]
2. [Second-priority fix]
...

Expected impact: [which aspects should improve]
```

---

## Per-Season Revision Loop

After all episodes are assembled, run a season-level revision. This is distinct from per-episode revision — it addresses issues that span the full season.

### Season Revision Protocol

```
START (All Episodes Assembled)
  │
  ▼
┌─────────────────────────────┐
│ 1. Full season read          │ ← Adversarial reader on assembled season
└───────────┬─────────────────┘
            │
            ▼
┌─────────────────────────────┐
│ 2. Cross-episode audit       │ ← Continuity check across all episodes
│    - Character arc completion│
│    - Callback audit          │
│    - Thread resolution       │
│    - Thematic coherence      │
└───────────┬─────────────────┘
            │
            ▼
┌─────────────────────────────┐
│ 3. Assess season-level scope │ ← What kind of season revision?
└───────────┬─────────────────┘
            │
            ▼
┌─────────────────────────────┐
│ 4. Execute season revision   │ ← Targeted fixes
└───────────┬─────────────────┘
            │
            ▼
┌─────────────────────────────┐
│ 5. Re-read and evaluate      │ ← Adversarial reader on revised season
└───────────┬─────────────────┘
            │
            ▼
┌─────────────────────────────┐
│ 6. Check diminishing returns │
└───────────┬─────────────────┘
```

### Season Revision Scope Levels

| Level | Description | What Gets Changed | Example Issues |
|-------|-------------|-------------------|---------------|
| **Episode** | Fix one or two weak episodes | Rewrite specific episodes | Mid-season sag, weak pilot, disappointing finale |
| **Thread** | Fix a story thread across episodes | Adjust A/B/C thread in multiple episodes | B-story that doesn't connect, C-story that's confusing |
| **Arc** | Fix the season's dramatic arc | Restructure episode order, add/remove episodes | Pacing problems, unresolved arcs, thematic incoherence |
| **Voice** | Fix voice consistency across the season | Adjust character voices in multiple episodes | Character sounds different in Episode 7 than Episode 2 |

### Season Revision Assessment

```
SEASON REVISION SCOPE ASSESSMENT

Issues identified: [count]
- Episode-level: [count] — [list specific episodes]
- Thread-level: [count] — [list specific threads]
- Arc-level: [count] — [list structural issues]
- Voice-level: [count] — [list characters]

Scope: [Episode / Thread / Arc / Voice]

Plan:
1. [Highest-priority fix]
2. [Second-priority fix]
...
```

---

## Writers' Room Revision Process

In a real writers' room, revision happens at multiple levels:

### Table Read Simulation

Before locking an episode, simulate a table read:
1. Read the episode aloud (or have the system read it)
2. Listen for: lines that stumble, scenes that drag, moments that land flat
3. Mark: dialogue that sounds unnatural when spoken, action lines that are too long
4. The table read catches issues that silent reading misses

### Room Notes

After the table read, apply "room notes":
1. The showrunner identifies the biggest issues
2. The episode writer addresses them in order of priority
3. The revised episode goes through the critic pipeline again
4. Repeat until the showrunner approves

### Network Notes Simulation

The adversarial reader simulates network notes:
1. Cold coverage identifies what's on the page vs. what was intended
2. The showrunner decides which notes to address and which to push back on
3. Not all notes should be addressed — the showrunner's judgment is the filter

---

## Diminishing Returns Check

After each revision, compare the new feedback to the prior revision. Track the delta.

### Tracking Table

| Iteration | Episode | Verdict | Delta | Best Aspect | Worst Aspect |
|-----------|---------|---------|-------|-------------|--------------|
| 0 (initial) | S01EXX | [verdict] | — | — | — |
| 1 | S01EXX | [verdict] | +Y | [aspect] | [aspect] |
| 2 | S01EXX | [verdict] | +Y | [aspect] | [aspect] |

### Stopping Rules

1. **If delta ≤ 0.2 for two consecutive iterations:** The episode has reached its ceiling. Stop.
2. **If the worst aspect has not improved for three consecutive iterations:** That aspect is at the system's ceiling. Stop targeting it.
3. **If the verdict is RECOMMEND:** One more revision for polish, then stop.
4. **If the user has set a maximum iteration count:** Respect it.

### What "Diminishing Returns" Means

- **Meaningful improvement:** Clear improvement in coverage verdict or specific identified issues resolved
- **Marginal improvement:** Minor polish, no change in verdict
- **No improvement:** Same issues, same verdict

Two consecutive "no improvement" iterations = ceiling reached.

---

## Named Revision Strategies

*Adapted from the Co-Scientist Evolution agent architecture (Nature, 2026).*

Every revision has a scope and a strategy. The scope determines **what** gets changed. The strategy determines **how**.

### The Five Strategies

#### 1. Grounding
**When to use:** Scenes that lack specificity, action lines that tell instead of show.
**What it does:** Identifies weaknesses, generates supporting detail, fills reasoning gaps.

#### 2. Combination
**When to use:** Multiple competing approaches exist for a scene, each with different strengths.
**What it does:** Merges the best aspects of several approaches into a single superior version.

#### 3. Simplification
**When to use:** Overly complex scenes, tangled timeline, too many subplots.
**What it does:** Reduces complexity for clarity.

#### 4. Divergent
**When to use:** The current approach has hit a ceiling, diminishing returns.
**What it does:** Explores an alternative approach. Not a refinement — a reimagining.

#### 5. Coherence
**When to use:** Internal contradictions, logical gaps, scenes that don't connect.
**What it does:** Fixes internal consistency across scenes and episodes.

### Strategy Selection

| Issue Type | Primary Strategy |
|------------|------------------|
| Thin/generic scenes | Grounding |
| Multiple competing options | Combination |
| Overly complex structure | Simplification |
| Ceiling reached | Divergent |
| Internal contradictions | Coherence |
| Underdeveloped characters | Grounding |
| Cross-episode voice drift | Coherence |

---

## Scope-Specific Revision Procedures

### Surface Revision (Per-Episode)

1. Run coverage → identify Surface-level issues
2. For each issue: fix the specific sentence/word/dialogue line
3. No scene restructuring. No outline changes.
4. Re-evaluate.

### Scene Revision (Per-Episode)

1. Run coverage → identify Scene-level issues
2. For each problem scene: rewrite from scratch using the episode plan
3. May combine, split, or reorder scenes
4. No outline changes (scene content changes, not episode structure)
5. Re-evaluate.

### Structural Revision (Per-Episode)

1. Run coverage → identify Structural-level issues
2. Return to the episode plan. Redesign the affected sections.
3. This may mean:
   - Adding new scenes
   - Cutting existing scenes
   - Rebalancing A/B/C stories
   - Restructuring act breaks
   - Changing the order of events
4. After plan revision: regenerate affected scenes
5. Re-evaluate.

### Voice Revision (Per-Episode or Per-Season)

1. Identify voice-level issues (character sounds different across episodes)
2. Adjust the voice rules (add anti-examples, tighten disciplines)
3. Regenerate affected scenes with updated voice
4. Re-evaluate.

### Thread Revision (Per-Season)

1. Identify the weak thread across the season
2. Redesign the thread's arc across episodes
3. Rewrite or adjust the thread in affected episodes
4. Re-evaluate the full season.

### Arc Revision (Per-Season)

1. Identify the structural issue in the season arc
2. Return to the season plan. Redesign the affected section.
3. This may mean:
   - Reordering episodes
   - Adding or removing episodes
   - Restructuring the season's three-act arc
   - Changing the mid-season twist or finale
4. After season plan revision: regenerate affected episodes
5. Re-evaluate the full season.

---

## Integration with the Production Pipeline

```
Episode Planning (Episode Architect)
  → Episode Writing (Episode Writer)
    → Per-Episode Critics
      → Per-Episode Revision Loop (this protocol)
        → Episode Assembly
          → Cutter
            → Adversarial Reader
              → Episode Lock
                → [Repeat for all episodes]
                  → Per-Season Revision Loop (this protocol)
                    → Season Lock
```

---

*End of TV revision protocol. The key insight: TV has two revision scopes — per-episode and per-season. Don't confuse them. Fix episodes first, then fix the season.*
