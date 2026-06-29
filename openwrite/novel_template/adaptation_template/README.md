# Novel Adaptation Template

> **Purpose:** Adapt a screenplay (or other source material) into a novel using the 3-phase adaptation protocol.

---

## Overview

This template provides everything needed to adapt a screenplay into a novel. The adaptation protocol ([`skills/adaptation_protocol.md`](../../skills/adaptation_protocol.md)) guides the process through three phases:

1. **Story Outline** — Extract narrative DNA from the screenplay, design novel outlines
2. **Author Voice** — Design and test prose voice candidates
3. **Drafting** — Write the novel chapter by chapter with iterative review

---

## Getting Started

### 1. Upload Source Material

Place your source screenplay in the project root:

```
your_project/
├── source/
│   └── your_screenplay.fountain    ← Source screenplay here
├── bible/
├── manuscript/
├── voice_experiment/
└── ...
```

The system reads Fountain (`.fountain`) or PDF screenplay formats.

### 2. Configure Adaptation Variables

Create or edit your adaptation configuration. You can place this in a `adaptation_config.md` file at the project root or provide it directly:

```yaml
# Adaptation Configuration
source: ./source/your_screenplay.fountain
target_type: novel
autonomous: false              # true = run without pausing; false = pause at each phase
outline_count: 2               # Number of outline options to generate
voice_count: 5                 # Number of voice candidates to test
voice_runs: 3                  # Runs per voice candidate
max_iterations: 5              # Max revision iterations per act/part
target_verdict: "Recommend"    # "Recommend" or "Acquisition Recommendation"
line_count_min: 70000          # Minimum word count
line_count_max: 90000          # Maximum word count
dual_track: false              # true if adaptation has alien/non-human POV tracks
```

### 3. Start the Adaptation

Tell the system:

> "Adapt this screenplay into a novel."

The system will begin Phase 1, reading the screenplay and extracting its narrative DNA.

---

## Phase-by-Phase Walkthrough

### Phase 1: Story Outline

**What happens:**
1. System reads your screenplay completely
2. Extracts narrative DNA: plot structure, character arcs, themes, emotional beats, world-building, callbacks
3. Generates `outline_count` novel outline options
4. Runs editorial review (Lara Marsh, Dr. Elena Vasquez, Marcus Webb) on each outline
5. Selects the best outline based on editorial consensus

**Your screenplay's visual storytelling becomes prose:**
- Scene descriptions → rich sensory narration
- Dialogue → dialogue integrated with action, thought, and description
- Subtext → interiority (character thoughts, feelings, motivations)
- Montages → narrative summary or expanded scenes
- Voice-over → free indirect discourse or direct narration

**Pause point (if `autonomous: false`):**
- Review the outlines and editorial feedback
- Select your preferred outline (or request revisions)
- Adjust any configuration variables
- Approve to continue

**Outputs:** Selected outline in [`bible/04_outline.md`](../bible/04_outline.md), updated bible files, narrative DNA document.

### Phase 2: Author Voice

**What happens:**
1. System analyzes your screenplay's voice (dialogue cadence, description style, emotional register)
2. Designs `voice_count` prose voice candidates calibrated to the source
3. Runs the voice experiment: Round 1 (all voices) → Round 2 (top 2) → Round 3 (winner)
4. Lara Marsh evaluates each round
5. Locks the winning voice

**What "calibrated to the source" means:**
- If your screenplay has spare, Hemingway-esque dialogue, the prose voice won't become purple prose
- If your screenplay has rich visual description, the prose voice will match that density
- The voice adapts the source's sensibility for the target medium

**Pause point (if `autonomous: false`):**
- Review voice candidates and experiment results
- Adjust voice direction if needed
- Approve the locked voice

**Outputs:** Locked voice specification in [`voice_experiment/LOCKED_VOICE_SPEC.md`](../voice_experiment/LOCKED_VOICE_SPEC.md).

### Phase 3: Drafting

**What happens:**
1. System generates the novel chapter by chapter using the locked voice and selected outline
2. After each part/act: Lara Marsh cold evaluation
3. If not RECOMMEND: identifies issues, revises, re-evaluates
4. Continues until RECOMMEND or ceiling reached
5. Assembles the complete manuscript

**The iterative cycle:**
```
Generate → Evaluate → Identify Issues → Revise → Re-evaluate → [repeat until RECOMMEND]
```

**Pause point (if `autonomous: false`):**
- Review each evaluation report
- Adjust revision direction
- Let the system continue or accept the current state

**Outputs:** Complete novel manuscript, coverage reports, final verdict.

---

## Running in Autonomous Mode

Set `autonomous: true` to run the entire pipeline without pausing:

```yaml
autonomous: true
```

The system will:
1. Generate outlines → pick the best one automatically
2. Run voice experiment → lock the winner automatically
3. Draft the novel → iterate until RECOMMEND or ceiling → report final status

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

## Example: Screenplay-to-Novel Adaptation

A produced novel was adapted from a screenplay using this protocol (before it was formalized). Key outcomes:

| Phase | Result |
|-------|--------|
| Phase 1 | 3 outline options generated. Option C selected for its chapter structure and interiority strategy. |
| Phase 2 | 5 voice candidates tested. Winning voice locked — spare prose with controlled interiority bursts. |
| Phase 3 | 52 chapters drafted across 5 parts. Iterative revision through multiple passes. Final verdict: **Acquisition Recommendation**. |

**Lessons learned:**
- The screenplay's visual storytelling required significant expansion for prose (sensory detail, character thought, backstory)
- The bible/manuscript split (bible files separate from manuscript) improved drafting focus
- Cross-model triangulation (different AI models for different critics) caught blind spots
- The callback ledger was essential for tracking plant/payoff across 70,000+ words

---

## Project Structure

After adaptation, your project will have this structure:

```
your_project/
├── source/
│   └── your_screenplay.fountain          # Source material
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
├── manuscript/
│   ├── chapters/                         # Individual chapter files
│   ├── novel_full.md                       # Assembled manuscript
│   └── chapters_pdf/                     # PDF exports
├── voice_experiment/
│   ├── LOCKED_VOICE_SPEC.md              # Winning voice
│   ├── round1_results.md
│   ├── round2_results.md
│   └── round3_results.md
├── coverage_reports/
│   └── *.md                              # Per-act evaluation reports
├── state/
│   ├── callback_ledger.json
│   ├── reader_state.json
│   └── convention_ledger.json
└── tools/
    ├── assemble.py
    ├── word_count.py
    ├── callback_check.py
    └── ...
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Outlines feel too different from source | Review the narrative DNA extraction. Adjust `outline_count` to get more options. |
| Voice doesn't feel right | Request voice refinement in Phase 2 pause point. Provide specific feedback on what to adjust. |
| Revision ceiling reached before RECOMMEND | Review the blocking issues. Consider adjusting voice, outline, or accepting the ceiling. |
| Novel is too short | Increase `line_count_min`. The system will add more interiority and expansion. |
| Novel is too long | Decrease `line_count_max`. The system will be more selective about what to expand. |
| Dual-track voices feel inconsistent | Ensure `dual_track: true` is set. Review cross-track consistency test results. |
