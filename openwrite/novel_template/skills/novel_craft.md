# Novel Craft — Prose Writing Principles

*Distilled craft knowledge from novel production. Transferable to any literary prose project.*

*This file replaces the screenplay_craft.md from the screenplay template. The original focused on screenplay format rules; this version focuses on prose-specific craft.*

---

## The Discipline Document

The single most important file in any novel project is `bible/07_format_rules.md`. It is reloaded every chapter. Without it, the prose swells. The key rules:

1. **Scene vs. summary.** 70%+ of each chapter should be scene (rendered moments with sensory detail, action, dialogue, interiority). Summary earns its place only by compressing what scene would belabor.
2. **Prose distance modulation.** Every chapter must vary between extreme close-up, middle distance, and compressed lyric distance. Five consecutive paragraphs at the same distance = flat prose.
3. **AI tic scrub list.** Tier 1 (banned): "Not X but Y," "The particular X of Y," hedge words, existential expletives, telling interiority. Tier 2 (flag): em-dash overuse, adverbs in dialogue tags, "something between X and Y."
4. **Interiority must do work.** Never "she felt grief." Instead: "The kitchen had not changed since the morning Sofia stopped wanting toast." Interiority must be specific to character, specific to moment, and must not name the emotion.
5. **Dialogue is subtext, not statement.** Characters do not name their emotional states. If a line says "I am terrified," rewrite until the character is talking about something else.
6. **Dialogue differentiation is mandatory.** Each character must sound distinct. Mira speaks in fragments when under stress. Daniel speaks in complete sentences. Theo sounds like a too-smart teenager reaching for language that's slightly too large.

## The Rendering Spectrum

The central craft principle for prose interiority:

| Level | Example | Quality |
|-------|---------|---------|
| Named emotion | *She felt grief.* | Bad. Cut or replace. |
| Named emotion with qualifier | *She felt a familiar grief.* | Still bad. |
| Physical symptom | *Her chest tightened.* | Better, but generic. |
| Specific physical detail | *She set the cup down harder than she meant to.* | Good. Behavioral, specific. |
| Rendered consciousness | *The kitchen had not changed since the morning Sofia stopped wanting toast.* | Best. Interiority as perception. |

Aim for levels 4 and 5. Level 3 is acceptable in moderation. Levels 1 and 2 are failures.

## The Body-Anchor Technique

Ground abstract emotion in physical sensation. This bridges POV voices and reader identification because bodies are universal.

**Primary anchors:** hands, eyes, breath, spine, jaw, feet, shoulders, knees.

**The discipline:** Check the convention ledger before each chapter. If hands appeared in the last 3 chapters, use eyes or breath. The most dangerous repetition is the repetition of permitted constructions.

**The test:** If every emotional beat in the novel uses hands, the reader notices. Diversify.

## The Conditional Cutter

First drafts always over-describe. The compression pass produces better work. Apply it mechanically:

- If a sentence doesn't earn its place, cut it
- If two sentences say the same thing, cut one
- If an adverb modifies a verb that already carries the meaning, cut the adverb
- White space is your friend. A single sentence alone on its line is often the right choice.

The cutter runs only when critics or editorial flag extraneous material — there is no default reduction pass and no target percentage. Chapter length follows the scene and the outline beat. Prose earns its length through quality, not brevity. If nothing was flagged, the cutter does not run.

## Scene Completeness (Not Length Quotas)

Chapter length is not a quality proxy. A 1,200-word chapter that renders every beat is better than a 3,000-word chapter that pads with summary. The 800-word floor catches stubs — chapters that were never written. It is a tripwire, not a target.

**The real test is scene completeness:**
- Is the chapter's central moment rendered (scene, dialogue, body anchors) or summarized (telling the reader what happened)?
- Is the emotional turn dramatized — does the reader experience the shift, or are they told it occurred?
- Are body anchors present — hands, eyes, breath, spine — grounding abstract emotion in physical sensation?
- Does the chapter have dialogue, or is it pure narration?

**The lint suite checks this deterministically:** chapters with <5% dialogue AND <5 body-anchor words per 1k words are flagged as "pure summary." This is a gating condition — a chapter that is pure summary cannot advance, regardless of word count.

**The critic checks this qualitatively:** the palette critic evaluates rendering depth (scene vs summary ratio), and the show critic flags telling-not-rendering. These are located findings, not assertions.

**What this replaces:** Word-count floors/ceilings as quality proxies. The old system drove agents to edit-check-edit until chapters landed on round numbers (3000, 2500). The new system asks: "Is this chapter rendered or summarized?" Length follows rendering need.

## Prose as Music

