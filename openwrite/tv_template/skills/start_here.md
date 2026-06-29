# Start Here — TV Production Onboarding

*Read this file first when starting a TV series project. It contains everything you need to orient yourself before doing any work.*

*This template is based on screenplay and novel production systems, adapted for episodic television. The production system and methodologies described here were developed and validated across multiple produced works.*

---

## What Is This Template?

This is a self-contained TV series production system. It provides:

- **Bible templates** (`bible/`) — series concept, world bible, character profiles, season arc, episode outlines, format rules, craft guidance, writers' room notes
- **State tracking** (`state/`) — character state tracker, season arc tracker, callback ledger, audience state, convention ledger
- **Python tools** (`tools/`) — page count, parenthetical audit, callback check, continuity check, convention scan, episode assemble, season assemble, word count, episode export
- **Skills files** (`skills/`) — TV craft guidance, critic architecture, voice guidance, editorial review, revision protocol, convention tracking
- **Custom modes** (`.kilo/modes/`) — showrunner, season architect, episode architect, episode writer, cutter, 6 critics, meta-critic, adversarial reader, continuity editor

A bot with access to only this directory should have everything it needs to produce a complete TV season.

---

## Environment Detection

Before using any commands, check your environment to determine which command set to use:

### Check Your Shell

**PowerShell (Windows):**
```powershell
$PSVersionTable.PSVersion
if ($env:OS -like '*Windows*') { 'Running on Windows PowerShell' }
```

**Bash (Unix/Linux/Mac):**
```bash
echo $SHELL
uname
```

### Choose Your Command Set

- **Windows PowerShell:** Follow [`skills/windows_powershell_guide.md`](windows_powershell_guide.md)
- **Bash (Unix/Linux/Mac):** Use standard bash commands
- **WSL (Windows Subsystem for Linux):** Follow [`skills/wsl_git_bash_setup.md`](wsl_git_bash_setup.md)
- **Git Bash (Windows):** Use bash commands within Git Bash environment

### If Tools Fail

If you encounter tool errors, see [`skills/tool_limitation_workarounds.md`](tool_limitation_workarounds.md) for alternative approaches.

---

## Before You Do Anything

1. **Read this file** (`skills/start_here.md`) — you're doing it now.
2. **Read [`tv_craft.md`](tv_craft.md)** — understand TV-specific craft principles.
3. **Read [`tv_critic_architecture.md`](tv_critic_architecture.md)** — understand the 15-mode review system (includes meta-critic).
4. **Read [`bible/08_writers_room_notes.md`](../bible/08_writers_room_notes.md)** — understand the writers' room workflow.

---

## What Is This Project?

A TV series project produced using AI-assisted writers' room methodology. The system simulates a professional TV writers' room using specialized AI modes:

| Role | Mode | What It Does |
|------|------|-------------|
| Showrunner | `tv-showrunner` | Oversees the entire production pipeline |
| Season Architect | `tv-season-architect` | Plans season-level arcs and episode breakdowns |
| Episode Architect | `tv-episode-architect` | Plans individual episodes scene by scene |
| Episode Writer | `tv-episode-writer` | Writes episodes in Fountain format |
| Cutter | `tv-cutter` | Conditional — removes only flagged material |
| Show-Don't-Tell Critic | `critic-show-tv` | Mechanical format enforcement |
| Voice Critic | `critic-voice-tv` | Per-character voice consistency |
| Palette Critic | `critic-palette-tv` | Emotional palette verification |
| Continuity Critic | `critic-continuity-tv` | Cross-episode continuity checking |
| Naturalism Critic | `critic-naturalism-tv` | AI-tell detection |
| Meta-Critic | `critic-meta-tv` | Cross-episode review synthesis — reviews the critics |
| Adversarial Reader | `adversarial-reader-tv` | Cold coverage (Lara Marsh, 14 years) |
| Continuity Editor | `continuity-editor` | State file maintenance |

**Human creator:** The showrunner-equivalent. Final creative authority. Approves outlines, reviews scripts, makes casting-level decisions.

---

## The Workflow (High Level)

