# Continuity Critic — Chapter 8: The Schoolteacher

**Chapter:** 8 — The Schoolteacher
**Critic:** Continuity (knowledge-delta, POV-knowledge, callback, timeline, reader-state, props)
**Date:** 2026-06-07

---

## Verdict: REVISE

Three blocking continuity errors. Multiple advisory findings. The chapter is structurally strong and emotionally devastating, but the Euskara alphabet chart is handled as if Chapter 7 did not happen, and the school building changes between chapters.

---

## BLOCKING FINDINGS

### B-1. The Euskara Alphabet Chart Is Taken Twice

**Location:** Ch8:17-25 vs Ch7:99-109

In Chapter 7, Martín explicitly removes the chart from the wall:

> "I reached out and touched the chart. Paper. Thin, printed, the ink faded slightly where the sun had hit it through the window. A child's hand had drawn a flower in the margin, small, in pencil, five petals, a stem... I pulled the chart from the wall. The nail held for a moment, then the paper tore and the chart came free in my hands. I folded it and put it in my breast pocket." (Ch7:105-109)

In Chapter 8, the chart is described as still on the floor where it was torn from the wall:

> "The Euskara alphabet chart was on the floor. It had been torn from the wall — the four tacks still in the plaster, the paper ripped where the tacks held, the top edge curling down." (Ch8:17)

Martín then picks it up and pockets it again:

> "I picked up the chart... I folded the chart once and put it inside my jacket." (Ch8:19, 25)

The chart cannot be in both Martín's pocket (from Ch7) and on the school floor (in Ch8). Chapter 7 establishes that Martín took the chart secretly, told no one ("Found anything?" "I shook my head."), and the nail held then tore. Chapter 8 describes the chart with four tacks still in the paper. These are incompatible accounts of the same object.

**Fix options:**
1. Remove the chart-taking from Ch8 entirely. Martín already has it. He can take it out and look at it, but he does not pick it up from the floor.
2. Remove the chart-taking from Ch7. Ch8 is the canonical taking. Rewrite Ch7 to reference the chart on the wall without removing it.
3. Make Ch8 reference that Martín already has the chart (from Ch7) and show him taking it out during the encounter with Amaia — she sees it in his jacket because he already put it there days earlier.

Option 3 is strongest: it preserves the parallel between chapters and makes Amaia's recognition of the chart in his jacket (Ch8:33) a callback to Ch7 rather than an impossible observation.

### B-2. Amaia Sees the Chart in Martín's Jacket — But He Already Took It

**Location:** Ch8:33

> "She looked at the chart in my jacket, the edge of it visible above the button, the black letters and the red vowels and the corner of the child's flower."

If Martín took the chart in Ch7 (days earlier, secretly), it would not be "visible above the button" of his jacket during the Ch8 encounter — he would have folded it and stored it. If the chart is still on the floor in Ch8 (as the current text implies), then Amaia cannot see it in his jacket before he picks it up. The timeline of when the chart enters his jacket is broken.

**Dependent on B-1 fix.** If option 3 is chosen, this detail must be adjusted: the chart was already in his jacket from Ch7, and Amaia recognizes it during the encounter. The "edge visible above the button" detail needs to be rewritten to reflect that the chart has been in his pocket for days — soft from handling, not freshly picked up.

### B-3. The School Building Changes Between Chapters

**Location:** Ch7:91-93 vs Ch8:5

Chapter 7:

> "A low building next to the church. One room. Stone walls, a wooden floor, desks arranged in rows." (Ch7:91-92)

Chapter 8:

> "The town had a school. It stood on a slope above the plaza, two stories, whitewashed stone, a sign above the door in two languages: Ikastola / Escuela." (Ch8:5)

The school is a single-story, single-room building in Ch7 and a two-story building in Ch8. The location relative to the church/plaza also shifts. These are the same building — both have the Euskara alphabet chart, the crucifix, the overturned desks.

**Fix:** Reconcile the building description. Either Ch7 or Ch8 must be rewritten to match. The Ch8 description (two stories, sign in two languages) is more specific and should be canonical. Rewrite Ch7's "A low building next to the church. One room." to match.

---

