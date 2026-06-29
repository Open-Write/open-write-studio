# Screenplay Craft — What We Learned

*Distilled craft knowledge from screenplay production. Transferable to any screenplay project.*

---

## The Discipline Document

The single most important file in any screenplay project is `bible/07_format_rules.md`. It is reloaded every scene. Without it, the script swells. The key rules:

1. **No camera directions.** None. Not even "we see." The director chooses shots.
2. **No emotional parentheticals.** (angrily), (sadly), (quietly) — all forbidden. If the dialogue doesn't carry the emotion, rewrite the dialogue.
3. **No adverbs in dialogue tags.** "She says quietly" — forbidden.
4. **No interiority in action lines.** "Character remembers the funeral" — forbidden. "Character's hand stops on the photograph" — allowed.
5. **Dialogue is subtext, not statement.** Characters do not name their emotional states.
6. **Trust the actor.** The action line says what is happening. The dialogue says what is said. The actor and director find the rest.

## The Invisible Information Problem

The show-don't-tell critic initially missed a category of violation: **invisible information** — action lines that state facts the camera cannot see.

Three subcategories:
- **Durations stated as fact:** "She has been awake for thirty-one hours." → Show coffee cups, dark circles, a half-eaten sandwich.
- **Off-screen knowledge:** "Daniel and Theo are asleep." → "No sound from upstairs."
- **Historical interiority dressed as description:** "Dark circles under her eyes that have stopped being circles and have become a permanent feature of her face." → "Dark circles under her eyes."

The fix for all three: ask "Can the camera see this? Can the audience hear this?" If not, cut it or replace with something visible/audible.

## The Voice Architecture

Characters speak differently under different emotional conditions. Each character should have 2-4 distinct voice registers — ways of speaking that emerge under different pressures:
- A character's intellectual register sounds different from their vulnerable register
- A character's caretaker register sounds different from their defensive register
- A character's default register sounds different from their desperate register

The richest moments are when one register is speaking and another is bleeding through — when a character gives a precise answer in a voice that is starting to crack.

**Critical:** Voice register names must never appear in action lines. "The Analyst takes over" is forbidden. "Her spine straightens. Her eyes focus." is allowed. The registers are the writer's understanding, not the script's content.

## The Conditional Cutter

The cutter runs only when critics or editorial flag extraneous material. No target percentage. Cut only what was flagged.
- If a sentence doesn't earn its place, cut it
- If two sentences say the same thing, cut one
- If an adverb modifies a verb that already carries the meaning, cut the adverb
- White space is your friend. A single sentence alone on its line is often the right choice.

## The Misdirection Architecture

The screenplay maintains misdirection axes — what the audience believes at each point:

1. **Primary misdirection** — the audience believes [X] is the threat (Act One–Two-A), then ambiguity (Two-B), then the real threat is revealed (Act Three).
2. **Secondary misdirection** — the audience doesn't think about [Y]'s self-defense (early), then fears preemptive strike (middle), then learns the truth (end).

The audience-state tracking system (`state/audience_state.json`) is essential. Without it, the writer accidentally reveals too much too early.

## The Callback System

Every seeded item must have a payoff. Every payoff must have a seed. The callback ledger (`state/callback_ledger.json`) tracks this across scenes. Key callbacks follow the pattern:
- Something planted in Act One → pays off in Act Three
- A character's early observation → confirmed by the climax
- A visual or auditory motif → returns with new meaning

## The Adversarial Reader

The most valuable critic is one that reads the script cold, without the bible. The named persona (Lara Marsh, 14 years, calibrated against specific films) produces genuinely different coverage than generic prompts. Key calibration:
- The reader describes what the script IS ABOUT, not what it was MEANT to be about
- The reader's "What the pages are" paragraph tells you whether the misdirection is holding
- If the reader says "domestic drama interrupted by something cosmic" — misdirection holds
- If the reader says "sci-fi film with human characters" — misdirection broke

## Cross-Model Triangulation

Same-model critics have self-recognition bias. Run at least 2 models on every critical pass. Take the union of flagged issues, not the intersection.

