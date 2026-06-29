# Start Here — Onboarding for New Bots

*Read this file first when assigned a task in a screenplay project. It contains everything you need to orient yourself before doing any work.*

---

## What Is This Template?

This is a self-contained screenplay production template. It provides:

- **Bible templates** for world-building, characters, and story structure
- **Skills files** with methodology, craft guidance, and revision protocols
- **Tools** for page counting, parenthetical auditing, callback tracking, and PDF export
- **State files** for tracking callbacks, audience knowledge, and writing conventions
- **Reference files** for voice consistency

The template was validated through production use — a produced screenplay achieved RECOMMEND from a professional contest reader after 5 iterative revisions using the Silence Architecture voice.

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

1. **Read this file** (`skills/start_here.md`) — understand the system.
2. **Read [`skills/screenplay_craft.md`](screenplay_craft.md)** — learn the Silence Architecture voice, format rules, and craft principles.
3. **Read [`skills/critic_architecture.md`](critic_architecture.md)** — understand the 12-mode review system (includes meta-critic).
4. **Read [`bible/07_format_rules.md`](../bible/07_format_rules.md)** — the discipline document. Reload for every scene.

---

## The Production Pipeline

```
Phase 1: Bible Creation
  → Fill bible/01_concept.md through bible/06_craft_feeling.md
  → Review bible/07_format_rules.md (discipline document)

Phase 2: Voice Selection
  → Run voice experiments per skills/voice_experiment_protocol.md
  → Lock a voice specification

Phase 3: Editorial Review
  → 3 personas review the outline per skills/editorial_review_protocol.md
  → Iterate until all return positive verdicts
  → Lock the outline

Phase 4: Scene Writing
  → For each scene: architect plans → screenwriter executes → critics review → cutter compresses
  → Load format rules for every scene
  → Load character profiles for characters in the scene
  → Load the voice card for the scene's POV voice
  → After every 5-8 scenes: meta-critic reviews critic outputs → produces refinement notes

Phase 5: Assembly & Audit
  → python tools/assemble_screenplay.py
  → python tools/page_count.py
  → python tools/parenthetical_audit.py
  → python tools/callback_check.py

Phase 6: Iterative Revision (5 iterations)
  → Adversarial reader (Lara Marsh) reads cold
  → Each iteration addresses specific issues identified by the reader
  → Stop when verdict reaches target level

Phase 7: Export
  → python tools/fountain_to_pdf.py script/screenplay.fountain script/screenplay.pdf

Phase 8: Completion Verification
  → Run `python tools/verify_completion.py` against the manifest
  → Only PASS certifies the workflow as complete
```

---

## Critical Rules

1. **The format rules are sacred.** No camera directions, no emotional parentheticals, no interiority in action lines, no adverbs in dialogue tags. Read [`bible/07_format_rules.md`](../bible/07_format_rules.md) before writing anything.
2. **Never modify state files directly.** Use the tools or the MCP server for state changes.
3. **Track what you learn.** Log issues and insights.
4. **The voice is locked.** Once selected, the voice does not change. Iterations improve content, not voice.
5. **Each iteration is targeted, not general.** Address specific issues identified by the adversarial reader. Do not "make everything better."
6. **The completion manifest is law.** Only `verify_completion.py` returning PASS may certify the workflow as complete. Never report success over a failing manifest.

---

## The 12-Mode Production System

| Mode | Purpose | Output |
|------|---------|--------|
| architect | Plans scenes before they are written | `critic_outputs/scene_N_plan.md` |
| screenwriter | Executes the plan in Fountain markup | `script/scenes/N_*.fountain` |
| critic-show | Show-don't-tell enforcement | `critic_outputs/scene_N_show_dont_tell.md` |
| critic-voice | Per-character voice consistency review | `critic_outputs/scene_N_voice_{character}.md` |
| critic-palette | Emotional palette verification | `critic_outputs/scene_N_palette.md` |
| critic-continuity | State/timeline/callback review with deep verification | `critic_outputs/scene_N_continuity.md` |
| critic-naturalism | AI-tell detection and naturalism review | `critic_outputs/scene_N_naturalism.md` |
| critic-meta | Cross-scene review synthesis — reviews the critics | `coverage_reports/meta_review_scenes[N-M].md` |
| cutter | Conditional — removes only flagged material | Overwrites scene file + `critic_outputs/scene_N_cuts.md` (only when cutter runs) |
| adversarial-reader | Cold coverage without bible access | `coverage_reports/` |
| adversarial-reader-quantitative | Quantitative coverage with scores | `coverage_reports/` |
| rewrite-prepper | Produces rewrite preparation documents for human rewriters | `critic_outputs/scene_N_rewrite_prep.md` |

