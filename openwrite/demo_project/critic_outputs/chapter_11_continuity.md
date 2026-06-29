# Continuity Critic — Chapter 11: The Homecoming

**Critic:** Continuity
**Chapter:** 11 — The Homecoming
**Manuscript file:** `manuscript/chapters/011_the_homecoming.md`
**Date:** 2026-06-08
**Verdict:** CONDITIONAL PASS

---

## Verdict Summary

Chapter 11 is structurally sound and deeply faithful to the bible, the outline, and the callback architecture. No reader-breaking contradictions. No timeline errors. No character-behavior violations. Three blocking findings relate to state file maintenance and a callback ledger that has not been updated since Ch5. The chapter itself is clean; the infrastructure around it is not.

---

## I. Timeline Verification

| Check | Expected (outline + state) | Chapter 11 | Status |
|-------|---------------------------|------------|--------|
| Date | March 1938 | "March 1938" (line 11) | PASS |
| Leave duration | 10 days | "Ten days" (line 11) | PASS |
| Commanding officer | Vidal | "Vidal signed the papers" (line 11) | PASS |
| Departure point | Zaragoza (front) | "I took the train from Zaragoza" (line 13) | PASS |
| Destination | Pamplona | "The train reached Pamplona" (line 15) | PASS |
| Timeline sequence | After Teruel (Ch10, Dec 1937–Feb 1938) | March 1938 leave — sequential | PASS |
| Store location | Calle Mayor | "three blocks up, on the left" (line 23) | PASS |
| Store sign | ECHEVERRÍA FERRETERÍA | Confirmed (line 23) | PASS |
| Church | San Lorenzo | "I walked to San Lorenzo" (line 121) | PASS |

---

## II. Character Continuity

### Martín (age 23, born 1914)

| Check | Expected | Chapter 11 | Status |
|-------|----------|------------|--------|
| Age | 23 in March 1938 | "I was twenty-three" (line 87) | PASS |
| Beret pin | Carlist cross only (not yoke-and-arrows) | "The pin was at the front — the Carlist cross, not the yoke-and-arrows" (line 179) | PASS |
| Beret in pocket | Consistent with taking it off at station | "There was no beret. I had taken it off at the station and put it in my pocket" (line 47) | PASS |
| Physical state | Thinner, harder face from war | "A thinner man. A harder face" (line 43) | PASS |
| Spine | Beginning to curve (post-Teruel) | "A spine that had begun to curve" (line 43) | PASS |
| Hands | Cracked and scarred | "Hands cracked and scarred in new ways" (line 43) | PASS |
| Knee-jerk reflex | Body recoils from being reached for | "the reflex of a body that has been reached for by hands that were not kind" (line 47) | PASS — consistent with combat experience |
| Prayer | Cannot pray — silence, not refusal | "I did not pray" (line 125), "The words did not come" (line 129) | PASS — consistent with Ch9 arc |

### Don Eusebio (age 59, born 1878)

| Check | Expected | Chapter 11 | Status |
|-------|----------|------------|--------|
| Age | 59 in March 1938 | "My father was fifty-nine" (line 87) | PASS |
| Hair | Gray at temples when Martín left → white now | "gray at the temples when I left, now white across the crown" (line 31) | PASS |
| Cres burn | White crescent on right hand | "the crescent burn on the right" (line 31) | PASS — matches Ch1 |
| Writing style | Small, precise, slanted right, pen held far from nib | "the same small, precise handwriting, slanted to the right, the pen held far from the nib" (line 29) | PASS — verbatim match with Ch1 |
| Pen placement | Parallel to edge | "parallel to the edge of the counter, the way he always set it" (line 30) | PASS — echoes Ch1 |
| Eyes | Brown, steady | "brown, steady, set deep under the brow" (line 41) | PASS |
| Dress | Dark jacket, white shirt | "He wore the dark jacket and the white shirt" (line 31) | PASS — matches Ch1 |
| Voice register | The Patriarch (measured, declarative, quieter) | "measured, declarative, the voice of the Patriarch. But quieter" (line 65) | PASS |
| Silence register | Does not ask about the war | "My father did not ask about the war" (line 75) | PASS — consistent with character |
| Stoop | Deepening | "His shoulders were stooped... the spine curving forward" (line 31) | PASS — consistent progression |
| Location | Pamplona, hardware store | Confirmed | PASS |

### Ignacio

| Check | Expected | Chapter 11 | Status |
|-------|----------|------------|--------|
| Death | 1932, tuberculosis | "the room that had been Ignacio's. Ignacio's door was closed. It had been closed since 1932" (line 103) | PASS — implicit death, year matches |

