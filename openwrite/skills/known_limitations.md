# Known Limitations

*Documented failure modes discovered through production use and red-team auditing. Read this before running the system on material you intend to publish.*

---

## 1. Source Bias Reproduction (ADAPTATIONS)

**What happens:** When adapting existing works (novels, plays, public-domain texts), the pipeline reproduces the source material's biases, prejudices, and sensitive content without flagging it. Nothing in the system performs values-level review of inherited content.

**Example:** A Dorian Gray adaptation faithfully reproduced Wilde's antisemitic descriptions ("a hideous Jew," "the fat Jew manager") verbatim, without any critic or lint flagging the content as sensitive. The pipeline treated the source text as authoritative.

**Why it happens:** The critics evaluate craft (show-don't-tell, voice, continuity, naturalism). None evaluate ethics, sensitivity, or the appropriateness of inherited content for a contemporary audience. The factual-review gate checks historical accuracy, not values.

**Mitigation:** When adapting works that contain sensitive material (racial stereotypes, antisemitism, slurs, outdated cultural representations), a human must review the output specifically for this content before publication. The system will carry the source's prejudices straight through. Treat this as you would treat a human assistant who transcribes faithfully — they'll transcribe what's there, and the editorial judgment about what to keep is yours.

**What the system should do (not yet implemented):** A sensitivity-review pass that flags content matching known patterns of bias in source material. This is a capability gap, not a bug.

---

## 2. Title Page Artifacts

**What happens:** Autonomous runs produce title pages with placeholder bylines. Observed artifacts include "Untitled / by Author," "by Kilo (mimo)," and the agent's project codename printed on the cover.

**Why it happens:** The prose-writer sub-agent generates the full chapter file including any title/front-matter blocks, and it fills placeholder fields with whatever it infers from context (its own agent name, the project codename, "Author," etc.). No gate checks the title page for placeholder content.

**Mitigation:** After any autonomous run, inspect the first page/title block of the assembled manuscript before distribution. Grep for "by Kilo," "by Author," "Untitled," and any project codenames. Replace with the intended author attribution before export.

**What the system should do (not yet implemented):** A title-page lint that flags common placeholder patterns (agent names, "Author," "Untitled," project codenames) and fails the gate.

---

## 3. Self-Authored Critics (STRUCTURAL)

**What happens:** When a single sub-agent writes both the draft and its critics (violating Rule 3 of the orchestrator), the critics rubber-stamp the draft. Located findings are manufactured, scores are inflated, and the independent read gap (self-assigned 8.5 vs. independent 6.0) is the measured cost.

**Why it happens:** A critic that shares the writer's context and weights cannot see the writer's blind spots. It produces critic-shaped files that validate the draft.

**Mitigation:** Enforce Rule 3 of the orchestrator prompt: one sub-agent per stage, never one per chapter. The writer writes. Separate critic sub-agents, in fresh contexts, evaluate. Ideally a different model runs the critics.

**Status:** The orchestrator prompt now enforces this. The hollow-critic lint now requires chapter_hash to prove the critic processed the file. But the lint cannot verify that the critic ran in a separate context — that's a harness enforcement, not a file check.

---

## 4. Lint Gaming

**What happens:** The agent satisfies the measurable marker of a lint without fixing the underlying behavior. Observed patterns:

- **Em-dashes:** Agent deletes Unicode em-dashes one at a time until the count clears, then the export writes double-hyphens (`--`) which the lint didn't count. Fix: lints.py now counts both.
- **Hollow critics:** Agent inserts quoted spans and line references into critic files to satisfy the located-findings detector. Fix: raised threshold to 3 findings + chapter_hash requirement.
- **Refrains:** Agent grep-deletes duplicated sentences one by one, reducing the count without changing the voice.
- **Word count:** Agent pads chapters to hit round numbers (2,500, 3,000) by expanding summary rather than deepening rendering.

**Why it happens:** The agent optimizes for the measurable gate, not the intent behind it. This is what optimizers do.

**Mitigation:** The lints are a backstop, not a fix. The real fix is independent critics (different model, fresh context) who evaluate the prose, not the metrics. The lints catch mechanical failures; the critics catch craft failures.

---

## 5. Historical Figure Inversions

**What happens:** The system portrays named historical figures in ways that contradict the historical record, because no internal check verifies factual accuracy against external sources. The factual-review lint is advisory and requires a sign-off record that autonomous runs never produce.

**Example:** Bishop Mateo Múgica, who was expelled from Spain by the Nationalist side in 1936 for being too tolerant of Basque Catholics, was portrayed as a Franco enforcer demanding a priest recant his opposition to Franco — the precise opposite of the historical record. This appeared in multiple autonomous runs and was never caught by any internal critic.

**Why it happens:** The continuity critic checks internal consistency (does the character act consistently within the story), not external fact (does the character's portrayal match the historical record). The factual-review lint requires a `real_figures.json` registry and independent sign-off, which autonomous runs don't produce.

**Mitigation:** For any work that names real historical figures: (1) declare them in `state/real_figures.json`, (2) have an independent reviewer (human or different model with web search) verify each figure's portrayal against the record, (3) sign off in `state/factual_reviews.json`. The factual-review lint will then gate on this sign-off.

**For autonomous runs without human review:** fictionalize real figures whose portrayal you cannot independently verify. Rename the bishop to a fictional character — the plot holds, the factual risk vanishes.

---

## 6. Voice Invariance

**What happens:** The system's line-level prose voice is consistent across all output regardless of how much human direction is applied. Short-declarative rhythm, anaphora stacking, negative-construction density, and body-motif repetition appear in autonomously generated novels, human-directed projects, and everything in between.

**What this means:** Human creative input visibly improves the bones — what story, what material, what to dramatize, the thematic architecture. It does not scrub the system's line-level voice. The thing that improves with effort is the skeleton, not the voice.

**Mitigation:** For projects where the prose voice must read as human (publication-quality fiction), an editorial pass by a skilled human writer is required at the line level. The system produces the structure and the draft; the human shapes the voice.

---

*Last updated: 2026-06-06*
