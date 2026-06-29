# Start Here — Onboarding for AI Agents

*Read this file first when assigned a creative writing task using Open-Write. It contains everything you need to orient yourself before doing any work.*

---

## What Is Open-Write?

Open-Write is a structured creative writing system with three self-contained templates:

| Template | Format | Location |
|----------|--------|----------|
| Screenplay | Film screenplay (Fountain → PDF) | `screenplay_template/` |
| Novel | Prose (Markdown → PDF) | `novel_template/` |
| TV Series | Episodic (Fountain → PDF) | `tv_template/` |

Each template contains its own bible templates, modes, rules, skills, tools, and state files. A bot with access to only one template directory should have everything it needs to produce a complete work.

---

## Before You Do Anything

1. **Determine which template** you're working with (screenplay, novel, or TV).
2. **Read the template's `skills/start_here.md`** — the template-specific onboarding guide.
3. **Read the template's `skills/*_craft.md`** — learn the voice and format rules.
4. **Read the template's `skills/critic_architecture.md`** — understand the review system.

---

## The Production Pipeline

All three templates follow the same high-level pipeline:

```
Phase 1: Build the Bible
  → Fill in world-building, characters, outline, and craft documents
  → Review bible/07_format_rules.md (the discipline document)

Phase 2: Voice Selection
  → Run voice experiments per skills/voice_experiment_protocol.md
  → Lock a voice specification

Phase 3: Editorial Review (Structural Gate)
  → 3 personas review outline per skills/editorial_review_protocol.md
  → Structural gate check: act structure, causal logic, arc completion, callbacks, character architecture
  → Iterate until all return positive verdicts AND pass structural gate
  → Lock the outline

Phase 4: Writing (one unit per session)
  → For each scene/chapter/episode:
    - Architect plans (with character architecture depth — strictest gate)
    - Plan must exist on disk before writer runs
    - Writer executes
    - ALL critics review (show, voice, palette, continuity, naturalism — every unit, no exceptions)
    - Cutter (conditional — only if critics flag material)
    - Editorial evaluates (structural assessment + prose review)
    - Verify on disk: all files exist, stub-detector floor passed
    - Write resume file for next session
  → After every 2-3 chapters:
    - Meta-critic reviews all critic outputs for the batch
    - Produces refinement notes for subsequent critics (feedback loop)
    - Named revision strategies (Grounding, Combination, Simplification, Divergent, Coherence)

Phase 5: Assembly & Audit
  → Assemble via Python tools (cross-platform, artifact-stripping)
  → Verify assembled word count equals sum of unit files
  → Run quality tools (page count, parenthetical audit, callback check)

Phase 6: Full-Manuscript Review (never a sample)
  → Adversarial reader reads FULL assembled manuscript/season (chunked if necessary)
  → Score reflects entire work, not a subset
  → Each iteration addresses specific issues identified by the reader
  → Stop when diminishing returns are confirmed

Phase 7: Export
  → Export to PDF via tools/fountain_to_pdf.py or tools/novel_chapter_export.py

Phase 8: Completion Verification
  → Run verify_completion.py against the manifest
  → Only a PASS verdict certifies the workflow as complete
  → The agent must never report success over a failing manifest
```

---

## Completion Manifest

Every autonomous workflow carries an explicit, machine-verifiable checklist of required outputs:

1. **At run start**: Once scope is locked (chapter/scene/episode count known), build `state/completion_manifest.json` from the template's `skills/definition_of_done.md`. Define "done" before the work begins.
2. **During the run**: A unit or phase counts as done only when its manifest items pass.
3. **At run end**: Run `python tools/verify_completion.py`. Only its PASS output may certify the workflow as complete. On FAIL, report INCOMPLETE with the exact failing items.
4. **The final summary must embed the verification tool's raw output.**

The system that does the work must not be the system that grades whether the work was done. A passing manifest certifies completeness and integrity — not quality.

---

## Cardinal Rules

1. **Every unit gets identical, full rigor.** No batch mode, no fast path, no abbreviation. Chapter/scene/episode 15 gets exactly what unit 1 gets.
2. **No self-reported completion.** A unit is complete only when verified files exist on disk. Word counts come from `word_count.py` (measured), never from memory.
3. **"Reduce context" = reset-and-continue at full rigor.** Write a resume file, stop, next session resumes fresh. Never abbreviate.
4. **Full-manuscript reviews read everything.** The adversarial reader and final editorial pass must cover the entire assembled manuscript. If context can't hold it, read in sequential chunks and aggregate findings. No sampling.
5. **The format rules are sacred.** No camera directions, no emotional parentheticals, no interiority in action lines, no adverbs in dialogue tags. Read `bible/07_format_rules.md` before writing anything.
6. **Never modify state files directly.** Use the MCP server or tools for state changes.
7. **The voice is locked.** Once selected, the voice does not change. Iterations improve content, not voice.
8. **Each revision is targeted, not general.** Address specific issues. Do not "make everything better."
9. **Structural issues route to outline/bible.** Character issues route to character profiles. Never patch structural problems at prose level.
10. **Characters have voice registers.** Each character has 2-4 distinct ways of speaking under different emotional conditions. Voice register names must never appear in the manuscript itself.
11. **The completion manifest is law.** Only `verify_completion.py` returning PASS may certify a workflow as complete. Never report success over a failing manifest.