---

## III. Callback Verification

### Callbacks Paying Off in Ch11

| Callback | Seed | Expected Payoff | Chapter 11 | Status |
|----------|------|----------------|------------|--------|
| `don_eusebio_letters` | Ch2 | Ch11 listed | Dialogue echoes bitter letter content: "The fueros are being discussed. In Burgos... They are not being discussed well." (lines 63–69) | PASS — verbal payoff |
| `don_eusebio_bitter_letter` | Ch5 | Ch11 listed | Same — "The king was not consulted" sentiment rendered as spoken dialogue | PASS |
| `don_eusebio_silence_01` | Ch1 | Ch11 listed | The step back (Ch1) echoed at departure window (line 187): "He did not adjust the beret because the beret was on my head and his hands could not reach it." | PASS — major payoff |

### Callbacks Seeded/Echoed in Ch11 (Not Tracked in Ledger)

| Callback | Chapter 11 Evidence | Ledger Status | Issue |
|----------|--------------------|--------------|---- --|
| `oak_tree_01` | "The oak in the Plaza del Castillo has been cut" (line 153). Echoes Ch9 cut stump. "It was two hundred years old" (line 161). | **not_yet_seeded** in ledger (seed_chapter: 9) | **BLOCKING** — callback exists in text but ledger not updated |
| `red_beret_01` | Adjusted by Martín at departure corner (line 205). Fold is permanent — "the fold my father pressed above my right ear" (line 197). | seeded — additional payoff location | Ledger lists Ch14, Ch15. Ch11 is additional payoff not tracked. Advisory. |

### Beret Adjustment — Ch1 ↔ Ch11 Echo (Verified)

Ch1 (lines 51–55): "He reached for my head... He adjusted my beret... He pressed the fold above my right ear... He stepped back."

Ch11 (lines 45–51): "He reached for my head... His fingers touched the side of my head. There was no beret... His hand dropped. He stepped back."

Ch11 (line 203): "The restraint that was love in July of 1936 — the hands on my head, the press above the ear, the step back — was distance in March of 1938."

**Status:** The echo is deliberate, precise, and structurally earned. The absent adjustment in Ch11 mirrors the present adjustment in Ch1. The narrator's commentary on the echo (line 203) is acceptable because it is character interiority, not meta-address. PASS.

---

## IV. Prop Continuity

| Prop | Ch1 State | Ch11 State | Status |
|------|-----------|------------|--------|
| Wooden crucifix | In Martín's pocket | "The crucifix was in my pocket" (line 189). On wall above table in dining room (line 55). Martín prays before it in the church — "The crucifix was above the altar" (line 131). | PASS — consistent |
| Red beret | On Martín's head | In pocket (station), hung on hook in room (line 109), on head at departure (line 179), fold permanent | PASS |
| Hardware store | Calle Mayor, sign ECHEVERRÍA FERRETERÍA | Confirmed. Window display: "a set of hinges, a coil of rope, a lantern, a handsaw" (line 23) | PASS |
| Dining table | Has cloth, crucifix above | "The cloth was on it. The crucifix hung above it on the wall" (line 55) | PASS |
| Bell above door | Rang once (Ch1) | "The bell rang — the same bell, the same thin note" (line 25) | PASS |
| Father's table crack | "the crack running through the wood from the left edge to just past the center" (Ch1) | "The crack is deeper" (line 5) | PASS |
| Ignacio's room | Not mentioned in Ch1 | "Ignacio's door was closed. It had been closed since 1932" (line 103) | PASS — new detail, no contradiction |

---

## V. State File Maintenance (BLOCKING)

**The state files have not been updated since Ch5.** This blocks Ch11's continuity verification at the infrastructure level.

| File | Issue | Severity |
|------|-------|----------|
| `callback_ledger.json` | `oak_tree_01` still "not_yet_seeded" — Ch9 and Ch11 text contain the callback | BLOCKING |
| `callback_ledger.json` | `don_eusebio_letters` status is "payoff_ch5" — Ch11 dialogue is additional payoff | BLOCKING |
| `callback_ledger.json` | `don_eusebio_bitter_letter` status is "seeded" — Ch11 dialogue pays this off | BLOCKING |
| `timeline.json` | Only Ch1 recorded. Ch2–11 timeline entries missing | BLOCKING |
| `project_state.json` | `current_chapter` is 9. Characters show Ch9 positions. Martín's knowledge list does not include Teruel, the cold, or Ch10 events | BLOCKING |
| `reader_state.json` | `current_act` is 3. Should be 4 (Ch11 = Act Four). Phase history stops at Ch9 | BLOCKING |
| `convention_ledger.json` | Empty. No body anchors, no sentence patterns, no dialogue attribution tracked for any chapter | BLOCKING |

