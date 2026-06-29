# CONTINUITY CRITIC — Chapter 6: The Field of Jarama

**Critic type:** Continuity (knowledge-delta, POV-knowledge, callback, timeline, reader-state, props)
**Chapter:** 6 — The Field of Jarama
**Date:** 2026-06-07
**State files loaded:** callback_ledger.json, convention_ledger.json, timeline.json, reader_state.json, pipeline_status.json, project_state.json, resume_chapter_5.json
**Bible files loaded:** 04_outline.md, 07_format_rules.md, 03_characters/ (martin, tomas, vidal, padre_joaquin)
**Prior chapters loaded:** Ch5 (The Yoke and the Arrows)

---

## VERDICT: ADVANCE

**Summary:** Chapter 6 is continuity-clean across all six check dimensions. Callbacks pay off correctly, the timeline is coherent, POV is maintained, props track, reader-state advances per the outline, and the knowledge-delta is earned. Two advisory notes (one foreign character in prose, one prop gap) do not block advancement.

---

## 1. TIMELINE CHECK

### Findings

| Item | Status | Detail |
|------|--------|--------|
| Chapter date | PASS | "February 1937" — consistent with Ch5 (February 17, 1937, unification decree) |
| Sequencing from Ch5 | PASS | Ch5 ends at Madrid reserve line. Ch6 opens with move south to Jarama front. Logical military progression. |
| Day count within chapter | PASS | Arrive afternoon → first meal → second night (voices) → third day (Tomás identifies English) → fourth day (sniper kills volunteer from Estella) → fifth night (confession) → eighth day (International Brigades attack) → burial at dawn → that night (conversation). Days are counted consistently from arrival. |
| Historical plausibility | PASS | Battle of Jarama ran February 6–27, 1937. Battalion arriving mid-February and holding the line is historically consistent. International Brigades (British Battalion, French, German volunteers) were present at Jarama. |
| Season detail | PASS | Tomás's mother writes about spring coming; Martín notes "It was February. In Navarre, spring was still a month away." Correct — Navarre spring arrives March/April. |
| Gap from prior chapter | PASS | Ch5 ends at February 17, 1937 at Madrid reserve line. Ch6 opens "February 1937" at Jarama. No gap contradictions. |

### State file comparison

- **timeline.json**: Only Ch1 is logged (July 18, 1936). Ch6 is not yet logged — expected, as the timeline file is updated post-chapter.
- **resume_chapter_5.json**: `timeline_position: "February 17, 1937 — Madrid reserve line"`. Ch6 moves to Jarama — consistent forward progression.
- **project_state.json**: `timeline_position: "February 17, 1937 — Madrid reserve line"`. Same — Ch6 advances from this point.

**No timeline violations found.**

---

## 2. KNOWLEDGE-DELTA CHECK

### What Martín knows entering Ch6 (from project_state.json + Ch5)

- Carlist faith, fueros, red beret tradition, grandfather's crucifix
- Seminary training, hardware store work
- Mola has risen, the meseta, non-Carlist Spain exists
- Professional soldiers exist (Vidal), what killing feels like
- Madrid's soundscape, Army of Africa exists
- **The unification decree** (Ch5)
- **The yoke-and-arrows** (Ch5)
- **Salazar's Falangist vision** (Ch5)
- **Don Eusebio's bitterness** — "The king was not consulted. I do not know what we are fighting for now." (Ch5)

### What Martín learns in Ch6

| New knowledge | How acquired | Earned? |
|---------------|-------------|---------|
| Foreign volunteers (German, English, French) across the field | Hearing voices at night | YES — direct sensory experience |
| The enemy is not "godless Reds" but men in trenches | Listening to their voices, cadence, a man praying in English | YES — earned through observation, not told |
| Trench warfare's soundscape (sniper crack/whistle/ping, mortar sequence) | Living in the trench | YES — body-learned, consistent with Ch4's soundscape education |
| Padre Joaquín's certainty is slowing | Hearing confession, observing longer pauses, shaking hands | YES — rendered through Martín's perception, not interiority access |
| The field is a stalemate — "We hold. They hold. Nobody moves." | Eight days of experience + Tomás's summary | YES — observed fact |
| Seventeen men dead | Vidal reads names | YES — witnessed directly |

### Knowledge gaps checked

- Martín does NOT learn anything he could not perceive from his position in the trench.
- He does NOT access other characters' interiority (Padre Joaquín's doubt is rendered through voice and hands, not thought).
- He does NOT learn historical facts about the International Brigades' composition — he only hears languages and sees one figure.