The novel is read aloud in the reader's head. The reader hears it. If the sound is monotonous, the reader's attention drifts even if the content is interesting.

- **Vary sentence length deliberately.** Long sentences and short sentences should alternate.
- **Vary paragraph length.** A page of paragraphs all four sentences long is a page with no rhythm.
- **Read passages aloud in planning.** If you cannot imagine a human reading it with interest, the rhythm is wrong.
- **Flag passages where 5+ consecutive sentences have similar lengths** (within 3 words of each other).

## The Voice Architecture

Voice registers produce distinct character voices when applied correctly. Each character has multiple emotional registers that speak in different voices:

- **Control registers** — protective patterns that try to manage the environment to prevent vulnerability
- **Reactive registers** — impulsive patterns that distract from pain when it surfaces
- **Wounded registers** — the raw, unguarded patterns that the control and reactive registers are protecting
- **Integrated voice** — the character at their most open, most present, most themselves

The richest moments are when one register is dominant and another is leaking through — when a character gives a precise, controlled answer in a voice that is starting to crack.

**Critical:** Voice register labels must never appear in prose. "The control register takes over" is forbidden. "Her spine straightens. Her eyes focus." is allowed. The architecture is the writer's understanding, not the prose's content.

## The Misdirection Architecture

The novel maintains misdirection axes. The audience-state tracking system (`state/` files) is essential. Without it, the writer accidentally reveals too much too early.

**The discipline:**
- Track what the reader believes at each chapter
- Plant seeds with restraint — most readers should only retroactively understand the seeding on a second reading
- The first reading's surprise is the point

## The Callback System

Every seeded item must have a payoff. Every payoff must have a seed. The callback ledger (`state/callback_ledger.json`) tracks this across chapters.

**Usage:** Before writing each chapter, check the callback ledger. What seeds are active? What must pay off soon? What new seeds should this chapter plant?

## The Adversarial Reader

The most valuable critic is one that reads the manuscript cold, without the bible. The named persona (Lara Marsh, 14 years coverage experience) produces genuinely different coverage than generic prompts. Key calibration:

- The reader describes what the manuscript IS ABOUT, not what it was MEANT to be about
- If the reader says "domestic drama interrupted by something cosmic" — misdirection holds
- If the reader says "sci-fi novel with human characters" — misdirection broke

## Single-Model Validation

Same-model critics have self-recognition bias. With a single model, the substitutes are:

1. **Blinding:** Each critic reads only the chapter text + its specific rubric. No cross-pollination from other critics or the architect plan.
2. **Located findings:** Every flagged issue must cite quoted text + position. Bare PASS assertions fail the gate.
3. **Deterministic lints:** The lint suite (`tools/lint_suite.py`) catches patterns the model won't flag against itself — duplicate paragraphs, refrain repetition, negative-construction density, banned constructions. These are model-independent.
4. **Revise-then-recheck:** Each finding must be fixed and re-verified before advance. No "flagged but shipped."

## The Silence Architecture Voice

The dominant voice pattern for this template. Meaning lives in what characters DON'T say.

Core principles:
- Characters speak only when they must. Silence carries meaning.
- Action lines render the gaps — what characters don't say, don't do, don't acknowledge.
- White space is structural. A single line alone on the page is a deliberate choice.
- Subtext over statement. Always.

## The Convention Ledger

Track all writing conventions — not just prohibited ones. The Convention Ledger prevents overuse of permitted constructions.

**Categories tracked:**
- Body anchors — hands, eyes, breath, spine, jaw. If every emotional beat uses hands, the reader notices.
- Sensory details — which senses are invoked, how often, in what patterns.
- Sentence rhythm patterns — short-long-short, all short, periodic sentences.
- Dialogue attribution conventions — said/asked/whispered ratios, attribution frequency.

Full guidance: [`convention_tracking.md`](convention_tracking.md)

---

## The Iterative Revision Protocol

How a produced novel went from draft to Acquisition Recommendation through targeted revision iterations. Each iteration addressed specific issues identified by the adversarial reader:

1. **Cut and Consolidate** — Mechanical compression. Prose density.
2. **Deepen and Earn** — Character specificity, POV interiority.
3. **Resonance and Polish** — Callback reinforcement, thematic threading.
4. **Structural Issues** — Chapter-level architecture.
5. **Final Polish** — Sentence-level precision, convention ledger compliance.

**Key insight:** Each iteration was targeted, not general. The adversarial reader identified specific issues; the revision addressed those issues and nothing else.

Full protocol: [`iterative_revision_protocol.md`](iterative_revision_protocol.md)

---

*This craft guide is based on the production system for a dual-track literary science fiction novel that received an Acquisition Recommendation from professional coverage.*
