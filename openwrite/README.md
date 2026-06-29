# Open-Write

A structured AI-assisted creative writing system that produces developmental-quality drafts of screenplays, novels, and TV series — a strong autonomous first draft for a human writer to develop, fact-check, and finish.

Open-Write provides reusable production templates, each containing a complete pipeline from story bible through assembled draft — including specialized critic modes, state tracking, iterative revision protocols, and export tools.

## What to Expect

Open-Write is a tool for capable hands, not a push-button author. Used well, it collapses the slowest part of long-form writing — getting from a blank page to a complete, structured draft — from weeks into about a day. What comes out is raw material to build on, and two things stay yours:

- **Craft.** The output is a developmental draft, not a finished manuscript. A human writer still does the shaping, the deepening, and the final polish.
- **Facts.** The system states detail — historical, technical, factual — with complete confidence, and is sometimes wrong. Anything you rely on, you verify yourself or with someone who knows the material. In earlier runs the system confidently inverted the documented position of a real historical figure; that is why verification is treated as non-negotiable rather than optional.

The system also works best when its own procedure is followed, and keeping it on procedure is part of what the human is for. Left entirely alone, an autonomous run can cut corners — the demo writeup in [`update_log.md`](update_log.md) walks through a concrete, documented case of where the system did and did not do what was expected. The verification tooling in this release exists to make those lapses visible rather than to hide them.

## What's Included

| Template | Format | Modes | Description |
|----------|--------|-------|-------------|
| [`screenplay_template/`](screenplay_template/) | Film screenplay (Fountain) | 13 | Complete film screenplay production pipeline |
| [`novel_template/`](novel_template/) | Novel prose (Markdown) | 14 | Novel production pipeline with dual-track support |
| [`tv_template/`](tv_template/) | TV episodic (Fountain) | 14 | TV series pipeline with writers' room simulation |