**No knowledge-delta violations found.**

---

## 3. POV-KNOWLEDGE CHECK

### POV contract (from 07_format_rules.md, Section IX)

> Each chapter is Martín's POV. The prose stays inside his perception, knowledge, and voice for the chapter's duration. Close third (default). No omniscient.

### Chapter 6 compliance

| Instance | Compliant? | Detail |
|----------|-----------|--------|
| Tomás's face "calm" (line 11) | YES | Observable behavior |
| Vidal's voice "clipped," face "flat" (lines 17–18) | YES | Observable behavior |
| Tomás falling asleep in 30 seconds (line 31) | YES | Observable — Martín watches him |
| Padre Joaquín's hands shaking (line 229) | YES | Observable from Martín's position |
| Padre Joaquín's internal state ("as if the answer required more thought") (line 147) | BORDERLINE — PASS | Martín's inference from observable behavior (voice tempo, pauses). Not interiority access. Rendered as Martín's interpretation. |
| Tomás sleeping: "pragmatism of a man who has decided that tomorrow is tomorrow" (line 257) | BORDERLINE — PASS | Martín's characterization of Tomás's observable behavior (falls asleep instantly). Consistent with how Martín has characterized Tomás since Ch2. |
| Voices across the field — "Not the sounds of the godless Reds the propaganda had described" (line 77) | YES | Martín's own thought, comparing what he hears to what he was told |
| "He looked like a man I might have passed on the street in Pamplona" (line 93) | YES | Martín's perception and judgment |

**No POV violations found.** All borderline instances are Martín's inferences from observable behavior, not omniscient access.

---

## 4. CALLBACK CHECK

### Callbacks with Ch6 as payoff chapter (from callback_ledger.json)

| Callback | Payoff chapter | Status | Ch6 execution |
|----------|---------------|--------|---------------|
| `crucifix_01` — Don Eusebio gives Martín the wooden crucifix | 6, 9, 13, 15 | Ch6 payoff expected | PASS — Martín holds the crucifix at night (lines 261–269). "Wood was warm. Groove under the thumb. Corpus under the fingers. Weight." Connects to father's letter, grandfather's wars. |
| `padre_joaquin_blessings_01` — Padre Joaquín's pastoral certainty | 6, 9, 13 | Ch6 payoff expected | PASS — Confession scene (lines 139–191). "God is with you... The cause is just." But the certainty is slower. Hands fold and unfold. Blessing delivery has "further to travel." The erosion begins here. |
| `meseta_motif` — The meseta as moral mirror | 4, 6 | Ch6 payoff expected | PASS — Line 9: "Not the green valleys of Navarre. Not the meseta of Castile." Landscape alienation established. |
| `vidal_competence` — Vidal's professional competence | 6, 10, 12 | Ch6 payoff expected | PASS — Vidal assigns positions (line 17–19), counts the dead (lines 223–227), reads names. Professional, flat, efficient. |
| `army_of_africa` — Regulares, Legionnaires | 6, 10, 12 | Ch6 expected | NOT EXPLICITLY PRESENT — The chapter does not mention the Army of Africa by name. The enemy here is the International Brigades. However, the Army of Africa was referenced in Ch4 and is not contradicted. This callback can pay off in Ch10/12 as scheduled. Not a violation — the outline does not require Army of Africa in Ch6. |
| `failed_assault` — The dream of quick victory dies | 6, 10 | Ch6 expected | PASS — The stalemate is the payoff. "We hold. They hold. Nobody moves. That's the field." The war has become attrition. |
| `sounds_of_madrid` — Artillery heartbeat, machine-gun breath | 6, 10, 12 | Ch6 expected | PASS — "Artillery was loudest — a distant press against the chest, a rumble that shook the sandbags." The soundscape from Ch4 carries forward and intensifies with the sniper/mortar taxonomy. |

### Callbacks seeded but NOT paying off in Ch6

