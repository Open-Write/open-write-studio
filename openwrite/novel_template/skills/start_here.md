# Start Here — Novel Production Onboarding

*Read this file first when starting a novel project. It contains everything you need to orient yourself before doing any work.*

*This template provides a complete novel production system with proven methodologies for voice selection, iterative revision, and cross-model quality control.*

---

## What Is This Template?

This is a self-contained novel production system. It provides:

- **Bible templates** (`bible/`) — thematic frame, world-building, character profiles, chapter outline, craft guidance, prose discipline
- **State tracking** (`state/`) — chapter outline, callback ledger, convention ledger, resume files
- **Python tools** (`tools/`) — word count, prose audit, callback check, convention scan, assembly, export, track balance
- **Skills files** (`skills/`) — craft guidance, critic architecture, voice experiment protocol, editorial review, iterative revision, convention tracking, PDF export

A bot with access to only this directory should have everything it needs to produce a complete novel.

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
2. **Read [`novel_craft.md`](novel_craft.md)** — understand prose craft principles.
3. **Read [`critic_architecture.md`](critic_architecture.md)** — understand the multi-mode production system.
4. **Read [`voice_experiment_protocol.md`](voice_experiment_protocol.md)** — understand how to select and lock a writing voice.

---

## The Workflow (High Level)

```
1. Fill the Bible
   → 01_concept.md, 02_mythology.md, 03_characters/, 04_outline.md,
     05_ending_notes.md, 06_craft_feeling.md, 07_format_rules.md

2. Select a Voice
   → voice_experiment_protocol.md
   → 5 candidates × 3 runs → Elo pairwise tournament → refine top 2 → lock winner

3. Editorial Review
   → editorial_review_protocol.md
   → 3 personas review outline → structural gate check → iterate → lock

4. Write the Novel (one chapter per session)
   → For each chapter:
     - Architect plans (bible N±2, characters, state files, character architecture depth)
     - Prose-writer executes
     - 5 critics (show-don't-tell, voice, palette, continuity with deep verification, naturalism)
      - Cutter (conditional — only when critics flag material)
     - Editorial evaluation (structural assessment + prose review)
      - Verify (disk check: all files exist, stub-detector floor passed)
     - Write resume file for next session
   → After every 2-3 chapters:
     - Meta-critic reviews critic outputs → produces refinement notes for next batch

5. Revise
   → iterative_revision_protocol.md
   → Adversarial reader reads FULL assembled manuscript (never a sample)
   → Targeted iterations driven by adversarial reader findings

6. Export
   → tools/assemble.py → tools/export_formats.py

7. Completion Verification
   → Run `python tools/verify_completion.py` against the manifest
   → Only PASS certifies the workflow as complete
```

---

## Cardinal Rules

1. **Every chapter gets identical, full rigor.** No batch mode, no fast path, no abbreviation.
2. **No self-reported completion.** Files must exist on disk. Word counts from `word_count.py`.
3. **"Reduce context" = reset-and-continue at full rigor.** Write a resume file, stop, next session resumes fresh.
4. **Full-manuscript reviews read everything.** No sampling, no "key chapters."
5. **The prose discipline document is sacred.** Reload [`bible/07_format_rules.md`](../bible/07_format_rules.md) before every chapter. Without it, the prose swells.
6. **Never modify state files directly.** Use the tools or the state MCP server to prevent schema corruption.
7. **The voice is locked before writing begins.** Do not start prose generation until the voice experiment is complete and the voice spec is locked.
8. **Each revision iteration is targeted, not general.** The adversarial reader identifies specific issues; the revision addresses those issues and nothing else.
9. **Structural issues route to outline/bible.** Character issues route to character profiles. Never patch structural problems at prose level.
10. **The completion manifest is law.** Only `verify_completion.py` returning PASS may certify the workflow as complete. Never report success over a failing manifest.

---

## The Production Modes

| Mode | Purpose |
|------|---------|
| book-runner | Orchestrates the full pipeline: plan → write → critique → cut → evaluate → verify |
| architect | Plans chapters with character architecture depth (strictest gate) |
| prose-writer | Executes the architect's plan |
| critic-show | Show-don't-tell enforcement |
| critic-voice | Per-character voice consistency review |
| critic-palette | Emotional palette verification |
| critic-continuity | State/timeline/callback review with deep verification |
| critic-naturalism | AI-tell detection and naturalism review |
| critic-meta | Cross-chapter review synthesis — reviews the critics, identifies patterns and blind spots |
| cutter | Conditional — removes only material flagged by critics or editorial |
| editorial-eval | Editorial panel evaluation with structural assessment |
| adversarial-reader | Cold coverage — must read FULL manuscript |
| adversarial-reader-quantitative | Quantitative coverage with dimensional scores |
| rewrite-prepper | Produces rewrite preparation documents for human rewriters |

