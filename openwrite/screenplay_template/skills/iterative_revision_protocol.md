# Iterative Revision Protocol — Version 2

*Updated: May 6, 2026*
*Key change: Revisions continue until diminishing returns, not just until a target verdict is reached.*

---

## Philosophy

The goal of autonomous mode is always to have the LLM produce the best work it is capable of on its own. This means:

1. **Don't stop at RECOMMEND.** If more revision would improve the work, continue. The target is not a verdict — it is the ceiling of what this system can produce.

2. **Don't assume the revision scope.** Between every revision, assess what the feedback actually says. If it points to structural problems (wrong outline, missing scenes, fundamental character issues), the revision scope is structural — go back to the outline. If it points to line-level problems (repetition, weak dialogue, interiority violations), the scope is surgical. Match the tool to the problem.

3. **Track diminishing returns.** If two consecutive revisions produce no dimensional score improvement, the system has reached its ceiling. Stop and report.

---

## Revision Loop

```
START
  │
  ▼
┌─────────────────────────┐
│ 1. Evaluate current draft │ ← Quantitative coverage
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 2. Assess revision scope │ ← NEW: Determine what kind of revision
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 3. Execute revision      │ ← Scope-appropriate revision
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 4. Re-evaluate           │ ← Quantitative coverage (delta mode)
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

## Step 2: Revision Scope Assessment

After receiving quantitative coverage, assess the scope of revision needed. This is a triage decision — the system examines the Fix Priority Matrix and categorizes each issue by scope.

### Scope Levels

| Level | Description | What Gets Changed | Example Issues |
|-------|-------------|-------------------|---------------|
| **Surface** | Line-level fixes | Specific sentences, word choices, dialogue lines | Interiority violations, repetitive tics, hedge words, over-constructed sentences |
| **Scene** | Scene-level restructuring | Scene order, scene length, scene content | Pacing issues, exposition loops, underdeveloped scenes, missing beats |
| **Structural** | Outline-level changes | Chapter/act structure, scene additions/deletions, character arc redesign | Wrong protagonist arc, missing plot beats, structural redundancy, fundamental pacing problems |
| **Voice** | Voice-level adjustments | Voice rules, register modulation, convention patterns | Voice monotony, register mismatch, convention overuse |

### Assessment Rules

1. **If ≥3 issues are Structural:** The revision scope is Structural. Return to the outline. Redesign the scenes/chapters that the feedback identifies. This may mean adding scenes, cutting scenes, or rewriting scenes from scratch.

2. **If ≥3 issues are Scene-level:** The revision scope is Scene. Rewrite the specific scenes identified. May involve scene-level restructuring (combining scenes, splitting scenes, reordering).

3. **If most issues are Surface:** The revision scope is Surface. Global search-and-fix pass. No structural changes.

4. **If issues are Voice-level:** The revision scope is Voice. Adjust the voice rules and regenerate affected scenes.

5. **Mixed scopes:** Address the highest-level issues first. If there are both Structural and Surface issues, fix the Structural ones first — they may resolve some Surface issues as a side effect.

### Assessment Output

Before each revision, produce a brief assessment:

```
REVISION SCOPE ASSESSMENT — Iteration N

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