| Callback | Expected | Status |
|----------|----------|--------|
| `red_beret_01` | Payoff Ch5, 9, 14, 15 | Seeded — beret worn throughout. No Ch6 payoff required. |
| `scapular_01` | Payoff Ch4, 12, 15 | Seeded — line 67: "Scapular on his chest." Present but not paying off. Correct. |
| `yoke_and_arrows` | Payoff Ch9, 14, 15 | Seeded — line 11: "The yoke-and-arrows pin caught the light." Present on Tomás. No Ch6 payoff required. |
| `don_eusebio_bitter_letter` | Payoff Ch9, 11, 15 | Seeded — line 267: Martín recalls the letter. No Ch6 payoff required. |
| `first_kill` | Payoff Ch9, 15 | Seeded. Not referenced in Ch6. Correct. |
| `body_prayer` | Payoff Ch9, 13, 15 | Seeded. Not referenced in Ch6. Correct. |
| `shaking_stopping` | Payoff Ch9, 15 | Seeded. Not referenced in Ch6. Correct. |
| `tomas_pragmatism` | Payoff Ch12 | Seeded — Tomás's behavior throughout Ch6 is consistent with his pragmatism (eating, sleeping, identifying English voices without concern). |
| `salazar_speech` | Payoff Ch9, 15 | Seeded. Not referenced in Ch6. Correct. |
| `tell_my_mother_01` | Payoff Ch12, 15 | Seeded — Tomás reads mother's letter (line 207). Consistent. |

### New callback seeds in Ch6

None identified. Ch6 is a payoff chapter, not a seeding chapter. Correct per the outline.

**All required callbacks pay off. No callback violations found.**

---

## 5. READER-STATE CHECK

### Current reader_belief_phase (from reader_state.json)

> "misdirection_cracking" — The midpoint has passed. The reader realizes the story is not about the war at all.

### Ch5 established the midpoint (unification decree). Ch6 should advance the cracking.

### Outline expectation for Ch6

> "The reader should feel the war's grind — and the gap between the crusade's rhetoric and the reality of men in trenches fighting men they do not know."

### Ch6 execution

| Reader-state element | Present? | How rendered |
|---------------------|----------|-------------|
| War's grind | YES | Eight days of trench life. Sniper kills. Seventeen dead. Stalemate. |
| Gap between rhetoric and reality | YES | "Propaganda had said godless Reds. Atheists. Anarchists. Men who burned churches and executed priests... These men across the field did not sound godless. They sounded tired." (lines 105–107) |
| The enemy is not what was promised | YES | Hearing German, English, French voices. A man praying in English. A young man with a mustache who "looked like a man I might have passed on the street in Pamplona." |
| Padre Joaquín's certainty cracking | YES | Confession scene — the certainty is "slower," hands shake, pauses grow longer. |
| Martín keeps doubt to himself | YES | "I kept this to myself. The thought stayed in my ears... where thoughts go when the mouth does not know what to do with them." (line 109) |

### Reader-state phase update needed

Ch6 should advance the reader from "misdirection_cracking" toward deeper cracking. The chapter executes this: the unification decree cracked the political narrative (Ch5), and Ch6 cracks the military/enemy narrative. The reader now sees that the enemy is human, the war is attrition, and even the chaplain is wavering.

**Reader-state advances correctly. No violations found.**

---

## 6. PROPS CHECK

### Props tracked in project_state.json

| Prop | Expected state in Ch6 | Actual in Ch6 | Status |
|------|----------------------|---------------|--------|
| `wooden_crucifix` | In Martín's pocket — held at night | Lines 261–269: Martín holds the crucifix. "Wood was warm. Groove under the thumb. Corpus under the fingers. Weight." | PASS |
| `red_beret` | On Martín's head | Line 11: Tomás's beret "pushed back." Martín's beret not explicitly described but implied (he wears it throughout prior chapters). | PASS (implicit) |
| `scapular` | On Tomás's chest | Line 67: "Scapular on his chest." Tomás sleeping. | PASS |
| `yoke_and_arrows_pin` | On berets | Line 11: "The yoke-and-arrows pin caught the light — a small flash, there and gone, the tin dull from wear." On Tomás. Line 249: "Pin caught the candle — a small flash, quick, gone." | PASS |
| `Don Eusebio's letter` | In Martín's pocket | Line 267: "I thought of my father's letter. *The king was not consulted. I do not know what we are fighting for now.*" Recalled from memory, not physically produced. | PASS |
| `ammunition_box` | Used as table | Lines 35, 141: "An ammunition box served as a table." "A candle stub sat on an ammunition box." | PASS (new prop, consistent) |
| `water_tin` | In trench | Lines 35, 39: On shelf dug by Tomás. | PASS (new prop, consistent) |

### Physical continuity notes

