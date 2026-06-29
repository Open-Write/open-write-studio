# Screenplay Adaptation Template

> **Purpose:** Adapt a novel (or other source material) into a screenplay using the 3-phase adaptation protocol.

---

## Overview

This template provides everything needed to adapt a novel into a screenplay. The adaptation protocol ([`skills/adaptation_protocol.md`](../../skills/adaptation_protocol.md)) guides the process through three phases:

1. **Story Outline** — Extract narrative DNA from the novel, design screenplay outlines
2. **Author Voice** — Design and test screenplay voice candidates
3. **Drafting** — Write the screenplay scene by scene with iterative review

---

## Getting Started

### 1. Upload Source Material

Place your source novel in the project root:

```
your_project/
├── source/
│   └── your_novel.md                   ← Source novel here (or .txt, .doc)
├── bible/
├── script/
├── voice_experiment/
└── ...
```

The system reads markdown, plain text, or Word document formats.

### 2. Configure Adaptation Variables

Create or edit your adaptation configuration. You can place this in a `adaptation_config.md` file at the project root or provide it directly:

```yaml
# Adaptation Configuration
source: ./source/your_novel.md
target_type: screenplay
autonomous: false              # true = run without pausing; false = pause at each phase
outline_count: 2               # Number of outline options to generate
voice_count: 5                 # Number of voice candidates to test
voice_runs: 3                  # Runs per voice candidate
max_iterations: 5              # Max revision iterations per act
target_verdict: "Recommend"    # "Recommend" or "Acquisition Recommendation"
line_count_min: 90             # Minimum page count
line_count_max: 120            # Maximum page count
dual_track: false              # true if adaptation has alien/non-human POV tracks
```

### 3. Start the Adaptation

Tell the system:

> "Adapt this novel into a screenplay."

The system will begin Phase 1, reading the novel and extracting its narrative DNA.

---

## Phase-by-Phase Walkthrough

### Phase 1: Story Outline

**What happens:**
1. System reads your novel completely
2. Extracts narrative DNA: plot structure, character arcs, themes, emotional beats, world-building, callbacks
3. Generates `outline_count` screenplay outline options
4. Runs editorial review (Lara Marsh, Dr. Elena Vasquez, Marcus Webb) on each outline
5. Selects the best outline based on editorial consensus

**Your novel's prose becomes screen storytelling:**
- Interiority (character thoughts) → subtext, behavioral indication, or voice-over
- Rich description → concise action lines, visual storytelling
- Narrative summary → montages, time cuts, or omitted
- Exposition → revealed through dialogue, action, or visual cues
- Multiple POV → consolidated or restructured for screen

**What must be cut (the hard truth of novel → script):**
- Subplots that don't serve the central dramatic question
- Backstory that can be implied rather than stated
- Descriptive passages that a director/production designer will interpret
- Interior monologue that can be externalized

**Pause point (if `autonomous: false`):**
- Review the outlines and editorial feedback
- Select your preferred outline (or request revisions)
- Adjust any configuration variables
- Approve to continue

**Outputs:** Selected outline in [`bible/04_outline.md`](../bible/04_outline.md), updated bible files, narrative DNA document.

### Phase 2: Author Voice

**What happens:**
1. System analyzes your novel's voice (sentence rhythm, detail density, emotional register, POV, tense)
2. Designs `voice_count` screenplay voice candidates calibrated to the source
3. Runs the voice experiment: Round 1 (all voices) → Round 2 (top 2) → Round 3 (winner)
4. Lara Marsh evaluates each round
5. Locks the winning voice

**What "calibrated to the source" means:**
- If your novel has lyrical, literary prose, the screenplay voice won't become terse action lines
- If your novel has spare, minimalist prose, the screenplay voice will match that economy
- The voice adapts the source's sensibility for the screen medium

**Screenplay-specific voice dimensions:**
- Action line density (sparse vs. descriptive)
- Dialogue style (naturalistic vs. stylized)
- Parenthetical usage (minimal vs. expressive)
- Slug line convention (standard vs. creative)
- Transition style (CUT TO: vs. none)

**Pause point (if `autonomous: false`):**
- Review voice candidates and experiment results
- Adjust voice direction if needed
- Approve the locked voice

**Outputs:** Locked voice specification in [`voice_experiment/LOCKED_VOICE_SPEC.md`](../voice_experiment/LOCKED_VOICE_SPEC.md).

### Phase 3: Drafting