---

## The Critic System

Each template has specialized critic modes that catch different categories of failure:

| Mode | What It Does |
|------|-------------|
| Book Runner / Showrunner | Orchestrates the full pipeline with verification gates |
| Architect | Plans units — strictest quality gate, must exist on disk |
| Writer | Executes the plan in the output format |
| critic-show | Show-don't-tell enforcement |
| critic-voice | Per-character voice consistency review |
| critic-palette | Emotional palette verification |
| critic-continuity | State/timeline/callback review with deep verification (assumption decomposition) |
| critic-naturalism | AI-tell detection: em-dash overuse, triplet closings, style uniformity |
| critic-meta | Cross-chapter review synthesis — reviews the critics, identifies patterns and blind spots |
| cutter | Conditional — removes only material flagged by critics or editorial |
| editorial-eval | Editorial panel with structural assessment |
| adversarial-reader | Cold coverage — must read FULL manuscript (never a sample) |
| rewrite-prepper | Produces rewrite preparation documents for human rewriters |

**Run at least 2 AI models on every critical pass.** Same-model critics have self-recognition bias. Take the union of flagged issues, not the intersection.

---

## Voice Registers

Characters speak differently under different emotional conditions. Each character has 2-4 voice registers:

- A character's professional register sounds different from their vulnerable register
- A character's default register sounds different from their desperate register
- The richest moments are when one register is speaking and another is bleeding through

Voice register names must **never** appear in the manuscript itself. They are the writer's understanding, not the content. "Her spine straightens. Her voice flattens." is allowed. "The Analyst takes over." is forbidden.

---

## State Management

The system uses an MCP server for structured state management. The state files track:

- **Character knowledge** — what each character knows at each point
- **Callbacks** — seeded items and payoff tracking
- **Audience state** — what the audience believes (misdirection tracking)
- **Timeline** — diegetic time for all scenes
- **Convention ledger** — writing convention tracking
- **Resume files** — session handoff state for clean context resets

Configure in `.kilo/mcp.json`. Never edit state files directly — use the MCP server or the tools.

### MCP Tool Groups (v1.1.1)

The MCP server supports context-aware tool exposure. Filter tools by group to reduce attention dilution:

```bash
# Only expose callback tools during callback management
node tools/state_server/index.js --groups=callbacks

# Debug tool calls with inspector mode
node tools/state_server/index.js --inspector
```

See [`skills/mcp_debugging.md`](mcp_debugging.md) for full debugging documentation.

---

## Key Methodologies

| Methodology | Description | When to Use |
|-------------|-------------|-------------|
| Voice Experiment Protocol | Test 5 voices, Elo pairwise tournament, lock winner | Before writing begins |
| A/B Reader System | Two models (Reader A + Reader B) produce independent adversarial coverage — prevents self-recognition bias | Full-manuscript review |
| Iterative Revision Protocol | Targeted revisions with named strategies (Grounding, Combination, Simplification, Divergent, Coherence) | After full draft |
| Meta-Critic Protocol | Cross-chapter/episode review synthesis — critics learn from patterns | After every 2-3 chapters/episodes |
| Editorial Review Protocol | 3 personas + structural gate review outline before generation | Before writing begins |
| Convention Tracking | Track ALL writing conventions to prevent drift | During writing |
| One Unit Per Session | Each chapter/scene/episode in its own context with resume handoff | During writing |
| Known Limitations | [`known_limitations.md`](known_limitations.md) | Read before publishing — documented failure modes |
| MCP Debugging | [`skills/mcp_debugging.md`](mcp_debugging.md) | When MCP tool calls fail or hallucinate parameters |

---

## Tools Reference

| Tool | Purpose | Command |
|------|---------|---------|
| `tools/word_count.py` | Verified word count — pipeline source of truth | `python tools/word_count.py` |
| `tools/assemble.py` | Assemble screenplay scenes (strips artifacts) | `python tools/assemble.py --title "Title"` |
| `tools/fountain_to_pdf.py` | Fountain → PDF | `python tools/fountain_to_pdf.py input.fountain output.pdf` |
| `tools/page_count.py` | Page count estimation | `python tools/page_count.py` |
| `tools/parenthetical_audit.py` | Parenthetical audit | `python tools/parenthetical_audit.py` |
| `tools/callback_check.py` | Callback verification | `python tools/callback_check.py` |
| `tools/ai_tell_audit.py` | AI-tell detection | `python tools/ai_tell_audit.py <scene>` |
| `tools/critic_runner.py` | Multi-model critic dispatch | `python tools/critic_runner.py --scene 1 --critic show` |

**Note:** Set `PYTHONIOENCODING=utf-8` before running Python tools on Windows.

---

## Environment Detection

Before using commands, check your environment:

- **Windows PowerShell:** See `skills/windows_powershell_guide.md` (inside templates)
- **Bash (Unix/Linux/Mac):** Use standard bash commands
- **If tools fail:** See `skills/tool_limitation_workarounds.md` (inside templates)

---

## If You're Stuck

- Re-read the template's craft file for guidance
- Re-read `bible/07_format_rules.md` for format discipline
- Check the tools — they can tell you the current state
- Ask the human creator before making assumptions about creative direction
