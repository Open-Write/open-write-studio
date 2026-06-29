# Continuity Critic — Chapter 5: "The Yoke and the Arrows"

**Date:** 2026-06-07
**Chapter:** 5
**Word count:** ~4,200 (estimated)
**State files consulted:** callback_ledger.json, convention_ledger.json, pipeline_status.json, project_state.json, reader_state.json, timeline.json, resume_chapter_1–4.json, meta_critic_notes.md
**Bible files consulted:** 04_outline.md, 03_characters/ (all 7 profiles), 07_format_rules.md

---

## VERDICT: ADVANCE — with 3 advisory notes

Chapter 5 is continuity-clean at the manuscript level. No knowledge-delta violations, no POV breaks, no prop errors, no timeline contradictions. Three advisory notes concern stale state files that must be updated after this chapter is committed.

---

## 1. KNOWLEDGE-DELTA CHECK (HIGHEST PRIORITY)

**Verdict: PASS — no violations.**

Martín's knowledge at Ch5 opening (per resume_chapter_4.json): crucifix in pocket, beret on head, has killed a man, hands shook then stopped, has seen Army of Africa (Regulares, Legionnaires), heard first major battle at Madrid, held crucifix at night, the quick victory dream is dead.

Chapter 5 introduces:
- The unification decree (told to him by Vidal — legitimate source)
- Salazar (arrives in person — Martín observes directly)
- The yoke-and-arrows pin (distributed by Salazar's aide — direct experience)
- Don Eusebio's letter about the king not being consulted (received by mail — legitimate source)

**No character knows anything they shouldn't.** Martín does not reference events from Ch6+. Don Eusebio's letter contains information the junta would have (the king was not consulted) and a father would write to a son at the front.

**One observation for the book-runner:** `project_state.json` is stale (last updated at Ch2). It still shows Martín's location as "billeted in Castilian village" and his knowledge list omits the Army of Africa, the failed assault, and the first kill. This does not affect the manuscript but will cause false positives on subsequent continuity checks if not updated.

---

## 2. POV-KNOWLEDGE CHECK

**Verdict: PASS — no violations.**

Outline contract: "Third-person limited, Martín's perspective exclusively. The reader knows only what Martín knows, sees only what he sees."

Format rules (§IX): "Close third (default): The narrator knows what Martín knows. What Martín cannot see, the prose cannot describe."

The chapter uses the established frame device (first-person present tense: "I am at the table") wrapping past-tense third-person narration. This is consistent with Ch1–4 and is a project convention, not a POV break.

Checked passages:
- Salazar's interiority: NOT rendered. Martín reads his face and hands: "His face was still. The eyes moved" (line 69), "The mouth did not comment" (line 69). ✓
- Tomás's interiority: NOT rendered. Martín reads behavior: "His face was content" (line 21), "He was listening the way he listened to Vidal — without ideology, without theology" (line 107). ✓
- Vidal's interiority: NOT rendered. "His face was flat. The officer's face" (line 25). ✓
- Don Eusebio's interiority: NOT rendered. Martín reads the letter's physical properties — ink pressure, crowding, crossed-out word (lines 165–188). ✓

---

## 3. CALLBACK CHECK

**Verdict: PASS — all callbacks consistent.**

| Callback | ID | Seed | Ch5 Status | Consistent? |
|----------|----|------|------------|-------------|
| Wooden crucifix | crucifix_01 | Ch1 | In Martín's pocket. Compared to pin (lines 133, 149, 211, 217). On wall in frame ending (line 237). | ✓ |
| Red beret | red_beret_01 | Ch1 | On Martín's head throughout. Receives pin (line 151). On hook in frame ending (implied). | ✓ |
| Tomás's scapular | scapular_01 | Ch1 | "The scapular was on his chest" while sleeping (line 225). | ✓ |
| Don Eusebio's letters | don_eusebio_letters | Ch2 | Letter arrives, bitter and short (lines 159–191). Pays off seed: "short, factual, Carlist content between the lines." | ✓ |
| Vidal's competence | vidal_competence | Ch2 | Delivers decree "without decoration" (lines 25–41). Consistent with Ch2 seed. | ✓ |
| Tomás's pragmatism | tomas_pragmatism | Ch2 | "It's a pin" / "It doesn't change anything" / "It doesn't change the war" (lines 137, 141, 205). Consistent with "We fight. We win. We go home." | ✓ |
| Padre Joaquín's blessings | padre_joaquin_blessings_01 | Ch1 | "Padre Joaquín blessed them" (line 13). Brief mention, consistent with Madrid setting. | ✓ |

**New callback seeds planted in Ch5 (for ledger update):**
- `unification_decree_01`: The yoke-and-arrows pin on the red beret. Seeds the physical symbol that persists through Ch14–15.
- `don_eusebio_bitterness_01`: The bitter letter with crossed-out word. Payoff in Ch11 (homecoming) and Ch15.
- `salazar_persuasion_01`: Salazar's speech about "the birth of a greater one." Payoff in Ch14 ("We built a new Spain.").

---

## 4. TIMELINE CHECK

**Verdict: PASS — no violations.**

| Chapter | Date | Location | Source |
|---------|------|----------|--------|
| 1 | July 18, 1936 | Pamplona | resume_chapter_1.json |
| 2 | July–August 1936 | Castile (marching) | resume_chapter_2.json |
| 3 | September–October 1936 | First engagement | resume_chapter_3.json |
| 4 | November 1936 | Madrid outskirts | resume_chapter_4.json |
| **5** | **February 1937** | **Reserve line, west of Madrid** | **Chapter text, line 13** |

Historical verification:
- Unification decree: February 17, 1937 (line 31: "dated February seventeenth"). ✓ (Historically accurate — the real Decreto de Unificación was signed April 19, 1937, but the novel uses February 17 as its internal date. The outline specifies "February 17, 1937" at line 49. Consistent with the novel's own timeline.)
- "University City" reference (line 13): Historically accurate for the Madrid front, November 1936–February 1937. ✓
- Three-month gap from Ch4 to Ch5 is handled by the time jump at line 13: "February. The winter of 1937." ✓

**No timeline violations detected.**

---

## 5. READER-STATE CHECK

**Verdict: ADVISORY — state file stale.**

`reader_state.json` (line 11): `"chapter": 1, "phase": "misdirection_active"`

Per the outline (lines 152–153): "Act II (misdirection cracking): The unification decree reveals that the crusade is a vehicle for Franco's consolidation."

Chapter 5 is the first chapter of Act II. The reader_state should be updated to reflect that misdirection is now cracking — the unification decree is the first betrayal. The chapter itself renders this correctly: Martín's conviction is shaken by the decree, not by a battle. The prose earns the shift.

**This is a state-file maintenance issue, not a manuscript violation.** The reader's experience is correct.

---

## 6. PROPS CHECK

**Verdict: PASS — no violations.**

| Prop | Location in Ch5 | Consistent with prior chapters? |
|------|-----------------|-------------------------------|
| Wooden crucifix | In Martín's pocket (lines 133, 149, 191, 211, 217). On wall in frame ending (line 237). | ✓ (Ch1–4: in pocket) |
| Red beret | On Martín's head (lines 55, 77, 143, 149, 151, 221, 223, 225). | ✓ (Ch1–4: on head) |
| Tomás's scapular | On his chest while sleeping (line 225). | ✓ (Ch1: worn cord visible; Ch3: pulled from collar before battle) |
| Yoke-and-arrows pin | Received (line 129), placed on beret (lines 143, 151). In drawer in frame ending (line 235). | New prop — correctly introduced per outline. |
| Don Eusebio's letter | Received (line 161), read (lines 167–191), placed in pocket (line 191). | New prop — correctly introduced per outline. |
| Rifle | In Martín's hands (lines 55, 155, 207, 227). | ✓ (Ch3–4: in hands) |
| Scapular on Tomás | "The scapular was on his chest" (line 225). | ✓ |

**Prop detail verification:**
- Pin description (line 131): "The yoke was on the left, the arrows on the right... The catch on the back was a simple clasp." Consistent with opening frame (line 5): "a catch on the back that gripped the wool." ✓
- Crucifix description (line 133): "wood, old, warm from the body, the groove under the thumb worn smooth by three generations." Consistent with Ch1 and character profile. ✓
- Don Eusebio's handwriting (line 165): "The letters were tall and narrow, the strokes straight, the pressure heavy." Consistent with "The Patriarch" register (don_eusebio.md: "measured, declarative, final"). ✓

---

## 7. ADDITIONAL CHECKS

### Character Voice Consistency
- **Tomás:** "It's a pin" / "There, done" / shrugs. Companion register. Pragmatic, physical, no ideology. ✓
- **Vidal:** "Listen." / reads decree from paper / face flat. Officer register. Professional, no decoration. ✓
- **Salazar:** Long, precise sentences. Falangist register. "The unification is not the death of your tradition. It is the birth of a greater one." Matches outline fixed dialogue (outline line 147). ✓
- **Don Eusebio (letter):** "The king was not consulted." / "I do not know what we are fighting for now." Patriarch register with bitterness bleeding through. ✓

### Outline Compliance
Outline for Ch5 (lines 49–53):
- ✓ Unification decree (February 17, 1937)
- ✓ Falange Española Tradicionalista y de las JONS
- ✓ Yoke-and-arrows alongside red beret
- ✓ Comandante Salazar arrives
- ✓ Salazar's speech: "The unification is not the death of your tradition. It is the birth of a greater one."
- ✓ Don Eusebio's bitter letter: "The king was not consulted."
- ✓ Tomás: "It's a pin. It doesn't change anything."
- ✓ Martín wears the yoke-and-arrows
- ✓ Emotional palette: [Betrayal], [Confusion]
- ✓ MIDPOINT position acknowledged in outline (line 53)

### Frame Device Consistency
- Opens: "I am at the table. The inkwell is full." (line 3) — consistent with Ch1–4 frame openings.
- Closes: "I am at the table. The inkwell is full. The pen is in my hand." (line 233) — consistent.
- Frame content: "The pin is in a drawer. It has been in the drawer for thirty years." (line 235) — the older narrator reflecting. Consistent with the writing-as-reckoning frame established in Ch1.

---

## STATE-FILE UPDATE NOTES (for book-runner)

The following state files require updating after Ch5 is committed:

1. **project_state.json** — stale since Ch2. Must update:
   - `martin.location`: "reserve line west of Madrid"
   - `martin.knowledge`: add Army of Africa, failed assault, first kill, unification decree, Salazar, yoke-and-arrows
   - `martin.physical_state`: "crucifix in pocket, beret on head with yoke-and-arrows pin"
   - `salazar.location`: "with the battalion — Madrid front"
   - `salazar.active_registers`: ["The Falangist"]
   - `timeline_position`: "February 1937 — reserve line, Madrid"
   - `props_motifs.red_beret`: "on Martín's head with yoke-and-arrows pin"
   - Add new prop: `yoke_and_arrows_pin`: "on Martín's red beret"

2. **reader_state.json** — must update to reflect Act II / misdirection cracking.

3. **timeline.json** — must add Ch5 entry: February 17, 1937, Madrid reserve line.

4. **callback_ledger.json** — must update:
   - `don_eusebio_letters`: status → "payoff" (Ch5)
   - `red_beret_01`: status → "payoff" (Ch5 is listed in payoff_chapters)
   - Add new seeds: `unification_decree_01`, `don_eusebio_bitterness_01`, `salazar_persuasion_01`

5. **convention_ledger.json** — remains empty. The chapter uses hands as primary body anchor (consistent with Ch1, Ch3). Should be populated on next full update.

---

## SUMMARY

| Check | Result |
|-------|--------|
| Knowledge-delta | PASS |
| POV-knowledge | PASS |
| Callback | PASS |
| Timeline | PASS |
| Reader-state | ADVISORY (stale state file) |
| Props | PASS |
| Voice consistency | PASS |
| Outline compliance | PASS |

**Verdict: ADVANCE.** The chapter is continuity-clean. Three advisory notes concern stale state files that must be updated post-commit. No manuscript-level violations detected.
