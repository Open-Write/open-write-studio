# Open-Write User Manual

A guide for humans using the Open-Write creative writing system.

---

## What Open-Write Is

Open-Write is a production system for AI-assisted creative writing. It provides structured templates, automated quality checks, and a multi-stage review pipeline that helps you produce developmental-quality drafts of screenplays, novels, and TV scripts — strong raw material that you then develop, fact-check, and finish.

You don't need to be a professional writer to use Open-Write. You do need to be willing to:
- Fill out a story bible before writing begins
- Let the critic system catch problems early
- Revise iteratively based on feedback
- Stay the editor — the system drafts; you verify, shape, and finish

## What Stays Your Job

Open-Write is a tool for capable hands, not a push-button author. It collapses the slowest part of long-form writing — getting from a blank page to a complete, structured draft — but two things remain yours and don't come out of the machine finished:

- **Craft.** What you get is a developmental draft. The shaping, the deepening of thin scenes, and the final polish are human work. Treat the output as a strong starting point, not a finished manuscript.
- **Facts.** The system states detail — historical, technical, factual — with complete confidence, and is sometimes wrong. It will not flag the parts it invented. Anything you intend to rely on, you verify yourself or with someone who knows the material. In earlier runs the system confidently inverted the documented position of a real historical figure, so verification is not optional — it is the price of using the tool on anything that touches the real world.

The system also works best when its own procedure is followed, and keeping it on procedure is part of your job. Left fully alone, an autonomous run can cut corners — for example, its per-chapter critics can drift into hollow "passes" that find nothing. The completion gate exists to surface those lapses rather than hide them, but a human watching the workflow catches them sooner.

## What You'll Need

1. **An AI coding tool** — Open-Write is designed to work with tools like Kilo that support custom modes. The modes define specialized AI roles (architect, writer, critic, etc.) that each do one thing well.
2. **An AI model** — Any OpenAI-compatible model works. You'll get better results with a strong creative writing model, and the most important capacity is context — the more the model can hold, the smoother the pipeline runs.
3. **Node.js** — For the state management server (tracks character knowledge, callbacks, etc.)
4. **Python 3.x** — For export tools (PDF generation, page counting, quality audits)

## Getting Started

### Step 1: Choose Your Format

| Format | Template | Output |
|--------|----------|--------|
| Film screenplay | `screenplay_template/` | Fountain file → PDF |
| Novel | `novel_template/` | Markdown → PDF |
| TV series | `tv_template/` | Fountain files → PDFs |

Copy the template folder to your project directory. Each template is self-contained.

### Step 2: Install Dependencies

```bash
# Install the state server
cd tools/state_server
npm install

# Verify Python tools work
python tools/page_count.py --help
```

### Step 3: Build Your Story Bible

The bible is the foundation of everything. It lives in `bible/` inside your template:

| File | What You Fill In |
|------|-----------------|
| `01_concept.md` | Logline, genre, tone, themes, central question |
| `02_mythology.md` | World rules, factions, the central dilemma |
| `03_characters/` | One profile per character (use `_template.md` as starting point) |
| `04_outline.md` | Scene-by-scene (or chapter-by-chapter) outline with emotional palettes |
| `05_ending_notes.md` | How the ending should be interpreted |
| `06_craft_feeling.md` | Emotional execution standards |
| `07_format_rules.md` | Writing discipline rules |

**Take your time here.** The quality of the bible determines the quality of everything that follows. The system has a saying: "Pre-generation auditing is 10x cheaper than post-generation revision."

### Step 4: Find Your Voice

Before writing begins, run a voice experiment:
1. Define 5 candidate writing voices
2. Write the same test passage in each voice (3 runs per voice)
3. Have an adversarial reader evaluate them cold
4. Rank by the best single run (ceiling), not the average
5. Refine the top 2, lock the winner

This is documented in `skills/voice_experiment_protocol.md` inside each template.

### Step 5: Write

The writing pipeline for each scene/chapter:

```
Architect plans → Writer executes → Critics review → Cutter (conditional)
```

Each role is a separate AI mode. The architect plans without writing. The writer writes without planning. The critics review without rewriting. The cutter compresses without restructuring.

This separation is intentional — it prevents the AI from confusing its roles. It is also where the most common breakdown happens: critics can return a "pass" without doing real work. Watch for that, and let the completion gate (Step 8 below) catch what you miss.

### Step 6: Revise

After the full manuscript is assembled, run the iterative revision protocol:

1. Adversarial reader reads the manuscript cold (no bible access)
2. Reader produces coverage with specific issues
3. You address those specific issues and nothing else
4. Run the reader again
5. Repeat until improvement plateaus (diminishing returns)

**Key principle:** Each revision is targeted, not general. "Make everything better" passes cause drift. "Fix the three specific issues the reader identified" passes produce genuine improvement.

### Step 7: Export

```bash
# Screenplay → PDF
python tools/fountain_to_pdf.py script/screenplay.fountain script/screenplay.pdf

# Novel → PDF (per-chapter)
python tools/novel_chapter_export.py
```

### Step 8: Verify Completion

Before you consider a draft done, run the completion gate:

```bash
python tools/finalize.py --base-dir your_project
```

It checks every unit against disk and runs the content lints. It writes a completion certificate **only** if everything passes, and the certificate is bound to a hash of the assembled manuscript — a copied or stale one won't validate. An `INCOMPLETE` verdict is the gate working: it means something the pipeline should have done wasn't done (often hollow critics), and it is telling you the truth rather than letting it slide.