```
1. Fill the Bible
   → 01_series_concept.md, 02_world_bible.md, 03_characters/,
     04_season_arc.md, 05_episode_outlines/, 06_format_rules.md,
     07_craft_feeling.md, 08_writers_room_notes.md

1.5. Pre-Production Review (run after bible, before production)
   → Review the bible for internal contradictions
   → Run structural agency and representation checks
   → Apply the two Opus tests:
     (a) Decision-bends-plot: Does every significant character make at
         least one decision per season that other characters respond to
         consequentially?
     (b) Removal-breaks-causal-chain: Could any character's scenes be
         removed from the episode without affecting the episode's events?
   → Check: Does the period text corpus include voices from all
     represented populations?
   → Address critical and moderate issues before proceeding to production
   → Output: critic_outputs/pre_production_review.md

2. Plan the Season
   → Season Architect produces season arc and episode breakdowns
   → Review bible for contradictions
   → Editorial review (3 personas) → revise → lock

3. Write Episodes (for each episode)
   → Episode Architect plans scene by scene
   → Episode Writer writes in Fountain
   → Critic pipeline (show-don't-tell, voice, palette, continuity with deep verification, naturalism)
   → Episode Writer addresses issues
   → Assembly → page count check → parenthetical audit
    → Cutter (conditional — only when critics flag material)
   → Adversarial Reader (cold coverage)
   → Continuity Editor updates state files
   → Showrunner approves → episode lock
   → After every 2-3 episodes: meta-critic reviews critic outputs → refinement notes

4. Season Review
   → Adversarial Reader on full season
   → Continuity check across all episodes
   → Callback audit → character arc audit → thematic coherence
   → Season lock

5. Export
   → tools/episode_export.py → PDF
   → tools/season_assemble.py → full season

6. Completion Verification
   → Run `python tools/verify_completion.py` against the manifest
   → Only PASS certifies the workflow as complete
```

---

## Critical Rules

1. **The format rules document is sacred.** Reload [`bible/06_format_rules.md`](../bible/06_format_rules.md) before every scene. Without it, the script swells.
2. **Never modify state files directly.** Use the tools or the continuity editor mode to prevent schema corruption.
3. **The bible is law.** No episode contradicts the bible without an amendment to the bible first.
4. **Cross-episode consistency is everyone's job.** The continuity critic catches what others miss, but every mode should be aware of cross-episode implications.
5. **The adversarial reader reads cold.** No bible access. No prior episode context. What's on the page is what's on the page.
6. **Every episode must be self-contained.** Even in a heavily serialized show, each episode must have a beginning, middle, and end.
7. **The cold open must hook. Act breaks must compel. The final image must linger.** These are the structural non-negotiables of television.
8. **Track what you learn.** Log issues and insights in the runlog or in skill files.
9. **The completion manifest is law.** Only `verify_completion.py` returning PASS may certify the workflow as complete. Never report success over a failing manifest.

---

## The 15-Mode Critic System

| Mode | Purpose | When to Run |
|------|---------|-------------|
| tv-showrunner | Pipeline management, quality control | Continuous |
| tv-season-architect | Season arc planning | Season start |
| tv-episode-architect | Episode scene planning | Before each episode |
| tv-episode-writer | Fountain script writing | Each scene |
| tv-cutter | Conditional — removes only flagged material | After all critics |
| critic-show-tv | Show-don't-tell enforcement | Every scene |
| critic-voice-tv | Per-character voice consistency review | Every scene, per character |
| critic-palette-tv | Emotional palette verification | Every episode |
| critic-continuity-tv | Cross-episode continuity with deep verification | Every episode |
| critic-naturalism-tv | AI-tell detection | Every episode |
| critic-meta-tv | Cross-episode review synthesis — reviews the critics | After every 2-3 episodes |
| adversarial-reader-tv | Cold coverage | After major revisions |
| continuity-editor | State file maintenance | After each episode lock |
| rewrite-prepper | Produces rewrite preparation documents for human rewriters | Before revision passes |

See [`tv_critic_architecture.md`](tv_critic_architecture.md) for full details.

---

## Key Methodologies

