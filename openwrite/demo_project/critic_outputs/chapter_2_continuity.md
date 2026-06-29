# Continuity Critic Report — Chapter 2: The March South

**Critic:** Continuity  
**Chapter:** 002_the_march_south.md  
**State files consulted:** project_state.json, callback_ledger.json, convention_ledger.json, reader_state.json, timeline.json  
**Bible files consulted:** 04_outline.md, 03_characters/martin.md, 03_characters/tomas.md, 03_characters/vidal.md, 03_characters/padre_joaquin.md  
**Prior chapter consulted:** 001_the_red_beret.md

---

## VERDICT: CONDITIONAL PASS — 1 blocking violation, 1 advisory

---

## 1. KNOWLEDGE-DELTA CHECK (HIGHEST PRIORITY)

### No violations found.

Martín's retrospective narration about Vidal is explicitly framed:

> "Later I learned what had happened. Vidal had been sent by the Army — the regular Army, the professional force — to organize the requeté battalion into something that could function as a military unit." (lines 107)

The knowledge that Vidal served in the Rif and at Toledo is presented as acquired knowledge, not immediate perception. This is consistent with the retrospective frame — the older Martín writing decades later.

Martín's knowledge of the meseta ("I had heard of the meseta. My father had spoken of it," line 15) is consistent with his established backstory as a hardware store son who had not traveled.

---

## 2. POV-KNOWLEDGE-AS-NARRATION CHECK

### ADVISORY — borderline interiority of non-POV character

**Location:** Lines 103–104  
**Quote:** "the face of a man who had seen the Rif mountains and the barracks of Toledo and the politics of the Republic and who had learned that the face was a tool and the tool's job was to reveal nothing"  
**Category:** POV — interiority of non-POV character  
**Severity:** Advisory (borderline)

The phrase "who had learned that the face was a tool" describes Vidal's internal understanding, not something observable. While the Rif and Toledo references are recoverable through later knowledge, the internalized lesson about the face as a tool is pure interiority. The retrospective frame ("later I learned") does not fully cover this because Martín could learn *about* Vidal's service but not *what Vidal internally concluded* about managing his face. Suggest recasting as Martín's inference: "the face of a man who had spent a decade in uniform and who treated his own expression the way a soldier treats his rifle — maintained, cleaned, never left where the enemy could find it."

---

## 3. TIMELINE CHECK

### BLOCKING — Magdalene feast date error

**Location:** Lines 25  
**Quote:** "We reached the village on the twenty-third. I remember the date because it was the day before the Magdalene — July twenty-two, the eve of her feast."  
**Category:** Factual / Timeline error  
**Severity:** Blocking  
**State reference:** timeline.json — Ch1 is July 18; Ch2 outline is "July–August 1936"

The feast of Mary Magdalene is **July 22**. The text states the village was reached on "the twenty-third" and calls it "the day before the Magdalene — July twenty-two, the eve of her feast." This is internally contradictory:

- If the arrival date is July 23, then the Magdalene (July 22) has already passed — it is the day *after*, not the day *before*.
- If the intent is that July 22 is the eve of the Magdalene, the Magdalene would have to be July 23, which is incorrect.
- The phrase "July twenty-two, the eve of her feast" implies the feast is July 23, but the Magdalene feast is July 22.

**Recommended fix:** Either change the arrival date to July 21 (true eve of the Magdalene) or change the reference entirely. Example: "We reached the village on the twenty-second, the feast of the Magdalene."

### Timeline consistency (no other issues)

- Chapter 1 ends with departure from Pamplona on July 18 (late afternoon). Chapter 2 opens with the train on July 19 — consistent. The battalion likely marched to the station or camped overnight.
- Feast of Santiago (July 25) is correctly placed on line 83.
- The sequence train → village → road march → second village is internally consistent.

---

## 4. CALLBACK CHECK

### No violations found.

| Callback | Seed (Ch1) | Ch2 Status | Assessment |
|----------|-----------|------------|------------|
| crucifix_01 | Don Eusebio gives crucifix | Present: "the crucifix in my pocket" (line 79), "touched the crucifix my father had given me" (line 91), "the crucifix under my pillow" (line 223) | Consistent. Maintained as body-object. |
| red_beret_01 | Martín puts on beret | Present: "the wool of the beret on my head" (line 79), "the beret pressed against my forehead" (line 89), "He took off his beret" (line 29, Tomás) | Consistent. |
| scapular_01 | Tomás's scapular cord | Not explicitly mentioned in Ch2 | Acceptable — not every scene requires it. Tomás is described in action (sleeping, eating, talking), and the scapular is under his collar. |
| padre_joaquin_blessings_01 | Pastoral certainty | Present: "He blessed the train. He blessed the tracks. He blessed the direction — south" (line 19); "He blessed the road" (line 89); Santiago Mass (line 85) | Consistent. Blessings are confident, rote — the pastoral certainty register. |
| tell_my_mother_01 | Tomás's mother | Present: "Write to my mother. Tell her I'm well." (line 61); "Tell her I will come home." (line 69) | Consistent. Deepens the seed. |

---

## 5. READER-STATE CHECK

### No violations found.

**Current state (from reader_state.json):** misdirection_active, Act 1.  
**Outline expectation for Ch2:** "The reader should feel the breadth of the Nationalist coalition — and the first hint that the Carlist cause is one voice among many, not the voice."

Chapter 2 delivers this through:
- The farmer who doesn't know what the fueros are (lines 159–201)
- Tomás's indifference to the cause ("We fight. We win. We go home." — line 219)
- Martín's growing unease ("the coalition is broad. The cause is wide." — line 201)

The retrospective warnings ("I did not know that the breadth was the danger," line 203) are consistent with the misdirection framework — the older narrator foreshadows, but the boy in the scene still believes.

---

## 6. PROPS CHECK

### No violations found.

| Prop | Location in Ch2 | Consistency |
|------|----------------|-------------|
| Wooden crucifix | Pocket (line 79, 91, 197, 223) | Consistent with Ch1 (pocket) and state file. |
| Red beret | On head (lines 79, 89, 229, 231) | Consistent. |
| Mauser rifle | On shoulder/back (lines 109, 121, 229) | Consistent with Ch1 (issued at cuartel). |
| Tomás's pack | Present with inscription (line 3, 73) | New detail — inscription on inside flap. Consistent with Ch1 pack description ("already bulging"). |
| Letter to father | Written at second village (lines 153–157) | New prop. Consistent with Martín's voice register and relationship. |

---

## SUMMARY

| Category | Violations | Severity |
|----------|-----------|----------|
| Knowledge-delta | 0 | — |
| POV-knowledge-as-narration | 1 | Advisory |
| Timeline | 1 | **Blocking** |
| Callbacks | 0 | — |
| Reader state | 0 | — |
| Props | 0 | — |

**Blocking item:** The Magdalene feast date reference (line 25) is internally contradictory and factually incorrect. Must be fixed before the chapter can pass.

**Advisory item:** Vidal's interiority at line 103–104 ("who had learned that the face was a tool") exceeds Martín's POV even under retrospective framing. Recommend recasting as observable inference.