## ADVISORY FINDINGS

### A-1. Desk Damage Description Is Inconsistent

**Location:** Ch7:97 vs Ch8:15

Ch7: "The desks were overturned. Some were broken — legs snapped, tops splintered."
Ch8: "The desks were overturned. Not broken — overturned."

Ch7 describes broken desks (snapped legs, splintered tops). Ch8 explicitly states they are "Not broken — overturned." This is a direct contradiction of the same physical state. If Ch7 is the canonical first visit, the desks should still be broken when Martín returns in Ch8 — unless someone repaired them, which is not stated.

**Fix:** Align the desk descriptions. If Ch8 is the canonical school visit, Ch7 should describe the desks as overturned but not explicitly broken. If both visits are canonical, Ch8 should note the broken desks from Ch7.

### A-2. The Yoke-and-Arrows Pin Is Not Mentioned

**Location:** Ch8 (throughout)

Martín wears the yoke-and-arrows pin on his beret (established in Ch5, confirmed in project_state.json). Amaia examines Martín closely — his beret, the chart in his jacket, his face. She says: "And you are here. In a red beret. Fighting for the men who will ban it." She references the beret but not the pin.

Given that the pin is the symbol of the movement that closed her school and banned her language, its absence from her perception is a missed opportunity. It is not a continuity error — she may have seen it and chosen not to mention it — but the pin should at least be rendered in the physical description of Martín's beret.

**Fix:** Add a brief physical detail — "the yoke-and-arrows on my beret" — in Amaia's survey of the room (Ch8:33) or in Martín's self-description when she first sees him.

### A-3. project_state.json and reader_state.json Are Not Updated

**Location:** state/project_state.json, state/reader_state.json

- `project_state.json` shows `current_chapter: 5` and `chapters_completed: [1,2,3,4,5]`. The pipeline_status.json shows chapters 1–7 complete. The project_state is stale.
- `reader_state.json` has no entries for chapters 6, 7, or 8. The `phase_history` ends at chapter 5.
- `timeline.json` has only chapter 1's date. No entries for chapters 2–8.
- `callback_ledger.json` has `amaia_school_01` as "not_yet_seeded" — Ch8 seeds it.
- `convention_ledger.json` is empty — no body anchors, sentence rhythms, or dialogue attributions tracked across 8 chapters.

These state files should be updated after Ch8 is finalized. The stale state files will cause problems for Ch9 planning.

### A-4. Tomás's Dialogue Register Shifts Without Trigger

**Location:** Ch8:115-186

Tomás speaks in complete, articulate sentences in this chapter: "She's right," "About the chart. About the school. About the language," and the long passage about his mother teaching him to read (Ch8:177-181). His character profile specifies three registers: The Companion (dialect, fragments), The Brother (blunt, short), The Son (quiet, hesitant).

The "She's right" passage uses The Brother register (blunt, direct). The mother passage uses The Son register (quiet, personal). Both are appropriate to the emotional context. However, Tomás's profile specifies that The Son register "surfaces only when he is away from the other men" — but here he speaks to Martín on the bench outside the billet. This is a minor register-context mismatch. The moment works emotionally, but the profile's constraint ("only when away from other men") should be noted.

**Fix:** Either relax the profile constraint (The Son can surface with Martín, who is the closest thing Tomás has to a brother) or adjust the scene so Tomás speaks these words when Martín is not directly present (e.g., overheard).

### A-5. Padre Joaquín's Absolution Scene — Timeline of His Doubt

**Location:** Ch8:137-155

The chapter shows Padre Joaquín absolving a dying Basque Nationalist soldier. His profile establishes this as "the key turning point" in his theological arc — the moment the framework cracks. However, in Ch7, Padre Joaquín already said: "I do not know how to hold both in one hand" (Ch7:217), indicating doubt has already begun.

The Ch8 absolution scene should register as the *deepening* of doubt, not its origin. The current text renders it cleanly — Padre Joaquín's "thumb moved on the soldier's forehead with the precision of a man who has made that sign ten thousand times and has never yet found it adequate" (Ch8:145) — but the "never yet found it adequate" implies this inadequacy is new, when Ch7 already established his uncertainty.