- **Tomás's beret**: Line 11 — "pushed back." Line 31 — "He pulled his beret down." Line 95 — "his beret over his eyes." Line 249 — on his head. Consistent.
- **Tomás's scapular**: Line 67 — on his chest while sleeping. Consistent with Ch5 (scapular on chest).
- **Tomás's pin**: Line 11 — catches light. Line 249 — catches candle. Consistent — pin is on beret.
- **Crucifix**: Held at chapter's end (lines 261–269). Referenced as being in three wars. Consistent with Ch1 (Don Eusebio: "Carry this. It has been in three wars.") and Ch5 (father's letter: "Your grandfather's crucifix has been in three wars.").
- **Martín's pin**: NOT explicitly described as on his beret in Ch6. The resume_chapter_5.json and project_state.json both state Martín wears the pin. The chapter does not describe him removing it. **Advisory note** — the prose could acknowledge the pin's presence on Martín's beret at least once, given it was the central image of Ch5.

### New props introduced

| Prop | Description | Consistent? |
|------|-------------|------------|
| Trench equipment (sandbags, corrugated tin, firing step) | Military trench detail | YES — consistent with Jarama front |
| Sardine tin + bread | First meal | YES — consistent with field rations |
| Candle stub on ammunition box | Confession scene | YES — consistent with trench conditions |
| Leather pouch (Padre Joaquín) | Communion wafers, wine, prayer book | YES — consistent with character profile ("He carries a leather pouch with communion wafers, a small bottle of wine, and a prayer book") |

**No prop violations found. One advisory note on Martín's pin.**

---

## 7. ADDITIONAL FINDINGS

### Foreign character in prose

Line 23 contains a non-English character (`气味` — Chinese for "smell") embedded in the text:

> "the sweat of men who had been in this hole before us and had left their气味 in the walls"

This appears to be a text-generation artifact, not intentional code-switching. The surrounding prose is in English. This character should be removed or the sentence rewritten.

**Severity:** Advisory — does not block continuity but is a prose defect.

### Character register consistency

| Character | Expected register | Ch6 execution | Status |
|-----------|------------------|---------------|--------|
| Martín | The Soldier (concrete, physical) transitioning toward doubt | Predominantly Soldier register. Observations are sensory and concrete. Doubt surfaces in the private reflection (lines 263–269) but stays within "concrete" bounds — no Fracture register yet. | PASS |
| Tomás | The Companion (easy, colloquial) | "Not bad" (line 41). "Compared to Madrid. At least here we can see the sky" (line 45). "English... Definitely English" (lines 97–101). "We held" / "That's the field" (lines 245–255). Companion register throughout, with the humor stripped by fatigue — consistent with "The Brother" register bleeding through. | PASS |
| Vidal | The Officer (clipped, precise) + The Realist | "Here. You're here." (line 19). "Bury him tonight. Do not stand above the parapet." (lines 127–128). "This is not a siege. This is a field. A field does not care which side you are on." (lines 131). Reads names. | PASS |
| Padre Joaquín | The Pastor (warm, measured) with doubt leaking | Confession: "God is with you... The cause is just. The Church has said so." (line 173). "Pray for clarity... Not believe. Know." (lines 177). But the delivery is "slower," hands shake, pauses grow. The Pastor register holds but the doubt is audible. | PASS — **Excellent execution of the character arc beat.** |

### Outline beat coverage

| Outline beat | Present? | Location |
|-------------|----------|----------|
| Battalion moved to Jarama front | YES | Lines 9–16 |
| Martín and Tomás share a trench | YES | Lines 17–31 |
| International Brigades across the line | YES | Lines 64–109 |
| Propaganda vs. reality gap | YES | Lines 105–109 |
| Snipers, mortar fire, constant noise | YES | Lines 53–63, 113–136 |
| Padre Joaquín hears confessions | YES | Lines 139–191 |
| Confessions grow longer | YES | Lines 147, 175–179 |
| Chapter ends with stalemate | YES | Lines 255, 277 |
| Cost is seventeen dead | YES | Lines 225–231 |

**All outline beats are present. No structural omissions.**

---

## SUMMARY

| Check | Result |
|-------|--------|
| Timeline | PASS — February 1937, consistent with Ch5 and historical record |
| Knowledge-delta | PASS — all new knowledge earned through direct experience |
| POV-knowledge | PASS — Martín's perception only, no omniscient leakage |
| Callback | PASS — all Ch6 payoffs executed, all seeds maintained |
| Reader-state | PASS — misdirection cracking deepens, gap between rhetoric and reality rendered |
| Props | PASS — crucifix, beret, scapular, pin all tracked correctly |

### Advisory notes (non-blocking)

1. **Foreign character artifact** at line 23 (`气味`) — text-generation error, should be removed.
2. **Martín's yoke-and-arrows pin** not explicitly described on his beret in Ch6 — the prose could acknowledge its presence at least once given its centrality in Ch5.

---

**Verdict: ADVANCE**
