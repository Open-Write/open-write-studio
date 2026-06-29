# TV Template — Episodic Production System

*Adapted from the screenplay and novel template systems for episodic television production. This template provides a complete pipeline from series bible through episode scripts, with cross-episode tracking, multi-model critic review, and writers' room simulation.*

---

## What This Is

A complete TV writing template that adapts the proven screenplay system for episodic production. It preserves everything that works — multi-model critics, callback tracking, convention ledger, voice experiment protocol, state MCP server — and adds TV-specific infrastructure: episode assembly, season arc tracking, cross-episode continuity, and writers' room workflow.

**What carries over from the screenplay template:**
- Multi-model critic pipeline (show-don't-tell, voice, palette, continuity, naturalism, adversarial reader)
- Callback ledger for tracking seeds and payoffs
- Convention ledger for preventing writing drift
- Voice experiment protocol for selecting and locking writing voices
- Format rules discipline (reloaded every scene)
- Iterative revision protocol with diminishing-returns tracking
- Pre-script editorial review with 3 personas

**What's new for TV:**
- Episode-level organization (S01E01, S01E02, etc.)
- Season arc tracking across episodes
- Cross-episode callback and continuity checking
- Writers' room simulation protocol
- Episode assembly and season assembly tools
- Per-episode page count targets (half-hour: ~30 pages, one-hour: ~55-65 pages)
- Cold open, act breaks, and teaser/epilogue structure
- Series bible with season-level planning
- Character state tracking across episodes

---

## Directory Structure

```
tv_template/
├── README.md                          # This file
├── bible/
│   ├── 01_series_concept.md           # Series concept/logline/genre/tone
│   ├── 02_world_bible.md              # World building document
│   ├── 03_characters/
│   │   ├── _template.md               # Character profile template
│   │   └── .gitkeep
│   ├── 04_season_arc.md               # Season-level arc outline template
│   ├── 05_episode_outlines/
│   │   ├── _template.md               # Episode outline template
│   │   └── S01E01_example.md          # Example first episode outline
│   ├── 06_format_rules.md             # TV script format rules
│   ├── 07_craft_feeling.md            # Craft, tone, and feeling guide
│   └── 08_writers_room_notes.md       # Writers' room protocol
├── scripts/
│   └── .gitkeep                       # Completed episode scripts
├── reference/
│   └── .gitkeep                       # Reference materials
├── state/
│   ├── audience_state.json            # Per-episode audience state tracking
│   ├── callback_ledger.json           # Cross-episode callback/setup tracking
│   ├── convention_ledger.json         # Convention tracking across episodes
│   ├── season_arc_tracker.json        # Season arc progress tracking
│   └── character_state_tracker.json   # Character state across episodes
├── critic_outputs/
│   └── .gitkeep                       # Critic review outputs
├── coverage_reports/
│   └── .gitkeep                       # Coverage reports
└── tools/
    ├── episode_assemble.py            # Assemble episode script from scenes
    ├── season_assemble.py             # Assemble full season from episodes
    ├── callback_check.py              # Check callbacks across episodes
    ├── continuity_check.py            # Check continuity across episodes
    ├── page_count.py                  # Page counting (TV standard ~1 page/min)
    ├── word_count.py                  # Word count tool
    ├── convention_scan.py             # Convention scanner
    ├── parenthetical_audit.py         # Parenthetical audit tool
    └── episode_export.py              # Export episode to PDF/fountain
```

---

## How to Use This Template

### Phase 1: Series Development

1. **Fill out [`bible/01_series_concept.md`](bible/01_series_concept.md)** — Logline, genre, tone, central themes, the central question.
2. **Fill out [`bible/02_world_bible.md`](bible/02_world_bible.md)** — World rules, geography, technology, culture, history.
3. **Create character profiles** — Copy [`bible/03_characters/_template.md`](bible/03_characters/_template.md) for each main character. Fill in character voice profiles.
4. **Fill out [`bible/04_season_arc.md`](bible/04_season_arc.md)** — Season-level arc with episode breakdown.
5. **Fill out [`bible/07_craft_feeling.md`](bible/07_craft_feeling.md)** — Emotional execution standards for the series.
6. **Fill out [`bible/08_writers_room_notes.md`](bible/08_writers_room_notes.md)** — Writers' room protocol and creative guidelines.

### Phase 2: Pre-Production Review

Run the **Editorial Review Protocol** (see [`skills/editorial_review_protocol.md`](../skills/editorial_review_protocol.md)):
- Present the series bible and season arc to 3 editorial personas
- Iterate until all return positive verdicts
- Lock the season outline

Run the **Voice Experiment Protocol** (see [`skills/voice_experiment_protocol.md`](../skills/voice_experiment_protocol.md)):
- Test 5 voice candidates
- Lock the winning voice
- For multi-track shows, run the cross-track "One Writer" test

### Phase 3: Episode Production

For each episode:

1. **Outline** — Fill out [`bible/05_episode_outlines/_template.md`](bible/05_episode_outlines/_template.md) for the episode.
2. **Architect** — Plan each scene (architect mode).
3. **Write** — Write scenes in Fountain markup (screenwriter mode).
4. **Critique** — Run the multi-model critic pipeline:
   - Show-don't-tell critic
   - Voice critic (per character)
   - Palette critic
   - Continuity critic (cross-episode)
   - Naturalism critic
   - Adversarial reader (cold coverage)
5. **Revise** — Apply iterative revision protocol.
6. **Cut** — Conditional (only when critics flag material).
7. **Assemble** — Run `python tools/episode_assemble.py --episode S01E01`
8. **Export** — Run `python tools/episode_export.py --episode S01E01`

### Phase 4: Season Assembly

After all episodes are complete:
1. Run `python tools/season_assemble.py --season 1`
2. Run `python tools/callback_check.py --season 1` to verify all cross-episode callbacks are paid off
3. Run `python tools/continuity_check.py --season 1` to verify continuity across episodes
4. Run adversarial reader on the full season

---

## Key Differences from the Screenplay Template

| Aspect | Screenplay Template | TV Template |
|--------|---------------------|-------------|
| Structure | Single 110-120 page script | Multiple episodes per season |
| Scenes | 52 scenes in one file | Scenes organized by episode |
| Callbacks | Single-scene seeds/payoffs | Cross-episode seeds/payoffs |
| Continuity | Within one script | Across entire season |
| Page target | 110-125 pages | 30 pages (half-hr) or 55-65 pages (one-hr) per episode |
| State tracking | Single project state | Per-episode + season-level tracking |
| Assembly | One assemble run | Episode assembly + season assembly |
| Revision | One revision pass | Per-episode revision + season-level consistency pass |
| Cold open | Part of Act One | Standalone pre-title sequence |
| Act breaks | 4-act structure | 4-6 acts with commercial breaks (network) or continuous (streaming) |

---

## The TV Critic Pipeline

The critic pipeline is identical to the screenplay template but with cross-episode awareness:

```
Episode Outline
  → Editorial Review (3 personas)
    → Outline locked
      → Per-scene generation:
          Architect → Screenwriter → Critics → Cutter
      → Episode assembly
        → Episode-level adversarial reader
          → Cross-episode continuity check
            → Season assembly (after all episodes)
              → Season-level adversarial reader
```

### Critics (per scene, same as screenplay):
- **Show-don't-tell critic** — Mechanical enforcement of format rules
- **Voice critic** — Per-character voice consistency review (one call per character)
- **Palette critic** — Emotional palette verification
- **Continuity critic** — Cross-episode state/timeline/callback review
- **Naturalism critic** — AI-tell detection
- **Cutter** — Conditional, removes only flagged material (separate model state from writer)

### Critics (per episode):
- **Adversarial reader** — Cold coverage without bible access

### Critics (per season):
- **Season-level adversarial reader** — Cold coverage of the full season
- **Cross-episode callback audit** — All seeds paid off
- **Cross-episode continuity audit** — No contradictions across episodes

---

## State Files

| File | Purpose |
|------|---------|
| [`state/audience_state.json`](state/audience_state.json) | Tracks what the audience believes at each point, organized by episode |
| [`state/callback_ledger.json`](state/callback_ledger.json) | Cross-episode callback seeds and payoffs |
| [`state/convention_ledger.json`](state/convention_ledger.json) | Writing convention tracking across all episodes |
| [`state/season_arc_tracker.json`](state/season_arc_tracker.json) | Season arc progress — which storylines are active/resolved |
| [`state/character_state_tracker.json`](state/character_state_tracker.json) | Character knowledge, relationships, and physical state across episodes |

---

## Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| [`tools/episode_assemble.py`](tools/episode_assemble.py) | Assemble one episode from scene files | `python tools/episode_assemble.py --episode S01E01` |
| [`tools/season_assemble.py`](tools/season_assemble.py) | Assemble full season from episodes | `python tools/season_assemble.py --season 1` |
| [`tools/callback_check.py`](tools/callback_check.py) | Check callbacks across episodes | `python tools/callback_check.py --episode S01E05` or `--season 1` |
| [`tools/continuity_check.py`](tools/continuity_check.py) | Check continuity across episodes | `python tools/continuity_check.py --season 1` |
| [`tools/page_count.py`](tools/page_count.py) | Page counting for TV scripts | `python tools/page_count.py --episode S01E01` |
| [`tools/word_count.py`](tools/word_count.py) | Word count tool | `python tools/word_count.py` |
| [`tools/convention_scan.py`](tools/convention_scan.py) | Convention ledger scanner | `python tools/convention_scan.py` |
| [`tools/parenthetical_audit.py`](tools/parenthetical_audit.py) | Parenthetical audit | `python tools/parenthetical_audit.py --episode S01E01` |
| [`tools/episode_export.py`](tools/episode_export.py) | Export episode to PDF/fountain | `python tools/episode_export.py --episode S01E01` |

---

## Naming Conventions

- **Episode scripts:** `scripts/S01E01_title.fountain`
- **Scene files:** `scripts/scenes/S01E01/01_cold_open.fountain`, `scripts/scenes/S01E01/02_act_one.fountain`, etc.
- **Episode outlines:** `bible/05_episode_outlines/S01E01_title.md`
- **Character profiles:** `bible/03_characters/character_name.md`
- **Critic outputs:** `critic_outputs/S01E01_scene_01_show_dont_tell.md`
- **Coverage reports:** `coverage_reports/S01E01_coverage.md`

---

## Scalability

This template works for:
- **Half-hour comedies** (~30 pages per episode, 10-13 episodes per season)
- **One-hour dramas** (~55-65 pages per episode, 8-13 episodes per season)
- **Limited series** (6-10 episodes, single season)
- **Ongoing series** (multiple seasons, expand the state files)
- **Anthology series** (reset character state per episode, keep convention ledger)

To adapt for format, adjust the page targets in [`bible/06_format_rules.md`](bible/06_format_rules.md) and the episode count in [`bible/04_season_arc.md`](bible/04_season_arc.md).

---

## Referenced Skills Files

These files from the main project contain methodologies that apply to TV production:

| Skill | Location | TV Application |
|-------|----------|----------------|
| Screenplay Craft | [`skills/screenplay_craft.md`](../skills/screenplay_craft.md) | All craft principles apply to TV scripts |
| Critic Architecture | [`skills/critic_architecture.md`](../skills/critic_architecture.md) | The 8-mode review system |
| Convention Tracking | [`skills/convention_tracking.md`](../skills/convention_tracking.md) | Preventing writing drift across episodes |
| Editorial Review Protocol | [`skills/editorial_review_protocol.md`](../skills/editorial_review_protocol.md) | Pre-production review by 3 personas |
| Iterative Revision Protocol | [`skills/iterative_revision_protocol.md`](../skills/iterative_revision_protocol.md) | Revision with diminishing-returns tracking |
| Dual-Voice Guidance | [`skills/dual_voice_guidance.md`](../skills/dual_voice_guidance.md) | Multi-track shows (e.g., dual timelines) |

---

## Getting Started

1. Copy this entire `tv_template/` directory to your project root.
2. Fill out the bible files starting with `01_series_concept.md`.
3. Create character profiles using the template in `03_characters/_template.md`.
4. Plan your season arc in `04_season_arc.md`.
5. Run editorial review on the bible before writing any episodes.
6. Write episodes one at a time, using the per-episode production pipeline.
7. Assemble and export after each episode is complete.
8. Run season-level checks after all episodes are done.

---

*Template adapted from screenplay and novel production systems. All craft knowledge, critic architecture, and revision protocols carry over with TV-specific adaptations.*