Expected impact: [which dimensional scores should improve]
```

---

## Named Revision Strategies

*Adapted from the Co-Scientist Evolution agent architecture (Nature, 2026). Each revision should select one or more named strategies based on the scope assessment.*

Every revision has a scope (Surface / Scene / Structural / Voice) and a strategy. The scope determines **what** gets changed. The strategy determines **how** it gets changed.

### The Five Strategies

#### 1. Grounding

**When to use:** Scenes that lack specificity, action lines that tell instead of show, narrative gaps that need filling.

**What it does:** Identifies weaknesses in the current draft, generates supporting detail, fills reasoning gaps, strengthens underdeveloped scenes with concrete work.

**Procedure:**
1. Identify passages that are thin, generic, or unsupported
2. For each: what specific visual detail, action, or dialogue would ground this?
3. Rewrite with concrete detail — not more words, but more specific words
4. Verify: does the grounded version render the scene rather than summarize it?

**Example:** "The market was busy" → render three specific vendors, the smell of fish, a child running between legs. Show through action and dialogue, not description.

#### 2. Combination

**When to use:** Multiple competing approaches exist for a scene, each with different strengths.

**What it does:** Merges the best aspects of several approaches into a single superior version. Does not pick a winner — creates something new from the strongest elements.

**Procedure:**
1. Identify the competing approaches (drafts, structural options, scene variations)
2. For each: what is its strongest element?
3. Combine those elements into a new version
4. Verify: does the combination feel coherent, not stitched together?

**Example:** Draft A has the strongest opening. Draft B has the best dialogue. Draft C has the best ending. Combination: A's opening + B's dialogue + C's ending, with new connective tissue.

#### 3. Simplification

**When to use:** Overly complex scenes, tangled timeline, too many subplots, confusing narrative structure.

**What it does:** Reduces complexity for clarity. Removes unnecessary threads, streamlines scenes, clarifies confusing passages. Not cutting for length — simplifying for comprehension.

**Procedure:**
1. Identify the complexity: what is confusing or tangled?
2. For each: what is the essential narrative thread?
3. Remove or consolidate non-essential elements
4. Verify: is the simplified version clearer without losing depth?

**Example:** A scene with 4 characters and 3 subplots → consolidate to 2 characters and 1 subplot that carries the same thematic weight.

#### 4. Divergent

**When to use:** The current approach has hit a ceiling, the revision loop is producing diminishing returns, or the feedback points to a fundamental problem that incremental fixes won't solve.

**What it does:** Explores an alternative approach. Moves away from the current draft entirely and generates a different version. Not a refinement — a reimagining.

**Procedure:**
1. Identify what the current approach is trying to achieve
2. Generate 2-3 fundamentally different approaches to the same goal
3. Evaluate each against the feedback criteria
4. If one is clearly better, adopt it. If none are, keep the original.

**Example:** A flashback scene that isn't working → try rendering the same information as a present-tense discovery, or as dialogue, or as a physical object that carries the history.

#### 5. Coherence

**When to use:** Internal contradictions, logical gaps, scenes that don't connect, character behavior that doesn't track.

**What it does:** Fixes internal consistency. Resolves contradictions between scenes, ensures character behavior tracks across the script, improves narrative flow. The "plumbing" revision — invisible when done right.

**Procedure:**
1. Identify the contradiction or gap
2. Trace it to its source (which scene introduced it?)
3. Fix at the source, not at the symptom
4. Verify: does the fix create new contradictions downstream?

**Example:** Character A is afraid of water in Scene 3 but swims in Scene 27 → fix: either remove the fear in Scene 3 or add a justification arc in between.

### Strategy Selection

After the scope assessment, select strategies based on the issues identified:

| Issue Type | Primary Strategy | Secondary Strategy |
|------------|------------------|-------------------|
| Thin/generic scenes | Grounding | — |
| Multiple competing options | Combination | — |
| Overly complex structure | Simplification | Coherence |
| Ceiling reached, need breakthrough | Divergent | — |
| Internal contradictions | Coherence | — |
| Underdeveloped characters | Grounding | Combination |
| Repetitive patterns | Simplification | Divergent |
| Missing narrative threads | Grounding | Coherence |

For mixed-scope revisions, select one strategy per scope level. Execute highest-level strategies first.

### Integration with Revision Scope Assessment

Add the strategy selection to the assessment output:

```
REVISION SCOPE ASSESSMENT — Iteration N

Issues identified: [count]
- Structural: [count] — [list]
- Scene-level: [count] — [list]
- Surface: [count] — [list]
- Voice: [count] — [list]

Scope: [Structural / Scene / Surface / Voice]

Strategies:
1. [Strategy name] — [applied to which issues]
2. [Strategy name] — [applied to which issues]

Plan:
1. [Highest-priority fix using selected strategy]
2. [Second-priority fix using selected strategy]
...

