# Craft & Feeling Guide — TV Series

*Adapted from screenplay craft guidance for episodic television. This is the emotional execution standard. Every scene in every episode must be measured against these principles.*

*The core principles carry over from the screenplay template — lead with bodies, trust silence, no villain, voice architecture, grief as engine. The TV-specific additions are marked with [TV].*

*See also: [`06_format_rules.md`](06_format_rules.md) for formatting discipline, [`01_series_concept.md`](01_series_concept.md) for thematic frame.*

---

## I. THE FOUNDATION

### Every Scene Must Aim to Produce at Least Two Distinct Emotions in Tension

A scene of pure grief is sentimental. A scene of pure suspense is mechanical. A scene where a detective examines a crime scene while processing a phone call from her estranged sister — that is television. Most scenes in the outline have an emotional palette annotated for that reason.

**[TV] Note:** TV has more scenes than film. This means more opportunities for emotional complexity — and more temptation to settle for single-note scenes. A procedural case-of-the-week can survive single-note scenes. A great show cannot. Every scene earns its place by doing emotional work.

### Lead with Bodies, Not Concepts

The show may deal with complex ideas — patterns, anomalies, institutional dynamics — but the audience experiences this through bodies. A hand on a desk. A breath held too long. Eyes that don't meet. The science is not the feeling. The hand is the feeling.

When in doubt, write the body — the breath held, the eyes that won't meet, the hand that almost reaches and doesn't.

### Trust Silence

The most important moments in the show are not dialogue. A scene where two characters sit in a car and don't speak can be the most powerful scene in the episode. Resist the impulse to fill.

**[TV] Note:** TV is a dialogue-heavy medium. Episodes have more pages, more scenes, more words than a feature film. This makes silence even more powerful — because it's rarer. A silent moment in a 60-page script hits harder than a silent moment in a 120-page script, because the audience has been conditioned to expect words.

### No Villain

Every character — including antagonists, institutional opponents, and morally compromised figures — must be given the most articulate possible version of their position. The audience must be able to hear the antagonist's argument and feel its pull.

The show fails if anyone is a foil. The show succeeds if every character is the protagonist of the story they are telling themselves.

**[TV] Note:** TV has more time to develop antagonists than film. Use it. A recurring antagonist who appears in 6 episodes can be more nuanced than a film antagonist who appears in 3 scenes. But the temptation is also greater — with more screen time, the temptation to make the antagonist "complex" by giving them a sad backstory increases. Complexity is not a backstory. Complexity is a position that the audience understands without forgiving.

---

## II. THE VOICE ARCHITECTURE

The voice architecture produces distinct character voices when applied correctly. Each character has multiple "registers" — tonal modes that emerge under different conditions.

**Critical:** Voice register names must never appear in action lines. "The Analyst takes over" is forbidden. "Her spine straightens. Her voice flattens" is allowed. The architecture is the writer's understanding, not the script's content.

**[TV] Note:** TV runs for multiple episodes and seasons. Voice registers can evolve over time — a character's defensive register may weaken as they open up. Track these changes in the character profile and in [`../state/character_state_tracker.json`](../state/character_state_tracker.json).

### How to Use Voice Architecture in Each Scene

1. **Before writing the scene:** Ask "Which register of this character is active?"
2. **In the dialogue:** Let the register's voice come through — sentence structure, vocabulary, verbal tics.
3. **In the action lines:** Show the physical manifestation of the register — posture, gestures, breathing.
4. **At transitions:** When one register gives way to another, show it in the body before the dialogue changes.

### The Richest Moments

The richest moments are when one register is active and another is leaking through — when the character gives a precise professional answer in a voice that is starting to crack. That crack is the scene.

---

## III. THE MISDIRECTION ARCHITECTURE

TV shows — especially serialized dramas — maintain misdirection across episodes and seasons. What the audience believes at the start of the season is not what they believe at the end.

### How to Manage Misdirection in TV

1. **Plant seeds early.** In Episodes 1-3, establish the audience's false assumption through background details, character dialogue, and visual cues.
2. **Reinforce the false assumption.** In Episodes 4-6, let the audience feel confirmed in their belief. The misdirection is strongest when the audience thinks they've figured it out.
3. **Crack the assumption.** In Episodes 7-9, introduce details that don't fit the false assumption. The audience should feel uneasy without knowing why.
4. **Reveal or refuse to reveal.** In the finale, either confirm the truth or leave the audience in productive ambiguity.

### [TV] Serialized Misdirection vs. Procedural Misdirection

- **Procedural misdirection** is per-episode: the audience thinks the suspect is X, but it's Y. This resets each week.
- **Serialized misdirection** is per-season: the audience believes the mythology is X, but it's Y. This accumulates across episodes.

The best shows use both. The procedural misdirection keeps the audience engaged week to week. The serialized misdirection keeps them coming back.

### Tracking Misdirection

Use [`../state/audience_state.json`](../state/audience_state.json) to track what the audience believes at each point. Without it, the writer accidentally reveals too much too early.

---

## IV. THE CALLBACK SYSTEM

Every seeded item must have a payoff. Every payoff must have a seed. The callback ledger tracks this across episodes.

**[TV] Note:** TV callbacks can span episodes, seasons, or even series. A seed planted in the pilot may not pay off until the series finale. The callback ledger must track the full scope.

### Types of TV Callbacks