| Methodology | Skills File | When to Use |
|-------------|-------------|-------------|
| TV Craft | [`tv_craft.md`](tv_craft.md) | When writing or revising TV scripts |
| TV Critic Architecture | [`tv_critic_architecture.md`](tv_critic_architecture.md) | When running the review system |
| TV Revision Protocol | [`tv_revision_protocol.md`](tv_revision_protocol.md) | When revising episodes or the season (named strategies: Grounding, Combination, Simplification, Divergent, Coherence) |
| Meta-Critic Protocol | [`meta_critic_protocol.md`](meta_critic_protocol.md) | After every 2-3 episodes — cross-episode review synthesis |
| TV Convention Tracking | [`tv_convention_tracking.md`](tv_convention_tracking.md) | When tracking writing conventions |
| TV Voice Guidance | [`tv_voice_guidance.md`](tv_voice_guidance.md) | When managing multi-episode voice consistency |
| TV Editorial Review | [`tv_editorial_review.md`](tv_editorial_review.md) | When reviewing outlines before generation |
| Windows PowerShell Guide | [`skills/windows_powershell_guide.md`](windows_powershell_guide.md) | When working on Windows PowerShell |
| WSL/Git Bash Setup | [`skills/wsl_git_bash_setup.md`](wsl_git_bash_setup.md) | When using WSL or Git Bash on Windows |
| Large File Operations | [`skills/large_file_operations.md`](large_file_operations.md) | When working with files over 1,000 lines |
| Tool Limitation Workarounds | [`skills/tool_limitation_workarounds.md`](tool_limitation_workarounds.md) | When tools fail or are unavailable |
| Definition of Done | [`skills/definition_of_done.md`](definition_of_done.md) | When building or verifying the completion manifest |
| Known Limitations | [`skills/known_limitations.md`](known_limitations.md) | Read before publishing — documented failure modes |
| MCP Debugging | [`skills/mcp_debugging.md`](mcp_debugging.md) | When MCP tool calls fail or hallucinate parameters |

---

## The Tools

| Tool | Command | Purpose |
|------|---------|---------|
| Page count | `python tools/page_count.py --episode S01E01` | Check page count against target |
| Parenthetical audit | `python tools/parenthetical_audit.py --episode S01E01` | Verify parenthetical count under limit |
| Callback check | `python tools/callback_check.py --episode S01E01` | Check callback ledger status |
| Continuity check | `python tools/continuity_check.py --episode S01E01` | Cross-episode continuity verification |
| Convention scan | `python tools/convention_scan.py` | Scan scripts for convention patterns |
| Episode assemble | `python tools/episode_assemble.py --episode S01E01` | Assemble scenes into single episode |
| Season assemble | `python tools/season_assemble.py` | Assemble all episodes into full season |
| Word count | `python tools/word_count.py` | Count words by episode and scene |
| Episode export | `python tools/episode_export.py --episode S01E01` | Export episode to PDF |
| Verify completion | `python tools/verify_completion.py` | Verify manifest — only PASS certifies done |

**Note:** Always set `PYTHONIOENCODING=utf-8` before running tools.

---

## The Bible Files

| File | Purpose | When to Load |
|------|---------|--------------|
| [`bible/01_series_concept.md`](../bible/01_series_concept.md) | Series concept, logline, central question | Before planning any episode |
| [`bible/02_world_bible.md`](../bible/02_world_bible.md) | World-building, rules of the show's universe | When writing scenes in the world |
| [`bible/03_characters/`](../bible/03_characters/) | Character profiles (voice registers) | For every scene with that character |
| [`bible/04_season_arc.md`](../bible/04_season_arc.md) | Season arc plan with A/B/C threads | For every episode planning session |
| [`bible/05_episode_outlines/`](../bible/05_episode_outlines/) | Per-episode outlines | For every episode (N±1) |
| [`bible/06_format_rules.md`](../bible/06_format_rules.md) | TV format discipline, forbidden patterns | **RELOAD BEFORE EVERY SCENE** |
| [`bible/07_craft_feeling.md`](../bible/07_craft_feeling.md) | Emotional execution standards | For every episode |
| [`bible/08_writers_room_notes.md`](../bible/08_writers_room_notes.md) | Writers' room workflow and guidelines | At production start |

---

## The State Files