See [`critic_architecture.md`](critic_architecture.md) for full details.

---

## Key Methodologies

| Methodology | Skills File | When to Use |
|-------------|-------------|-------------|
| Voice Experiment Protocol | [`voice_experiment_protocol.md`](voice_experiment_protocol.md) | When testing/selecting a writing voice (Elo-based pairwise tournament) |
| Iterative Revision Protocol | [`iterative_revision_protocol.md`](iterative_revision_protocol.md) | When revising a completed draft (named strategies: Grounding, Combination, Simplification, Divergent, Coherence) |
| Meta-Critic Protocol | [`meta_critic_protocol.md`](meta_critic_protocol.md) | After every 2-3 chapters — cross-chapter review synthesis |
| Editorial Review Protocol | [`editorial_review_protocol.md`](editorial_review_protocol.md) | When reviewing an outline before generation |
| Convention Tracking | [`convention_tracking.md`](convention_tracking.md) | When tracking writing conventions across a project |
| Novel Craft | [`novel_craft.md`](novel_craft.md) | When writing or revising prose |
| PDF Export | [`pdf_export.md`](pdf_export.md) | When exporting novels to PDF |
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
| Word count | `python tools/word_count.py` | Verified word count by chapter — pipeline source of truth |
| Prose audit | `python tools/prose_audit.py` | Detect AI tics and prose violations |
| Callback check | `python tools/callback_check.py` | Check callback ledger status |
| Convention scan | `python tools/convention_scan.py` | Scan manuscript for convention patterns |
| Assemble | `python tools/assemble.py --title "Title" --author "Author"` | Assemble chapters into full manuscript (strips artifacts, verifies counts) |
| Verify | `python tools/assemble.py --verify` | Verify all chapters pass stub-detector floor |
| Export formats | `python tools/export_formats.py` | Export to TXT and PDF |
| Chapter export | `python tools/novel_chapter_export.py` | Export per-chapter PDFs |
| Cumulative summaries | `python tools/build_cumulative_summaries.py` | Build cumulative chapter summaries |
| Track balance | `python tools/track_balance.py` | Check Track A/B/interlude ratios |
| Verify completion | `python tools/verify_completion.py` | Verify manifest — only PASS certifies done |

**Note:** Always set `PYTHONIOENCODING=utf-8` before running tools.

---

## The Bible Files

| File | Purpose | When to Load |
|------|---------|--------------|
| [`bible/01_concept.md`](../bible/01_concept.md) | Thematic frame, logline, central question | Before planning any chapter |
| [`bible/02_mythology.md`](../bible/02_mythology.md) | World-building, fictional rules | When writing scenes in the world |
| [`bible/03_characters/`](../bible/03_characters/) | Character profiles (voice registers, motivation, contradiction, blind spot) | For every scene with that character |
| [`bible/04_outline.md`](../bible/04_outline.md) | Chapter outline with emotional palettes | For every chapter (N±2) |
| [`bible/05_ending_notes.md`](../bible/05_ending_notes.md) | Ending interpretation guidance | When writing the final act |
| [`bible/06_craft_feeling.md`](../bible/06_craft_feeling.md) | Emotional execution standards | For every chapter |
| [`bible/07_format_rules.md`](../bible/07_format_rules.md) | Prose discipline, AI tic scrub list | **RELOAD BEFORE EVERY CHAPTER** |

---

## Session Management

### Starting a New Chapter
1. Load the latest resume file from `state/resume_chapter_N.json`
2. Load only what the next chapter needs: N±2 outline, active characters, format rules, voice spec, prior chapter tail
3. Run the full pipeline at full rigor

### Ending a Chapter
1. Verify all output files exist on disk
2. Write `state/resume_chapter_N.json` with current position, callback/convention state, prior chapter tail, next chapter target
3. Do NOT carry manuscript context into the next session

---

## If You're Stuck

- Re-read the relevant skills file for your current task
- Check the tools — `prose_audit.py` and `convention_scan.py` catch issues you're too close to see
- Run the adversarial reader — cold coverage reveals what bible-aware review misses
- When in doubt: make it more specific, more physical, more this-character, this-moment

---