| Type | Span | Example |
|------|------|---------|
| **Intra-episode** | Same episode | A detail in Scene 2 pays off in Scene 15 |
| **Cross-episode** | Same season | A line in Episode 1 pays off in Episode 8 |
| **Cross-season** | Multiple seasons | A character detail in Season 1 pays off in Season 3 |
| **Visual callback** | Any | An image from one episode recontextualizes in another |
| **Dialogue callback** | Any | A line repeated or echoed across episodes |

### The Rule

If you plant it, you must pay it off. If you pay it off, you must have planted it. No exceptions.

---

## V. THE NATURALISM PROBLEM

AI-generated text has identifiable tells. Readers who perceive AI authorship prejudge the work regardless of quality. The Naturalism Critic addresses this by detecting and flagging:

1. **Em-dash overuse** — Target: ≤2 per page. Replace with periods, commas, colons, or silence.
2. **Triplet closing patterns** — Three short sentences ending passages. Acceptable once per scene; mechanical when repeated.
3. **Inhuman style consistency** — Uniform sentence lengths across scenes. Human writers have bad days.
4. **Sentence construction overuse** — Negation-action pairs, parallel adjectives, corrective fragments.

**[TV] Note:** TV has more pages per episode than a single scene in a film. This means more opportunities for AI tells to accumulate. Run the naturalism critic on each episode after assembly.

**Key principle:** The goal is reduction to human-normal frequency, not elimination.

---

## VI. PACING IN TELEVISION

### [TV] The Episode Rhythm

Every episode has a rhythm — a build from the cold open to the final image. The rhythm is not just plot; it is emotional.

**The cold open** sets the emotional register. It should be the episode's most arresting moment — not necessarily the most dramatic, but the most intriguing.

**Act One** establishes the world of the episode. The audience enters the show's reality. The case is introduced. The characters are in their routine.

**Act Two** disrupts the routine. The case deepens. The B-story introduces tension. The audience begins to see that this episode is not what they expected.

**Act Three** is the crisis. The case reaches its most dangerous point. The B-story collides with the A-story. The character is forced to choose.

**Act Four** is the resolution — or the refusal to resolve. The case is closed (or left open). The character is changed (or confirmed in their resistance to change). The final image lingers.

**[TV] Note:** These are not rigid rules. Some episodes break the rhythm deliberately — an episode told in reverse, an episode with no case, an episode that is entirely a conversation. But the writer must know the rhythm before they break it.

### [TV] The Season Rhythm

The season has its own rhythm, analogous to a three-act structure:

- **Act One (Episodes 1-3):** Setup. The audience learns the world.
- **Act Two (Episodes 4-7):** Complication. The stakes escalate.
- **Act Three (Episodes 8-10):** Crisis and resolution.

The mid-season twist (usually Episode 5 or 6) is the season's midpoint — the moment where the protagonist's understanding of the world shifts irrevocably.

---

## VII. DIALOGUE IN TELEVISION

### [TV] Dialogue Density

TV has more dialogue than film. A one-hour drama may have 40-50 pages of dialogue-heavy content. This creates two risks:

1. **Over-writing:** Characters talk too much. Scenes become conversations instead of dramatic events.
2. **Under-writing:** Characters talk too little. Scenes become atmospheric without advancing.

The balance: every scene must have at least one line of dialogue that advances the plot, reveals character, or shifts the power dynamic. If a scene has none of these, it is not earning its page count.

### [TV] Character Voice Consistency Across Episodes

In a film, a character speaks for 120 pages. In a TV season, a character speaks for 600+ pages across 10 episodes. Voice drift is a real risk.

**Prevention:**
1. Reload the character profile before every episode.
2. Use the character's voice registers as anchors.
3. Run the voice critic on every scene.
4. Track dialogue patterns in the convention ledger.

### [TV] The "Previously On" Problem

TV shows sometimes use "previously on" recaps that require characters to restate plot points in unnatural dialogue. This is a production convenience, not a writing choice. Do not write dialogue that exists only to remind the audience of what happened last week. If the audience needs reminding, the show's writing isn't strong enough.

---

## VIII. THE ADVERSARIAL READER

The most valuable critic is one that reads the script cold, without the bible. The named persona (Lara Marsh, 14 years, calibrated against specific shows) produces genuinely different coverage than generic prompts.

**[TV] Note:** For TV, the adversarial reader operates at two levels:

1. **Per-episode:** Cold coverage of each episode as a standalone document.
2. **Per-season:** Cold coverage of the assembled season as a complete story.

The per-season read is essential — it catches issues that per-episode reads miss: pacing across episodes, subplot resolution, character arc completion, and the season's thematic coherence.

---

## IX. CROSS-MODEL TRIANGULATION

Same-model critics have self-recognition bias. Run at least 2 models on every critical pass. Take the union of flagged issues, not the intersection.

**[TV] Note:** With 10 episodes per season, the temptation is to run critics on only a few episodes. Run them on every episode. A voice inconsistency in Episode 3 that isn't caught until Episode 8 has contaminated 5 episodes of script.

---

## X. THE LAST THING

The success of this show is not measured by how clever the premise is. It is measured by whether, six weeks after the season finale, a viewer still thinks about the protagonist in the final image — and whether they are already waiting for the next season.

The premise is the scaffolding. The characters are the building.

---

*This document is the emotional constitution of the show. It governs every scene, every episode, every season. Reload it often.*