Expected impact: [which dimensional scores should improve]
```

---

## Step 5: Diminishing Returns Check

After each revision, compare the new dimensional scores to the prior revision. Track the delta.

### Tracking Table

| Iteration | Composite Score | Delta | Best Dimension | Worst Dimension | Verdict |
|-----------|----------------|-------|----------------|-----------------|---------|
| 0 (initial) | X.X | — | — | — | [verdict] |
| 1 | X.X | +Y.Y | [dim] | [dim] | [verdict] |
| 2 | X.X | +Y.Y | [dim] | [dim] | [verdict] |
| ... | ... | ... | ... | ... | ... |

### Stopping Rules

1. **If delta ≤ 0.2 for two consecutive iterations:** The system has reached its ceiling. Stop.
2. **If the worst dimension has not improved for three consecutive iterations:** That dimension is at the system's ceiling. Stop targeting it.
3. **If the composite score exceeds 8.5:** The system has produced work at the top of its capability. One more revision for polish, then stop.
4. **If the user has set a maximum iteration count:** Respect it.

### What "Diminishing Returns" Means

A 0.3-point improvement on a 10-point scale is significant. A 0.1-point improvement is noise. The system should distinguish between:
- **Meaningful improvement:** Delta ≥ 0.3 on composite, or ≥ 1.0 on any single dimension
- **Marginal improvement:** Delta 0.1-0.3 on composite
- **No improvement:** Delta ≤ 0.1 on composite

Two consecutive "no improvement" iterations = ceiling reached.

---

## Scope-Specific Revision Procedures

### Surface Revision

1. Run quantitative coverage → identify Surface-level issues
2. For each issue: fix the specific sentence/word/dialogue line
3. No scene restructuring. No outline changes.
4. Re-evaluate.

### Scene Revision

1. Run quantitative coverage → identify Scene-level issues
2. For each problem scene: rewrite from scratch using the architect plan
3. May combine, split, or reorder scenes
4. No outline changes (scene content changes, not scene structure)
5. Re-evaluate.

### Structural Revision

1. Run quantitative coverage → identify Structural-level issues
2. Return to the outline. Redesign the affected sections.
3. This may mean:
   - Adding new scenes
   - Cutting existing scenes
   - Rewriting character arcs
   - Restructuring act breaks
   - Changing the order of events
4. After outline revision: regenerate affected scenes
5. Re-evaluate.

### Voice Revision

1. Run quantitative coverage → identify Voice-level issues
2. Adjust the voice rules (add anti-examples, add pro-examples, tighten disciplines)
3. Regenerate affected scenes with updated voice
4. Re-evaluate.

---

## Integration with Quantitative Coverage

The revision scope assessment uses the Fix Priority Matrix from the quantitative coverage report. The matrix already categorizes issues by impact and effort. The scope assessment adds a level categorization:

- **Surface issues:** Effort = Low, Impact = Low-Medium
- **Scene issues:** Effort = Medium, Impact = Medium-High
- **Structural issues:** Effort = High, Impact = High
- **Voice issues:** Effort = Medium, Impact = Medium-High

The priority score (Impact ÷ Effort) still determines the order of fixes within each scope level.

---

## Example: How the Loop Works in Practice

### Iteration 1
- Coverage: Composite 6.8, Verdict CONSIDER
- Issues: Alex monologue repetition (Scene), Mira passivity (Structural), interiority violations (Surface)
- Scope: Structural (1 Structural issue + mixed)
- Plan: Add Mira active choice scene, rewrite Alex monologues, fix interiority violations
- Result: Composite 7.4, Delta +0.6 → Continue

### Iteration 2
- Coverage: Composite 7.4, Verdict ENGAGED
- Issues: Pacing in middle act (Scene), Okafor underwritten (Scene), some remaining tics (Surface)
- Scope: Scene
- Plan: Rewrite middle act pacing, add Okafor interiority scene, fix tics
- Result: Composite 7.8, Delta +0.4 → Continue

### Iteration 3
- Coverage: Composite 7.8, Verdict ENGAGED
- Issues: Repetitive sentence rhythm (Surface), geopolitical subplot thin (Scene)
- Scope: Surface + Scene
- Plan: Sentence rhythm variation pass, add one geopolitical scene
- Result: Composite 8.0, Delta +0.2 → Continue (marginal but still improving)

### Iteration 4
- Coverage: Composite 8.0, Verdict RECOMMEND
- Issues: Minor tics (Surface), one interiority violation (Surface)
- Scope: Surface
- Plan: Fix remaining tics and violations
- Result: Composite 8.1, Delta +0.1 → Marginal

### Iteration 5
- Coverage: Composite 8.1, Verdict RECOMMEND
- Issues: Same minor issues, no new improvement
- Scope: Surface
- Plan: Fix remaining issues
- Result: Composite 8.1, Delta 0.0 → **CEILING REACHED. STOP.**

---

*End of protocol v2.*
