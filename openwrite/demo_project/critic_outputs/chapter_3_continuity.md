# Continuity Critic — Chapter 3: "First Blood"

**Reviewed:** manuscript/chapters/003_first_blood.md
**State files:** All 8 state/*.json files loaded
**Cross-referenced against:** Chapters 1–2, bible/04_outline.md, all 7 character profiles, bible/07_format_rules.md
**Date:** 2026-06-06

---

## Verdict: CONDITIONAL PASS — 3 violations (1 blocking, 2 advisory)

---

## 1. KNOWLEDGE-DELTA CHECK (HIGHEST PRIORITY)

**Purpose:** Verify that Martín only references knowledge established in Ch1–2 and that no character acts on information they shouldn't have.

### Findings

**No knowledge-delta violations detected.** Martín's references to Pamplona life (cathedral, mantillas, processions), the Virgen del Pilar feast, Padre Joaquín, Vidal's sight-picture correction ("the way Vidal had taught me on the road, the bullet drops" — lines 59, directly echoing Ch2's "Aim at the top third. The bullet drops"), Tomás's pragmatic philosophy, and the hardware-store objects are all consistent with his established knowledge state.

### ⚠️ BLOCKING — "the letter from his mother" (line 171)

> "He checked his pack. He checked his canteen. The hands moved through the familiar inventory: the bolt, the magazine, the bread, the water, the scapular, the letter from his mother."

**Category:** Knowledge-delta / Props
**Location:** Line 171
**State-file reference:** resume_chapter_2.json → character_states.tomas: "beside Martín, pragmatism intact"
**Cross-reference:** Ch2 lines 59–73 — Tomás dictated a letter TO his mother. Martín wrote it. Tomás put it in his pack: "I folded the letter. I gave it to him. He put it in his pack" (Ch2 line 73).

**Problem:** The only letter associated with Tomás's mother is the letter he dictated TO her, written in Martín's hand. The text says "the letter from his mother" — implying a letter received from her. No such letter is established in Ch1–2, and no receipt of mail is described in the two-month gap between Ch2 and Ch3. This is either:
- A factual error: should read "the letter to his mother," or
- An unestablished prop: Tomás received a letter from his mother at some point during August–October 1936, which is plausible but never rendered or referenced.

**Fix:** Change "the letter from his mother" to "the letter to his mother" — or, if the received letter is intentional, seed it explicitly in the text (e.g., a brief mention of mail arriving at the billet).

---

## 2. POV-KNOWLEDGE CHECK

**Purpose:** Verify that the narration does not access information outside Martín's perception and knowledge.

### Findings

**No POV violations detected.** Two passages warrant comment but do not constitute violations:

- **Lines 121–122:** "He had not fired a shot. He had directed the attack from the edge of the olive grove, the binoculars up, the map open, the orders passed in short sentences." — Martín saw Vidal at the edge of the grove with binoculars before the attack (line 41). He can reasonably infer Vidal stayed there. Defensible.

- **Line 175:** "the shaking would return only once — at the end, at the Ebro, when Tomás was in my arms and his blood was on my hands" — This is a flash-forward by the retrospective narrator (old Martín writing in the hardware store). Consistent with the narrative frame established in Ch1–2 where the narrator knows the future. Not a POV violation within the established contract.

### Note on POV contract vs. outline

The outline (bible/04_outline.md) states: "Third-person limited, Martín's perspective exclusively." The manuscript uses first-person retrospective narration (established Ch1). This is a pre-existing deviation from the outline, not a Ch3-specific issue. Ch3 is consistent with the established manuscript voice.

---

## 3. CALLBACK CHECK

**Purpose:** Verify that all callbacks are tracked, seeded items are maintained, and no premature payoffs occur.

### Callback Status After Ch3

| Callback | Ch3 Status | Notes |
|----------|-----------|-------|
| crucifix_01 | ✅ Maintained | Lines 137, 143–144, 149, 151, 155 — in pocket, held in hands, prayed with. Consistent with seeded state. |
| red_beret_01 | ✅ Maintained | Lines 15, 79, 115, 127, 143 — on ground during Mass, on head during/after battle, under head as pillow. Consistent. |
| scapular_01 | ⚠️ **INCONSISTENCY** | See Props Check below. |
| don_eusebio_silence_01 | ✅ Seeded | No reference in Ch3. Not required. |
| padre_joaquin_blessings_01 | ✅ Extended | Lines 11–17 (Mass), 21–25 (rifle blessing). Pastoral certainty intact. Building toward Ch6 payoff. |
| tell_my_mother_01 | ✅ Maintained | Line 45: "the scapular his mother had sewed." Tomás's maternal connection preserved. |
| meseta_motif | ✅ Maintained | Line 11: "the village on the meseta." Line 33: "weeks of flat meseta." |
| vidal_competence | ✅ Extended | Lines 29–31 (map, orders), 41 (binoculars), 57 (return fire command), 77 (cease fire), 119–121 (post-battle assessment). Professional competence demonstrated through action. |
| don_eusebio_letters | ✅ Seeded | No reference in Ch3. Not required. |
| tomas_pragmatism | ✅ Payoff echo | Line 133: "The way he said I will come home. The way he said We fight, we win, we go home." Explicit callback to Ch2. |

### New Callback Seeds in Ch3

- **Tomás's cigarette sharing** (lines 91–103): Tomás lights a cigarette and offers it to Martín after the battle. A companion gesture that parallels the bread-sharing in Ch1. Potential future callback.
- **The man in the blue shirt** (lines 67–73): The man Martín kills. His image recurs in lines 129, 135, 147, 149. This is the first kill — a foundational trauma. Will need payoff in later chapters (the body's processing).

---

## 4. TIMELINE CHECK

**Purpose:** Verify dates, durations, and sequence consistency.

### Findings

| Element | Outline | Chapter | Status |
|---------|---------|---------|--------|
| Time period | September–October 1936 | Feast of Virgen del Pilar (October 12) + battle + next morning | ✅ Consistent |
| Sequence | First engagement → dig in → news of Madrid move | Same sequence rendered | ✅ Consistent |
| Duration | Not specified | ~2 days (Mass → battle → evening → morning briefing) | ✅ Plausible |
| Gap from Ch2 | Ch2 ends ~August 15 | Ch3 begins October 12 | ~2 months, handled implicitly: "After weeks of flat meseta, the land buckled" (line 33) | ✅ Acceptable |

### ⚠️ ADVISORY — Geographic direction: "north to the Madrid front" (line 161)

> "We are being moved," he said. "The battalion goes north to the Madrid front."

**Category:** Timeline / Geographic
**Location:** Line 161
**State-file reference:** project_state.json → timeline_position: "July 23 – August 15, 1936 — marching through Castile"
**Cross-reference:** Ch2 — the battalion marched SOUTH from Pamplona through Castile. The meseta is south of Pamplona. Madrid is further south/southwest of the meseta.

**Problem:** If the battalion is on the meseta (central Castile), Madrid is to the south or southwest. "North to the Madrid front" is directionally incorrect. The requeté would go south (or southeast) to reach Madrid. Historical context: the Nationalist advance on Madrid in late 1936 approached from the northwest (through the Sierra de Guadarrama) and the south (Army of Africa). The requeté would approach from the north/northwest — meaning they'd go south toward Madrid, not north.

**Fix:** Change "north to the Madrid front" to either "to the Madrid front" (removing the directional) or "south to the Madrid front."

---

## 5. READER-STATE CHECK

**Purpose:** Verify that the chapter maintains the current reader-belief phase and does not prematurely reveal future plot elements.

### Findings

**reader_state.json:** phase = "misdirection_active" — "The reader believes this is a war story about a young Carlist's crusade."

**Chapter 3 maintains the misdirection.** The first battle is rendered as a fact of war — the body's education, not the crusade's failure. Padre Joaquín's blessing remains authoritative (line 17: "God sees your sacrifice... The crusade is His work"). The requeté's faith holds. The killing is rendered as mechanics, not moral crisis. Tomás's pragmatism provides the human counterweight without questioning the cause.

**Line 175** contains a significant flash-forward:

> "I did not know that the numbness would grow, would thicken, would become the thing that carried me through the next village and the next and the next, through Madrid and the northern campaign and Teruel and the Ebro, through the killing and the dying and the blessing and the burying. I did not know that the shaking would return only once — at the end, at the Ebro, when Tomás was in my arms and his blood was on my hands..."

This foreshadows Tomás's death and the entire war's arc. Within the retrospective narrative frame (old Martín writing), this is structurally justified — the narrator knows the future. However, it does compress the novel's remaining arc into a single paragraph, potentially reducing the reader's investment in future chapters. This is a craft judgment, not a continuity violation. The misdirection phase is maintained: the reader knows something is coming but not how the crusade specifically fails.

**Verdict:** ✅ Reader state maintained.

---

## 6. PROPS CHECK

**Purpose:** Verify that all physical objects are tracked consistently across chapters.

### Props Audit

| Prop | Ch1 State | Ch2 State | Ch3 State | Status |
|------|-----------|-----------|-----------|--------|
| Wooden crucifix | In Martín's pocket (given by Don Eusebio) | In pocket, touched in church | In pocket (line 137), held in hands (lines 143–155) | ✅ |
| Red beret | On Martín's head (adjusted by Don Eusebio) | On head | On ground during Mass (15), on head (79, 115, 127), under head as pillow (143) | ✅ |
| Scapular | Cord around Tomás's neck, scapular under collar | Cord visible on neck | **In Tomás's pocket** (line 45), then pulled out and on chest (line 97) | ⚠️ **VIOLATION** |
| Rifle (Martín) | Mauser issued at cuartel | On shoulder | Checked (43), fired (61–75), beside him in trench (117, 143) | ✅ |
| Padre Joaquín's blanket | Over shoulders (Ch1) | Over shoulders (Ch2) | Over shoulders (line 13) | ✅ |
| Padre Joaquín's breviary | Not mentioned | Not mentioned | New prop — line 11: "marked it on his breviary with a pencil line" | ✅ New, plausible |
| Tomás's canteen | Not mentioned | Not mentioned | Lines 89, 131 — on belt, offered to Martín | ✅ New, plausible |
| Vidal's map/binoculars | Not present | Map case, binoculars, officer's cap | Map (29), binoculars (41) | ✅ |
| Tomás's cigarettes | Not mentioned | Not mentioned | Lines 91–93 — cigarette and match | ✅ New, plausible |

### ⚠️ MEDIUM — Scapular location inconsistency

**Ch1 line 109:**
> "A worn cord hung around his neck, the frayed end disappearing under his collar where a scapular would sit."

**Ch3 line 45:**
> "He reached into his pocket and took out the scapular his mother had sewed and touched it and put it back."

**Category:** Props / Callback
**Location:** Ch3 line 45
**State-file reference:** callback_ledger.json → scapular_01: "current_location": "on Tomás's neck"; resume_chapter_2.json → callback_state.scapular_01: "seeded — worn cord visible on Tomás"

**Problem:** Ch1 establishes the scapular on a cord around Tomás's neck, under his collar. Ch3 places it in his pocket. A scapular is worn on the body (cord over the shoulders, cloth pieces hanging front and back) — it is not a pocket object. The two descriptions are physically incompatible.

**Context within Ch3:** After being taken from the pocket (line 45), the scapular appears "outside his shirt now... it hung on his chest" (line 97), and later "His scapular was outside his shirt" (line 153). The progression (pocket → chest) contradicts Ch1 where it was always on his neck/chest.

**Fix:** Change line 45 from "He reached into his pocket and took out the scapular" to "He reached under his collar and pulled out the scapular" — maintaining the Ch1 established location (cord around neck, scapular under shirt).

---

## SUMMARY OF VIOLATIONS

| # | Severity | Category | Location | Description |
|---|----------|----------|----------|-------------|
| 1 | **BLOCKING** | Knowledge-delta / Props | Line 171 | "the letter from his mother" should be "the letter to his mother" — the only established letter is the one Tomás dictated TO his mother in Ch2 |
| 2 | ADVISORY | Geographic / Timeline | Line 161 | "north to the Madrid front" — Madrid is south of the meseta; should be "south" or direction removed |
| 3 | MEDIUM | Props / Callback | Line 45 | Scapular in pocket contradicts Ch1's cord-around-neck; should be pulled from under collar, not from pocket |

---

## ADDITIONAL OBSERVATIONS (non-violations)

1. **Temporal gap (Ch2 → Ch3):** ~2 months (August 15 → October 12) pass without explicit rendering. Handled implicitly by "After weeks of flat meseta, the land buckled" (line 33). Acceptable for a compression chapter.

2. **Comandante Etxeberria absence:** Ch2 introduces Etxeberria as battalion commander. Ch3 has Vidal giving all tactical orders without mentioning Etxeberria. Not a violation — Vidal commands the tactical element while Etxeberria may be at battalion HQ — but the silence is notable.

3. **New callback seeds:** The man in the blue shirt (first kill) and Tomás's cigarette sharing are well-seeded for future payoffs.

4. **Voice consistency:** All dialogue is character-accurate — Padre Joaquín's pastoral register, Tomás's pragmatic Companion register, Vidal's clipped Officer register. No voice bleed detected.

5. **Emotional palette match:** Outline specifies [Terror], [Numbness]. Chapter delivers: terror of first fire (lines 53–73), the shaking (lines 80–93), the numbness settling in (lines 127–136, 173–175). ✅

6. **Outline fidelity:** All outline beats are hit — Mass before attack, first kill, shaking, water from Tomás, digging in, crucifix/prayer at night, news of Madrid move. ✅
