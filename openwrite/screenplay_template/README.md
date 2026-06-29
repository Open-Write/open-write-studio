# Screenplay Template

*A self-contained template for writing a professional screenplay from scratch. Validated on produced screenplays through iterative revision.*

---

## What This Template Is For

This template provides everything a bot (or human) needs to write a screenplay from scratch:

- **Bible templates** for world-building, characters, and story structure
- **Skills files** with methodology, craft guidance, and revision protocols
- **Tools** for page counting, parenthetical auditing, callback tracking, and PDF export
- **State files** for tracking callbacks, audience knowledge, and writing conventions
- **Reference files** for voice consistency

This template has been validated on produced screenplays that went through voice experiments, iterative revisions, and achieved RECOMMEND from professional contest readers.

---

## Step-by-Step Workflow

### Phase 1: Preparation

1. **Read [`skills/start_here.md`](skills/start_here.md)** — understand the full system before doing anything.
2. **Read [`skills/screenplay_craft.md`](skills/screenplay_craft.md)** — learn the Silence Architecture voice, format rules, and craft principles.
3. **Read [`skills/critic_architecture.md`](skills/critic_architecture.md)** — understand the 8-mode review system.

### Phase 2: Bible Creation

4. **Fill [`bible/01_concept.md`](bible/01_concept.md)** — logline, genre, tone, themes, central question, structural misdirections.
5. **Fill [`bible/02_mythology.md`](bible/02_mythology.md)** — world rules, abilities, factions, the central dilemma.
6. **Create character profiles in [`bible/03_characters/`](bible/03_characters/)** — one file per character, using [`_template.md`](bible/03_characters/_template.md) as the starting point.
7. **Fill [`bible/04_outline.md`](bible/04_outline.md)** — scene-by-scene outline with emotional palette annotations.
8. **Fill [`bible/05_ending_notes.md`](bible/05_ending_notes.md)** — ending interpretation guidance (multiple defensible readings).
9. **Fill [`bible/06_craft_feeling.md`](bible/06_craft_feeling.md)** — emotional execution standards.
10. **Review [`bible/07_format_rules.md`](bible/07_format_rules.md)** — Fountain format rules (reload for every scene).

### Phase 3: Voice Selection

11. **Run voice experiments** per [`skills/voice_experiment_protocol.md`](skills/voice_experiment_protocol.md):
    - Define 5 candidate voices
    - Write test passages (3 runs per voice)
    - Have an adversarial reader evaluate cold
    - Rank by ceiling (highest single run), not average
    - Refine top 2, lock the winner
12. **Create a locked voice spec** (like [`reference/voice_card_template.md`](reference/voice_card_template.md)).

### Phase 4: Editorial Review

13. **Run pre-script editorial review** per [`skills/editorial_review_protocol.md`](skills/editorial_review_protocol.md):
    - 3 personas (contest reader, literary editor, development exec)
    - Each reviews the outline independently
    - Iterate until all return positive verdicts
    - Lock the outline

### Phase 5: Scene Writing

14. **Write scenes** to [`script/scenes/`](script/scenes/) as individual `.fountain` files.
    - For each scene: architect plans → screenwriter executes → critics review → cutter (conditional)
    - Load format rules (`bible/07_format_rules.md`) for every scene
    - Load character profiles for characters in the scene
    - Load the voice card for the scene's POV voice
15. **Track state** using [`state/callback_ledger.json`](state/callback_ledger.json), [`state/audience_state.json`](state/audience_state.json), and [`state/convention_ledger.json`](state/convention_ledger.json).

### Phase 6: Assembly

16. **Assemble scenes** into a single Fountain file:
    ```bash
    python tools/assemble_screenplay.py
    ```
17. **Check page count**:
    ```bash
    python tools/page_count.py
    ```
18. **Audit parentheticals**:
    ```bash
    python tools/parenthetical_audit.py
    ```
19. **Check callbacks**:
    ```bash
    python tools/callback_check.py
    ```

### Phase 7: Iterative Revision (Diminishing Returns)