## Understanding the Critic System

The critics are the core quality mechanism. Each critic catches a different category of problem:

### Show-Don't-Tell Critic
Flags writing that tells instead of shows. Catches:
- Characters naming their emotions ("I'm terrified")
- Action lines describing what can't be seen on camera
- Interiority in action lines
- Camera directions (CUT TO, CLOSE-UP, etc.)

### Voice Critic
Checks that each character sounds like themselves. Catches:
- Generic dialogue any character could say
- Voice drift across scenes or episodes
- Characters sounding like the writer instead of a person

### Palette Critic
Verifies emotional impact. The bar is "palette lands" not just "palette present" — a scene that technically contains grief but doesn't make the reader feel it has failed.

### Continuity Critic
Tracks state across scenes. Catches:
- Characters knowing things they haven't learned yet
- Callbacks that were planted but never paid off
- Timeline inconsistencies

### Naturalism Critic
Detects AI-tell patterns. Catches:
- Em-dash overuse
- Repetitive sentence structures
- Style uniformity across characters

### Adversarial Reader
The most important critic. Reads the manuscript cold, without the bible, as a professional reader would. Produces honest coverage with a verdict. This catches everything the other critics miss because they're too close to the material.

### Cutter
Removes only material flagged by critics or editorial. Does not run by default. No target percentage.

## Character Voice

Each character should have 2-4 distinct **voice registers** — ways of speaking that emerge under different emotional conditions:

- A character's professional register sounds different from their vulnerable register
- A character's default register sounds different from their desperate register
- The richest moments are when one register is speaking and another is bleeding through

This is captured in the character profile template (`bible/03_characters/_template.md`). Fill it out for every significant character before writing begins.

## State Tracking

The system tracks four categories of state across your manuscript:

### Character Knowledge
What each character knows at each point in the story. The continuity critic checks this — if a character references something they haven't learned yet, it's flagged.

### Callbacks
Seeded items and their payoffs. Every plant must have a payoff; every payoff must have a plant. The callback ledger tracks this across the entire manuscript.

### Audience Belief
What the audience believes at each point. Essential for managing misdirection, reveals, and dramatic irony.

### Timeline
Diegetic time — when each scene happens in the story's internal clock.

These are managed through JSON state files and the MCP server.

## Tips for Best Results

1. **Invest in the bible.** The more specific your character profiles and outline, the better the output. Vague bibles produce generic writing.

2. **Run multiple models if you can.** Same-model critics share blind spots. If you have access to more than one AI model, run the critic pipeline on at least two and take the union of flagged issues. If you only have one model, the value comes from isolation — make sure each critic reads blind, in a fresh context, seeing only the chapter and its rubric. Single-model critique is weaker than a two-model pass; don't treat its sign-off as final.

3. **Trust the adversarial reader.** The reader who reads cold, without your bible, will catch things you and the other critics miss. Their feedback is the most valuable input to the revision process.

4. **Let critics flag problems.** The cutter runs only when critics or editorial identify extraneous material. It removes only what was flagged.

5. **Revise targeted, not general.** Don't tell the AI "make it better." Tell it "fix the three issues the adversarial reader identified." Targeted revisions compound; general revisions drift.

6. **Lock the voice early.** Don't keep changing the writing voice during production. Run the voice experiment, lock a voice, and stick with it. Revisions improve content, not voice.

7. **Verify the facts.** Anything historical, technical, or factual that you intend to rely on, check it yourself or with someone who knows the subject. The system will be confident whether or not it is correct.

## Adaptation Workflow

If you're adapting an existing work (e.g., a novel into a screenplay), each template includes an `adaptation_template/` directory with a 3-phase pipeline:

1. **Extract narrative DNA** — Map the source's plot structure, character arcs, themes, and emotional beats
2. **Design and test voice** — Calibrate writing voices to match the source material
3. **Draft** — Generate with iterative review

See `adaptation_template/README.md` inside each template for details.

## Troubleshooting

### The output feels generic
Your bible is probably too vague. Add specific details to character profiles — speech patterns, physical behaviors, emotional registers. Generic inputs produce generic outputs.

### Characters all sound the same
Fill out the voice register section of each character profile. Make each character's dialogue identifiable by speech patterns alone (the "cover the names" test).

### The critics aren't catching real problems
You may be running only one model. Try adding a second model and taking the union of flagged issues. Also make sure the adversarial reader is reading cold (no bible access).

### The critics passed everything, but the gate says INCOMPLETE
This is the most common autonomous-run failure, and the gate is working as intended. The per-chapter critics drifted into hollow "passes" that produced no located findings, so the gate refused to certify. Re-run the critics with the requirement that every finding be located (quoted passage + location + diagnosis), or review those chapters yourself. A green critic that found nothing is not a clean chapter — it's a critic that didn't do its job.

### The revision isn't improving
You may be doing general revisions instead of targeted ones. Read the adversarial reader's specific feedback and address only those issues. Don't try to improve everything at once.

## File Overview

```
your_project/
├── bible/              ← Story bible (you fill this in)
├── script/             ← Output files (generated by the system)
│   └── scenes/         ← Individual scene/chapter files
├── state/              ← State tracking (managed by MCP server)
├── critic_outputs/     ← Critic review notes (generated)
├── coverage_reports/   ← Adversarial reader coverage (generated)
├── tools/              ← Python tools
├── skills/             ← Craft documentation
└── .kilo/              ← AI mode configuration
```

---

*Open-Write — structured creative writing with AI-assisted quality control. The system drafts; you remain the editor.*