| File | Purpose | Updated By |
|------|---------|------------|
| [`state/character_state_tracker.json`](../state/character_state_tracker.json) | Character knowledge, physical states, relationships | Continuity editor after each episode |
| [`state/season_arc_tracker.json`](../state/season_arc_tracker.json) | Episode-by-episode season progress | Continuity editor after each episode |
| [`state/callback_ledger.json`](../state/callback_ledger.json) | Seeded callbacks and payoff deadlines | Continuity editor + episode architect |
| [`state/audience_state.json`](../state/audience_state.json) | What the audience believes at each point | Continuity editor after each episode |
| [`state/convention_ledger.json`](../state/convention_ledger.json) | Writing convention tracking | Convention scan tool |

---

## Directory Structure

```
tv_template/
├── .roomodes                    # Custom mode definitions (14 modes)
├── .roo/                        # Rules files for each mode
│   ├── rules-tv-showrunner.md
│   ├── rules-tv-season-architect.md
│   ├── rules-tv-episode-architect.md
│   ├── rules-tv-episode-writer.md
│   └── rules-tv-cutter.md
├── bible/                       # Series bible
│   ├── 01_series_concept.md     # Series concept and logline
│   ├── 02_world_bible.md        # World-building
│   ├── 03_characters/           # Character profiles
│   ├── 04_season_arc.md         # Season arc plan
│   ├── 05_episode_outlines/     # Per-episode outlines
│   ├── 06_format_rules.md       # Format discipline (reload every scene)
│   ├── 07_craft_feeling.md      # Craft and emotional standards
│   └── 08_writers_room_notes.md # Writers' room workflow
├── scripts/                     # Written episodes
│   └── scenes/
│       └── S01EXX/              # Per-episode scene files (.fountain)
├── critic_outputs/              # Critic reports and episode plans
├── coverage_reports/            # Adversarial reader coverage
├── audit_reports/               # Bible auditor reports
├── reference/                   # Reference documents
├── state/                       # State tracking files
│   ├── character_state_tracker.json
│   ├── season_arc_tracker.json
│   ├── callback_ledger.json
│   ├── audience_state.json
│   └── convention_ledger.json
├── skills/                      # Skills and methodology docs
│   ├── start_here.md            # This file
│   ├── tv_craft.md              # TV craft guidance
│   ├── tv_critic_architecture.md # Critic system docs
│   ├── tv_revision_protocol.md  # Revision protocol
│   ├── tv_convention_tracking.md # Convention tracking
│   ├── tv_voice_guidance.md     # Voice consistency guidance
│   ├── tv_editorial_review.md   # Editorial review protocol
│   ├── windows_powershell_guide.md # Windows PowerShell commands
│   ├── wsl_git_bash_setup.md    # WSL/Git Bash setup guide
│   ├── large_file_operations.md # Large file handling guide
│   └── tool_limitation_workarounds.md # Tool failure workarounds
└── tools/                       # Python production tools
    ├── page_count.py
    ├── parenthetical_audit.py
    ├── callback_check.py
    ├── continuity_check.py
    ├── convention_scan.py
    ├── episode_assemble.py
    ├── season_assemble.py
    ├── word_count.py
    └── episode_export.py
```

---

## First Steps for a New TV Project

1. **Define the series concept.** Fill `bible/01_series_concept.md` with the show's logline, central question, genre, tone, and thematic frame.
2. **Build the world.** Fill `bible/02_world_bible.md` with the rules, locations, and institutions of the show's universe.
3. **Create characters.** Fill `bible/03_characters/` with profiles for all series regulars. Use the voice register framework for voice differentiation.
4. **Plan the season.** Use the season architect to produce `bible/04_season_arc.md` and `bible/05_episode_outlines/`.
5. **Review the bible for contradictions.** Catch contradictions before they cascade into episodes.
6. **Run editorial review.** Three personas review the season plan. Revise until all return positive verdicts.
7. **Lock the season plan.** No structural changes after lock.
8. **Begin episode production.** Follow the per-episode pipeline for each episode in order.

---

## If You're Stuck

- Re-read the relevant skills file for your current task
- Check the tools — `continuity_check.py` and `convention_scan.py` catch issues you're too close to see
- Run the adversarial reader — cold coverage reveals what bible-aware review misses
- When in doubt: make it more specific, more physical, more this-character, this-moment
- Ask the human creator before making assumptions about creative direction

---

*This onboarding guide is based on the production systems developed for screenplay and novel projects, adapted for episodic television production.*