**Fix:** Adjust the interiority to reflect that this inadequacy is not new — it has been present since Ch7 (or earlier). The absolution scene should deepen existing doubt, not discover it.

### A-6. The Framing Device Section Mirrors Ch7 Too Closely

**Location:** Ch8:191-197

The final section ("I am at the table. The inkwell is full. The hardware store is dark.") closely mirrors Ch7's framing section (Ch7:225-227). Both use the same structure: present-tense, the table, the inkwell, the chart in the drawer, the child's flower. The repetition is deliberate — the framing device is the novel's recurring anchor — but the specific details are near-identical.

Ch7: "I have the chart in a drawer. I took it with me when we left the town. I have never shown it to anyone. It is folded, once, the paper soft from handling, the ink faded where the sun hit it. The child's flower is still there, in pencil, in the margin. Five petals. A stem."

Ch8: "The chart is in the drawer, folded once, the paper soft from handling, the ink faded where the sun hit it. The child's flower is there, in pencil, in the margin. Five petals. A stem."

The near-verbatim repetition risks reading as accidental rather than intentional. If the framing device is meant to accumulate — each chapter adding a layer — then Ch8 should add something Ch7 did not have, not repeat the same inventory.

**Fix:** Add a detail to Ch8's framing that is new — the child's arithmetic slate (mentioned in Ch8's main narrative but not in the framing), or Amaia's voice, or the sound of the Euskara words. The framing already does this ("I look at it and I hear her voice") — lean into that addition and reduce the repeated inventory.

---

## KNOWLEDGE-DELTA

### What Martín Now Knows (post-Ch8)

| Knowledge | Source | Status |
|-----------|--------|--------|
| Amaia Etxeberria exists — Basque schoolteacher, 28, Tolosa | Direct encounter | NEW |
| The school was closed by military governor order — Euskara forbidden | Amaia's statement | NEW |
| The fueros are not abstract — they are a school, a chart, a language | Amaia's teaching | NEW |
| Tomás's mother taught him to read in the kitchen | Tomás's confession | NEW |
| Tomás's scapular was made the same year he learned to read (age 7) | Tomás's confession | NEW |
| Padre Joaquín absolves enemy soldiers with the same sacrament | Direct observation | NEW |
| He cannot speak Euskara — the language is gone from his mouth | Failed attempt | CONFIRMED |
| Sixty kilometers between Pamplona and Tolosa | Map observation | NEW |
| The crucifix in the classroom is the same as in Navarrese churches | Direct observation | CONFIRMED |

### Knowledge Gaps

No gaps detected. Martín does not learn anything he could not know through his senses and Amaia's speech.

---

## POV-KNOWLEDGE

**Assessment: CLEAN**

All narration stays within Martín's perception. No omniscient intrusions.

- Amaia's interiority is rendered through physical detail: "her eyes held mine," "her breathing was steady," "her hands were at her sides."
- Tomás's interiority is rendered through behavior: "His jaw worked slightly, the muscles moving under the skin, as it did before a man said something he had been holding back."
- Padre Joaquín's interiority is rendered through action: "His lips moved but no sound came."
- The dying soldier's interiority is absent — Martín sees only the body.

One borderline moment:

> "She had seen a man in a red beret who spoke Euskara, or had spoken it, or whose grandmother had spoken it, and she had spoken to him in the language of the chart on the wall, and he had not been able to answer." (Ch8:91)

This reads as Martín's interpretation of what Amaia saw, not omniscient narration. The construction ("She had seen") is Martín reconstructing her perception from the evidence of her face. Acceptable.

---

## CALLBACK ANALYSIS

### Callbacks Seeded

| Callback | Chapter | Detail | Status |
|----------|---------|--------|--------|
| amaia_school_01 | 8 | The closed school, the chart, the overturned desks | SEEDED — payoff Ch15 |
| scapular_01 | 8 | Tomás's scapular — frayed edge, mother's sewing | DEEPENED — now linked to age 7, learning to read |
| padre_joaquin_blessings_01 | 8 | Absolution of dying Basque Nationalist | DEEPENED — same sacrament, same God |
| red_beret_01 | 8 | Beret adjusted by Martín when uncomfortable | CONTINUED — habitual gesture |

### Callbacks Referenced

| Callback | Reference | Status |
|----------|-----------|--------|
| crucifix_01 | Classroom crucifix — same expression as Don Eusebio's | CONSISTENT |
| red_beret_01 | "In a red beret. Fighting for the men who will ban it." | CONSISTENT |
| tell_my_mother_01 | Tomás's mother — teaching him to read | CONSISTENT (pre-Ch12 seed) |

### Callback Risk

The Euskara chart callback is broken by the double-taking (B-1). The chart's journey from wall → Martín's pocket must be canonical in exactly one chapter.

---

## TIMELINE

**Ch8 timeline position:** July 1937 (per outline). The school was closed in June. Martín enters the school on the fourth morning of his presence in the town.

**Consistency with Ch7:** Ch7 establishes arrival in the occupied town after Bilbao falls (June 19, 1937). Ch8 follows — days later, same town. The timeline is coherent.

**Minor note:** The outline says "July 1937" but Ch7's resume says "June 1937." The chapter text does not specify a month. If Ch8 is July, there should be a temporal marker (the heat, the length of days, the occupation settling in). Currently the chapter reads as days after Ch7, not weeks.

---

## READER-STATE

**Expected post-Ch8 state (per outline):** "The reader understands the moral catastrophe. The Carlists are fighting Catholics for the same fueros."

**Actual reader-state achieved:** The chapter delivers this. Amaia's teaching ("We are Catholic. We are Basque. We had the fueros. You took them.") is the fixed dialogue from the outline. The classroom scene with the overturned desks, the torn chart, the remaining crucifix — these are the physical anchors of the moral catastrophe. The dying Basque Nationalist soldier reinforces it: the same sacrament, the same God, the same language.

**Assessment:** Reader-state transition is achieved. The chapter earns the outline's intended emotional beat.

---

## PROPS TRACKING

| Prop | Ch7 State | Ch8 State | Consistent? |
|------|-----------|-----------|-------------|
| Wooden crucifix | In Martín's pocket | Not mentioned (classroom crucifix only) | YES — personal crucifix not needed in this scene |
| Red beret | On Martín's head | On Martín's head, adjusted when uncomfortable | YES |
| Yoke-and-arrows pin | On Martín's beret (Ch5) | NOT MENTIONED | ADVISORY (A-2) |
| Scapular | On Tomás's chest | On Tomás's chest, frayed edge, visible at collar | YES |
| Euskara alphabet chart | Taken by Martín (Ch7:109) | On the floor, taken again (Ch8:19-25) | **NO — BLOCKING (B-1)** |
| Basque flag (ikurriña) | In the gutter (Ch7:122-129) | Not mentioned | YES — different scene |
| Child's slate (arithmetic) | Not in Ch7 | Under desk, 7+5=12 | NEW PROP — consistent |
| Map of Basque provinces | Not in Ch7 | Pinned to wall, Tolosa circled in red | NEW PROP — consistent |

---

## SUMMARY OF FINDINGS

| ID | Severity | Finding |
|----|----------|---------|
| B-1 | BLOCKING | Euskara alphabet chart taken twice (Ch7 and Ch8) |
| B-2 | BLOCKING | Amaia sees chart in Martín's jacket before he picks it up |
| B-3 | BLOCKING | School building is 1-story/1-room in Ch7, 2-story in Ch8 |
| A-1 | Advisory | Desk damage contradicts (broken in Ch7, "not broken" in Ch8) |
| A-2 | Advisory | Yoke-and-arrows pin not mentioned despite Amaia's close survey |
| A-3 | Advisory | State files (project_state, reader_state, timeline, callback_ledger) are stale |
| A-4 | Advisory | Tomás's Son register used in Martín's presence (contradicts profile constraint) |
| A-5 | Advisory | Padre Joaquín's doubt rendered as new when Ch7 already established it |
| A-6 | Advisory | Framing device section repeats Ch7 inventory near-verbatim |

**Three blocking findings must be resolved before this chapter advances.** The alphabet chart continuity break (B-1/B-2) and the school building description (B-3) are hard errors that will be caught by any attentive reader.