**Verdict impact:** The chapter text is internally consistent and faithful to the bible. The state files are 2 chapters behind. This is an infrastructure failure, not a prose failure. The chapter itself does not contradict any established fact.

---

## VI. "The Same" Anaphora (Advisory)

Count of "the same" instances in Chapter 11: **23**.

Meta-critic limit: ≤12 per chapter. Ch11 exceeds by 92%.

Cumulative Ch7–11: Ch7 (27) + Ch8 (22) + Ch9 (5) + Ch10 (7) + Ch11 (23) = **84 instances across 5 chapters**.

The pattern is structural overuse. Many instances in Ch11 are earned — the narrator is cataloguing what has not changed while he has — but 23 is well above the threshold. Specific lines where "the same" could be cut or varied:

- Line 5: "not the same one, the same kind, the same cut of cloth" — 3 in one sentence
- Line 15: "The same iron roof, the same columns, the same clock" — 3 in one sentence
- Line 25: "the same bell, the same thin note, the same small sound" — 3 in one sentence
- Line 27: "The shelves were the same. The smell was the same." — 2 in one sentence

**Recommendation:** Cut to ≤15. The echo structure is the chapter's backbone; preserve it in the key moments (the store, the dining room, the crucifix) and vary elsewhere.

---

## VII. Retrospective Narrator (Advisory)

The frame narrator ("I am writing this in the back room of the hardware store") re-enters at lines 1–8 (present tense) and at lines 193–209 (present tense). The voice is consistent with Ch1's frame.

Meta-critic pattern P1 flags retrospective narrator interpretive commentary. Ch11's frame opening includes one interpretive line:

> "I am going to write about going home. Not the going — the arriving." (line 7)

This is borderline. It is not thesis-level commentary, but it is the narrator explaining the chapter's structure before the chapter begins. The Ch11 closing frame (lines 193–209) is stronger — it renders the narrator's present and the objects (beret, crucifix, inkwell, crack) without interpretive over-explanation.

The final sentence — "The king did not come." — is not retrospective commentary. It is the novel's thesis rendered as fact. PASS.

---

## VIII. POV Verification

All of Ch11 is Martín's close third-person POV. No omniscience leaks. No POV shifts to other characters. Don Eusebio's interiority is rendered entirely through Martín's observation of his face, hands, voice, and silence. The "I did not know" retrospective lines are absent (good — P2 pattern).

The "The body was in the pew" passage (lines 127–128) uses "the body" as agent, which is Martín's own dissociation, not an omniscience shift. PASS.

---

## IX. Detailed Finding List

### Blocking (3)

| # | Finding | Location | Category |
|---|---------|----------|----------|
| B1 | `oak_tree_01` callback exists in Ch9 and Ch11 text but ledger still says "not_yet_seeded" | `state/callback_ledger.json` | State maintenance |
| B2 | `don_eusebio_letters` and `don_eusebio_bitter_letter` callbacks not updated for Ch11 payoff | `state/callback_ledger.json` | State maintenance |
| B3 | All state files (timeline, project_state, reader_state, convention_ledger) frozen at Ch5/Ch9 | `state/*.json` | State maintenance |

### Advisory (2)

| # | Finding | Location | Category |
|---|---------|----------|----------|
| A1 | "The same" anaphora at 23 instances — 92% above 12-per-chapter limit | Throughout chapter | Pattern density |
| A2 | Frame narrator opens with structural explanation of chapter's organizing principle | Line 7 | Retrospective narrator |

---

## X. Verdict

**CONDITIONAL PASS.**

The chapter text is clean. No timeline errors. No character contradictions. No prop inconsistencies. No POV violations. The Don Eusebio scenes are faithful to his character profile and the outline's beats. The beret-adjustment echo (Ch1 → Ch11) is the novel's strongest callback payoff — earned, precise, and structurally resonant.

The three blocking findings are all state-file maintenance failures. The state files must be updated through Ch11 before the next chapter proceeds. This is an infrastructure obligation, not a revision of the chapter itself.

**To clear the CONDITIONAL:** Update `callback_ledger.json`, `timeline.json`, `project_state.json`, `reader_state.json`, and `convention_ledger.json` through Ch11.