20. **Run adversarial reader** (Lara Marsh) on the assembled script — cold coverage, no bible access.
21. **Iterate** per [`skills/iterative_revision_protocol.md`](skills/iterative_revision_protocol.md) Version 2:

**Revision continues until diminishing returns, not just until target verdict.**

Before each revision, assess feedback scope:
- **Surface**: line-level fixes (interiority violations, repetitive tics, hedge words)
- **Scene**: scene-level restructuring (pacing, exposition loops, underdeveloped scenes)
- **Structural**: outline-level changes (act structure, scene additions/deletions, character arc redesign)
- **Voice**: voice-level adjustments (monotony, register mismatch, convention overuse)

**Scope matching:**
- If feedback points to fundamental structural problems → go back to the outline
- If feedback suggests superficial work → stay at line level

**Stopping rules** (stop when ANY of):
- Delta ≤ 0.2 for **two consecutive iterations** (diminishing returns confirmed)
- Worst dimension unchanged for 3 consecutive iterations
- Composite score > 8.5 (approaching ceiling)
- Maximum iterations reached (configurable, default 7)

**The goal is the best work the system is capable of, not just hitting a target verdict.**

22. **Track progress** in a diminishing returns table:
| Iteration | Composite | Delta | Verdict | Notes |
|-----------|-----------|-------|---------|-------|
| 1 | 6.2 | — | PASS | Initial evaluation |
| 2 | 6.8 | +0.6 | PASS | Meaningful improvement |
| 3 | 7.0 | +0.2 | PASS | Marginal improvement |
| 4 | 7.1 | +0.1 | PASS | No improvement — STOP |

23. **After each iteration:** Run adversarial reader again using [`skills/editorial_review_system.md`](skills/editorial_review_system.md) Mode 1 for quantitative coverage with dimensional scores. Compare deltas to track improvement.

### Phase 8: Export

23. **Export to PDF**:
    ```bash
    python tools/fountain_to_pdf.py script/screenplay.fountain script/screenplay.pdf
    ```
24. **Verify page count** from the PDF (not from `page_count.py` estimate).

---

## Adaptation Workflow

If you're adapting a novel (or other source material) into a screenplay, use the **Adaptation Protocol** instead of the standard workflow. The adaptation protocol is a 3-phase pipeline that:

1. **Extracts narrative DNA** from the source material
2. **Designs and tests voice candidates** calibrated to the source
3. **Drafts the screenplay** with iterative review until RECOMMEND

See [`adaptation_template/README.md`](adaptation_template/README.md) for the full adaptation workflow.

**Quick start:**
1. Place your source novel in `source/`
2. Set your adaptation configuration (target length, autonomous mode, etc.)
3. Tell the system: "Adapt this novel into a screenplay."

The adaptation protocol can run autonomously (no pauses) or interactively (pause at each phase boundary for your review).

---

## Key Principles

### Silence Architecture Voice

The dominant voice pattern validated through production use. Meaning lives in what characters DON'T say.

- Characters speak only when they must. Silence carries meaning.
- Action lines render the gaps — what characters don't say, don't do, don't acknowledge.
- White space is structural. A single line alone on the page is a deliberate choice.
- Key character speeches: maximum 2 per act. When a key character speaks at length, it matters.
- Body anchors: hands, eyes, breath, spine, jaw — physical grounding in every scene.

Full spec: [`skills/screenplay_craft.md`](skills/screenplay_craft.md) (see "The Silence Architecture Voice" section).

### Iterative Revision Protocol

The 5-iteration methodology validated through production use:

1. Cut and Consolidate (mechanical compression)
2. Deepen and Earn (character specificity)
3. Resonance and Polish (callback reinforcement)
4. Structural Issues (top 3 from adversarial reader)
5. Final Character Depth (interiority for underserved characters)

Full protocol: [`skills/iterative_revision_protocol.md`](skills/iterative_revision_protocol.md)

### Line Count Over Page Count

For screenplays, line count is more reliable than page count estimation. Fountain files render differently in different tools. Use line count for internal tracking; use PDF page count only for industry submission.