---

## Key Methodologies

| Methodology | Skills File | When to Use |
|-------------|-------------|-------------|
| Voice Experiment Protocol | [`skills/voice_experiment_protocol.md`](voice_experiment_protocol.md) | When testing/selecting a writing voice (Elo-based pairwise tournament) |
| Iterative Revision Protocol | [`skills/iterative_revision_protocol.md`](iterative_revision_protocol.md) | When revising a completed draft (named strategies: Grounding, Combination, Simplification, Divergent, Coherence) |
| Meta-Critic Protocol | [`skills/meta_critic_protocol.md`](meta_critic_protocol.md) | After every 5-8 scenes — cross-scene review synthesis |
| Editorial Review Protocol | [`skills/editorial_review_protocol.md`](editorial_review_protocol.md) | When reviewing an outline before generation |
| Dual-Voice Guidance | [`skills/dual_voice_guidance.md`](dual_voice_guidance.md) | When managing two POV voices in one work |
| Convention Tracking | [`skills/convention_tracking.md`](convention_tracking.md) | When tracking writing conventions across a project |
| PDF Export | [`skills/pdf_export.md`](pdf_export.md) | When exporting screenplays to PDF |
| Screenplay Craft | [`skills/screenplay_craft.md`](screenplay_craft.md) | When writing or revising screenplays |
| Critic Architecture | [`skills/critic_architecture.md`](critic_architecture.md) | When running the review system (includes review system documentation) |
| Windows PowerShell Guide | [`skills/windows_powershell_guide.md`](windows_powershell_guide.md) | When working on Windows PowerShell |
| WSL/Git Bash Setup | [`skills/wsl_git_bash_setup.md`](wsl_git_bash_setup.md) | When using WSL or Git Bash on Windows |
| Large File Operations | [`skills/large_file_operations.md`](large_file_operations.md) | When working with files over 1,000 lines |
| Tool Limitation Workarounds | [`skills/tool_limitation_workarounds.md`](tool_limitation_workarounds.md) | When tools fail or are unavailable |
| Known Limitations | [`skills/known_limitations.md`](known_limitations.md) | Read before publishing — documented failure modes |
| MCP Debugging | [`skills/mcp_debugging.md`](mcp_debugging.md) | When MCP tool calls fail or hallucinate parameters |

---

## The Silence Architecture Voice

The dominant voice pattern for this template. Meaning lives in what characters DON'T say.

- Characters speak only when they must. Silence carries meaning.
- Action lines render the gaps — what characters don't say, don't do, don't acknowledge.
- White space is structural. A single line alone on the page is a deliberate choice.
- Body anchors: hands, eyes, breath, spine, jaw — physical grounding in every scene.
- 8 lines of dialogue where another voice would use 20.

This voice was validated by achieving RECOMMEND from Lara Marsh after 5 iterative revisions. It is the default voice for the template.

Full spec: [`skills/screenplay_craft.md`](screenplay_craft.md) (see "The Silence Architecture Voice" section).

---

## The Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `tools/page_count.py` | Page count estimation | `python tools/page_count.py` |
| `tools/parenthetical_audit.py` | Parenthetical counting/classification | `python tools/parenthetical_audit.py` |
| `tools/callback_check.py` | Callback verification | `python tools/callback_check.py` |
| `tools/fountain_to_pdf.py` | Fountain → PDF conversion | `python tools/fountain_to_pdf.py input.fountain output.pdf` |
| `tools/assemble_screenplay.py` | Scene assembly | `python tools/assemble_screenplay.py` |
| `tools/convention_scan.py` | Convention pattern scanning | `python tools/convention_scan.py` |
| `tools/verify_completion.py` | Verify manifest — only PASS certifies done | `python tools/verify_completion.py` |

---

## If You're Stuck

- Re-read [`skills/screenplay_craft.md`](screenplay_craft.md) for craft guidance
- Re-read [`bible/07_format_rules.md`](../bible/07_format_rules.md) for format discipline
- Check the tools — they can tell you the current state of the script
- Ask the human creator before making assumptions about creative direction