**What happens:**
1. System generates the screenplay scene by scene using the locked voice and selected outline
2. After each act: Lara Marsh cold evaluation
3. If not RECOMMEND: identifies issues, revises, re-evaluates
4. Continues until RECOMMEND or ceiling reached
5. Assembles the complete screenplay

**The iterative cycle:**
```
Generate → Evaluate → Identify Issues → Revise → Re-evaluate → [repeat until RECOMMEND]
```

**Screenplay-specific quality gates:**
- Page count within target range (`line_count_min` / `line_count_max`)
- Proper Fountain formatting
- Scene count appropriate for genre
- Dialogue-to-action ratio balanced
- No unfilmables in action lines (see [`screenplay_craft.md`](../../skills/screenplay_craft.md))

**Pause point (if `autonomous: false`):**
- Review each evaluation report
- Adjust revision direction
- Let the system continue or accept the current state

**Outputs:** Complete screenplay in Fountain format, coverage reports, final verdict.

---

## Running in Autonomous Mode

Set `autonomous: true` to run the entire pipeline without pausing:

```yaml
autonomous: true
```

The system will:
1. Generate outlines → pick the best one automatically
2. Run voice experiment → lock the winner automatically
3. Draft the screenplay → iterate until RECOMMEND or ceiling → report final status

**When to use autonomous mode:**
- You trust the system's editorial judgment
- You want to see a complete draft before making changes
- You're running overnight or in the background

**When to use interactive mode (default):**
- This is a high-stakes adaptation
- You want creative control at each phase boundary
- You want to adjust voice direction based on experiment results
- You want to steer the revision process

---

## Example: Novel-to-Screenplay Adaptation

The following example demonstrates the voice experiment and editorial review protocols used in production. Key outcomes:

| Protocol Element | Result |
|-----------------|--------|
| Voice experiment | 5 voice candidates tested over 3 rounds. Winner locked with specific rules for action lines, dialogue, and parentheticals. |
| Dual-track voice | Human + alien voice tracks calibrated separately, then tested for cross-track consistency. |
| Editorial review | Lara Marsh evaluated each draft, producing coverage reports that drove revision. |
| Iterative revision | Multiple revision passes until RECOMMEND verdict reached. |

**Lessons learned for novel → script adaptation:**
- The hardest part is cutting — novels have 3–5x more content than screenplays can hold
- Interiority must be externalized through behavior, dialogue, or visual metaphor
- The voice experiment is critical for finding the right screenplay register
- Callback tracking prevents plant/payoff losses during compression

---

## Project Structure

After adaptation, your project will have this structure:

```
your_project/
├── source/
│   └── your_novel.md                     # Source material
├── bible/
│   ├── 00_narrative_dna.md               # Extracted from source
│   ├── 01_concept.md                     # Generated in Phase 1
│   ├── 02_mythology.md
│   ├── 04_outline.md                     # Selected outline
│   ├── 05_ending_notes.md
│   ├── 06_craft_feeling.md
│   ├── 07_format_rules.md
│   └── 03_characters/
│       └── *.md
├── script/
│   ├── screenplay.fountain               # Assembled screenplay
│   └── voice_experiment.md
├── voice_experiment/
│   ├── LOCKED_VOICE_SPEC.md              # Winning voice
│   ├── round1_results.md
│   ├── round2_results.md
│   └── round3_results.md
├── coverage_reports/
│   └── *.md                              # Per-act evaluation reports
├── state/
│   ├── callback_ledger.json
│   ├── audience_state.json
│   └── convention_ledger.json
└── tools/
    ├── assemble_screenplay.py
    ├── page_count.py
    ├── callback_check.py
    └── ...
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Outlines cut too much from the novel | Review the narrative DNA extraction. Identify which subplots are essential. Increase `outline_count` for more options. |
| Outlines don't cut enough | Remember: a screenplay is ~110 pages. If the outline is still too long, it needs more aggressive compression. |
| Voice feels too literary for screen | The voice experiment should catch this. Provide feedback during the Phase 2 pause point. |
| Voice feels too sparse compared to source | Request refinement toward the source's density. The voice experiment allows calibration. |
| Revision ceiling reached before RECOMMEND | Review the blocking issues. Consider adjusting voice, outline, or accepting the ceiling. |
| Page count too high | The system should track this during drafting. If persistent, the outline may need further compression. |
| Page count too low | The outline may have cut too aggressively. Review whether key scenes are missing. |
| Dual-track voices feel inconsistent | Ensure `dual_track: true` is set. Review cross-track consistency test results. |