**Baseline:** ~1,700 lines = ~60 pages in standard spec format (Courier 12, 1.5" left margin).

### Convention Ledger

Track ALL writing conventions — required AND prohibited — not just prohibited ones. The most dangerous repetition is the repetition of permitted constructions.

Full guidance: [`skills/convention_tracking.md`](skills/convention_tracking.md)

### Format Rules

The discipline document (`bible/07_format_rules.md`) must be reloaded for every scene. Key rules:

1. No camera directions. None.
2. No emotional parentheticals.
3. No adverbs in dialogue tags.
4. No interiority in action lines.
5. Dialogue is subtext, not statement.
6. Trust the actor.

---

## Validation

Every skill, tool, and protocol in this template was developed and validated during the production of multiple screenplays, including a 52-page single-voice script and a 113-page dual-voice script. The system has been tested with multiple independent adversarial readers and refined through iterative revision cycles.

---

## Directory Structure

```
screenplay_template/
├── README.md                    — This file (entry point)
├── bible/
│   ├── 01_concept.md            — Thematic frame template
│   ├── 02_mythology.md          — World/mythology template
│   ├── 03_characters/           — Character profiles
│   │   └── _template.md         — Blank character profile template
│   ├── 04_outline.md            — Scene outline template
│   ├── 05_ending_notes.md       — Ending interpretation template
│   ├── 06_craft_feeling.md      — Emotional execution template
│   └── 07_format_rules.md       — Fountain format rules
├── script/
│   ├── scenes/                  — Individual scene .fountain files go here
│   └── assemble_screenplay.py   — Assembles scenes into single Fountain file
├── reference/
│   └── voice_card_template.md  — Template voice card
├── state/
│   ├── callback_ledger.json     — Callback seed/payoff tracking
│   ├── audience_state.json      — Audience knowledge tracking
│   └── convention_ledger.json   — Writing convention tracking
├── tools/
│   ├── page_count.py            — Page count estimation
│   ├── parenthetical_audit.py   — Parenthetical counting/classification
│   ├── callback_check.py        — Callback verification
│   ├── fountain_to_pdf.py       — Fountain → PDF conversion
│   ├── assemble_screenplay.py   — Scene assembly script
│   └── convention_scan.py       — Convention pattern scanning
├── coverage_reports/            — Adversarial reader coverage goes here
├── critic_outputs/              — Critic review outputs go here
└── skills/
    ├── start_here.md            — Onboarding guide
    ├── screenplay_craft.md      — Craft guidance (Silence Architecture, etc.)
    ├── critic_architecture.md   — 8-mode review system
    ├── voice_experiment_protocol.md — Voice selection protocol
    ├── editorial_review_protocol.md — Pre-script review protocol
    ├── dual_voice_guidance.md   — Dual-voice management
    ├── iterative_revision_protocol.md — 5-iteration revision methodology
    ├── convention_tracking.md   — Convention ledger guidance
    └── pdf_export.md            — PDF export guide
```

---

## Skills Files Reference

| File | Purpose | When to Read |
|------|---------|--------------|
| [`skills/start_here.md`](skills/start_here.md) | Onboarding guide | First |
| [`skills/screenplay_craft.md`](skills/screenplay_craft.md) | Craft guidance, Silence Architecture, format rules | Before writing |
| [`skills/critic_architecture.md`](skills/critic_architecture.md) | 8-mode review system | Before running critics |
| [`skills/voice_experiment_protocol.md`](skills/voice_experiment_protocol.md) | Voice selection through empirical testing | Phase 3 |
| [`skills/editorial_review_protocol.md`](skills/editorial_review_protocol.md) | Pre-script outline review | Phase 4 |
| [`skills/dual_voice_guidance.md`](skills/dual_voice_guidance.md) | Managing two POV voices | If dual-track |
| [`skills/iterative_revision_protocol.md`](skills/iterative_revision_protocol.md) | 5-iteration revision methodology | Phase 7 |
| [`skills/convention_tracking.md`](skills/convention_tracking.md) | Convention ledger usage | During writing |
| [`skills/pdf_export.md`](skills/pdf_export.md) | PDF export instructions | Phase 8 |

---

*All protocols validated against production use.*