---

## The Silence Architecture Voice

The dominant voice pattern validated through production use. Meaning lives in what characters DON'T say.

**Primary tool:** What's NOT on the page. The Silence Architecture produces restraint — every line must earn its place.

Core principles:
- Characters speak only when they must. Silence carries meaning.
- Action lines render the gaps — what characters don't say, don't do, don't acknowledge.
- **Key character speeches:** Maximum 2 per act. When a key character speaks at length, it matters.
- **Protagonist:** Catalytic interjections — short lines that shift the energy of a scene without explaining why.
- **Supporting characters:** Their interventions are earned through specific experience, not through being wise beyond their years.
- White space is structural. A single line alone on the page is a deliberate choice, not an accident.

The voice was validated by achieving RECOMMEND from Lara Marsh after 5 iterative revisions.

### What the Silence Architecture Does

- **Opens with silence.** A woman in a dark house. A closed door. A notebook on a counter. Five pages, no dialogue.
- **Builds through omission.** The reader assembles emotional truth from what's not said.
- **Deploys physical detail in the silences.** When a character doesn't speak, the reader's attention goes to the room — the hum of the servers, the click of a relay, the weight of a hand on a table.
- **Ends on an unresolved image.** The image holds. Decays. Is gone.

### What the Silence Architecture Does NOT Do

- Describe what characters feel
- Explain what the audience should understand
- Use metaphors in action lines
- Allow the protagonist to be a bystander in their own climax
- Use camera directions
- Direct performances from the page

---

## The Dual-Voice Challenge

When a screenplay has two tracks (e.g., human + alien), both voices must feel like the same author. This is the central craft challenge of dual-track screenplays.

**The test:** Write 3 consecutive scenes in alternating voices (A → B → A) and have Lara read them cold. The question: "Does this feel like one writer or two?"

**What makes voices feel like one author:**
- Consistent sentence-level discipline (not the same sentences, but the same standards)
- Shared thematic preoccupations (both tracks are asking the same questions)
- Compatible restraint (neither track is more verbose than the other)
- Matching specificity (both tracks earn their details with equal precision)
- **Body-anchor bridge** — physical actions in both tracks are both specific, both silent

Full guidance: [`skills/dual_voice_guidance.md`](dual_voice_guidance.md)

---

## The Iterative Revision Protocol

How a produced screenplay went from CONSIDER to RECOMMEND through 5 targeted iterations:

1. **Cut and Consolidate** — Mechanical compression. Remove redundancy, tighten scenes, eliminate over-description.
2. **Deepen and Earn** — Give characters specific experience to justify their positions.
3. **Resonance and Polish** — Callback reinforcement, thematic threading.
4. **Structural Issues** — Address the largest remaining structural issues.
5. **Final Character Depth** — Interiority for underserved characters.

**Key insight:** Each iteration was targeted, not general. Lara identified specific issues; the revision addressed those issues and nothing else.

Full protocol: [`skills/iterative_revision_protocol.md`](iterative_revision_protocol.md)

---

## The Convention Ledger

Track all writing conventions used, not just prohibited ones. The Convention Ledger prevents overuse of permitted constructions — the subtle repetition that makes prose feel manufactured even when no individual sentence violates any rule.

**Categories tracked:**
- **Body anchors** — hands, eyes, breath, spine, jaw. If every emotional beat uses hands, the reader notices.
- **Sensory details** — which senses are invoked, how often, in what patterns.
- **Sentence rhythm patterns** — short-long-short, all short, periodic sentences. Rhythm repetition flattens impact.
- **Dialogue attribution conventions** — said/asked/whispered ratios, attribution frequency, tag placement.

Full guidance: [`skills/convention_tracking.md`](convention_tracking.md)

---

## Line Count Over Page Count

For screenplays, line count is more reliable than page count estimation. Fountain files render differently in different tools. Use line count for internal tracking; use PDF page count only for industry submission.

**Baseline:** ~1,700 lines = ~60 pages in standard spec format (Courier 12, 1.5" left margin).