The repo also includes `demo_project/` — a complete novel produced by this public release running autonomously, shipped as an honest example of the floor (see `update_log.md` for what it did and didn't do).

Each template is self-contained: copy it to a new directory, fill in the bible files, and begin production.

## Quick Start

### Prerequisites

- **Kilo** (or another AI coding tool that supports custom modes) for the full pipeline
- **Node.js** (for the state MCP server)
- **Python 3.x** (for tools: page counting, PDF export, callback checking, etc.)

### Setup

```bash
# Install the MCP state server dependencies
cd tools/state_server
npm install
```

### Choose a Template

1. **Film screenplay** → copy `screenplay_template/` to your project directory
2. **Novel** → copy `novel_template/` to your project directory
3. **TV series** → copy `tv_template/` to your project directory

Each template has its own `README.md` with a complete step-by-step workflow.

### The Production Pipeline (All Templates)

```
Phase 1: Build the Bible
  → Fill in world-building, characters, outline, and craft documents

Phase 2: Voice Selection
  → Run voice experiments to find and lock your writing voice

Phase 3: Editorial Review (Structural Gate)
  → 3 personas review the outline
  → Structural gate: act structure, causal logic, arc completion, callbacks, character architecture

Phase 4: Writing (per unit)
  → Architect plans → Writer drafts → 5 blinded critics → Conditional cutter → Editorial → Disk verify → Resume file
  → Meta-critic every 2-3 units

Phase 5: Assembly & Export
  → Assemble, then verify assembled word count equals sum of unit files

Phase 6: Full-Manuscript Review
  → Adversarial reader reads the FULL manuscript, never a sample

Phase 7: Export to PDF

Phase 8: Completion Verification
  → verify_completion.py + finalize.py; the agent may never self-report completion
```

## The Critic System

Each template includes specialized critic modes that catch different categories of failure:

| Critic | What It Catches |
|--------|----------------|
| Show-Don't-Tell | Emotional state names, camera directions, invisible information |
| Voice | Generic dialogue, voice drift, flat characterization |
| Palette | Emotional impact failures — "palette present" vs "palette lands" |
| Continuity | Knowledge errors, callback misses, timeline breaks |
| Naturalism | AI-tell patterns, style uniformity, em-dash density |
| Adversarial Reader | Cold coverage without bible access — catches what bible-aware critics miss |
| Cutter | Conditional — removes only material flagged by critics or editorial |

**On running the critics honestly:** critics are most reliable when two *different* AI models run each critical pass — take the union of flagged issues, since same-model critics share blind spots. With a single model, the value comes from isolation: each critic reads blind, in a fresh context, seeing only the chapter and its rubric. Single-model critique still has self-recognition limits, so treat its sign-off as weaker than a two-model pass. The completion gate exists in part because per-chapter critics can degrade into hollow "passes" that find nothing — the gate flags those rather than trusting them.

## Tools

| Tool | Purpose |
|------|---------|
| `tools/word_count.py` | Canonical word counter — pipeline source of truth |
| `tools/build_manifest.py` | Generates the completion manifest from locked outline |
| `tools/verify_completion.py` | Disk-checks every manifest item; sole PASS/FAIL authority |
| `tools/finalize.py` | Runs verify + lints, writes the hash-bound completion certificate |
| `tools/lints.py` | Blocking/advisory content lints |
| `tools/lint_suite.py` | Extended per-chapter content lints |
| `tools/reader_dispatch.py` | Dispatches adversarial readers with provider provenance |
| `tools/fountain_to_pdf.py` | Fountain screenplay → industry-standard PDF |
| `tools/page_count.py` | Page count estimation |
| `tools/parenthetical_audit.py` | Parenthetical counting and classification |
| `tools/callback_check.py` | Callback ledger verification |
| `tools/ai_tell_audit.py` | AI-tell detection (em-dashes, triplets, style) |
| `tools/critic_runner.py` | Multi-model critic dispatch |
| `tools/assemble.py` | Manuscript assembly |
| `tools/state_server/` | MCP server for state management |

## State Management

The system uses an MCP (Model Context Protocol) server for structured state management across four JSON files:

- **Project state** — character knowledge, props, facts, timeline
- **Callback ledger** — seeded items and payoff tracking
- **Audience state** — what the audience believes at each point (misdirection tracking)
- **Timeline** — diegetic time tracking

Configure in `.kilo/mcp.json`.

## Key Methodologies

| Methodology | Description |
|-------------|-------------|
| Voice Experiment Protocol | Test 5 voice candidates empirically, rank by ceiling, lock the winner |
| Iterative Revision Protocol | Named strategies (Grounding, Combination, Simplification, Divergent, Coherence) driven by full-manuscript adversarial review |
| A/B Reader System | Two readers (A and B) produce independent adversarial coverage; use two different models when available |
| Completion Gate | Disk-verified manifest + hash-bound certificate; no self-reported completion |
| Editorial Review Protocol | 3 editorial personas review outline before any generation |
| Convention Tracking | Track ALL writing conventions (required and prohibited) to prevent drift |
| Dual-Voice Guidance | Making two POV voices feel like one author |

See individual template `skills/` directories for detailed documentation.

## For AI Agents

If you are an AI agent being tasked with creative writing using this system, read [`skills/start_here.md`](skills/start_here.md) first. It is the onboarding document that explains the full system architecture, pipeline, and critical rules.

## Directory Structure

```
Open-Write/
├── README.md                       ← This file
├── user_manual.md                  ← Human-friendly guide
├── update_log.md                   ← v1.1 changes + demo writeup
├── .kilo/                          ← Kilo configuration
│   └── mcp.json                    ← MCP server configuration
├── tools/                          ← Shared tools
│   ├── word_count.py               ← Canonical word counter
│   ├── build_manifest.py
│   ├── verify_completion.py
│   ├── finalize.py
│   ├── lints.py
│   ├── lint_suite.py
│   ├── reader_dispatch.py
│   ├── assemble.py
│   ├── fountain_to_pdf.py
│   ├── critic_runner.py
│   ├── page_count.py
│   ├── parenthetical_audit.py
│   ├── callback_check.py
│   ├── ai_tell_audit.py
│   └── state_server/               ← MCP state server
├── skills/                         ← Cross-template skills
│   └── start_here.md               ← AI agent onboarding
├── demo_project/                   ← Autonomous demo novel (see update_log.md)
├── screenplay_template/            ← Film screenplay template
├── novel_template/                 ← Novel prose template
└── tv_template/                    ← TV episodic template
```

## License

Apache 2.0

## Acknowledgments

Open-Write was developed through the production of multiple complete creative works. The methodologies, critic architecture, and revision protocols were refined against real-world production use.
