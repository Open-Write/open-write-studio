# Continuity Critic — Chapter 10: The Cold

**Critic:** Continuity
**Chapter:** 10 — The Cold
**Date:** 2026-06-08
**Sources consulted:**
- `manuscript/chapters/010_the_cold.md` (169 lines)
- `manuscript/chapters/009_the_fallen_oak.md` (prior chapter)
- `bible/04_outline.md` (Ch10 entry + N±2)
- `bible/03_characters/martin.md`, `tomas.md`, `padre_joaquin.md`, `vidal.md`
- `state/callback_ledger.json`, `state/timeline.json`, `state/reader_state.json`
- `state/project_state.json`, `state/convention_ledger.json`
- `state/resume_chapter_9.json`
- `state/meta_critic_notes.md`

---

## VERDICT: CONDITIONAL PASS

3 blocking issues. 5 advisory findings. Chapter is structurally sound and emotionally effective but has three continuity errors that must be resolved before advancement.

---

## 1. KNOWLEDGE-DELTA

**What Martín now knows that he didn't before:**
- The physical reality of extreme cold as an occupying force in the body (Ch10 lines 19–20: "An occupation. First the extremities...")
- Vidal's cold-weather survival protocols — bolts inside greatcoats, body heat, grease lubrication (lines 64–65)
- What it looks like when a man freezes to death — Ibarra, the frost on the eyelashes, the frozen lids (lines 38–39)
- Padre Joaquín can bless the dead without sitting down — the machinery of blessing reduced to rote (lines 47–51)
- House-to-house fighting in frozen conditions — the sound of glass underfoot, the school with arithmetic on the blackboard (lines 125–131)
- The depth of Tomás's physical loyalty — blankets, bread, body heat, the face pressed against the neck (lines 113–119)

**Assessment:** Knowledge-delta is clean. All new knowledge is earned through direct experience. No information arrives from sources Martín cannot access.

---

## 2. POV-KNOWLEDGE

**POV contract (bible: third-person limited, Martín exclusively):**

Mostly clean. Two passages require scrutiny:

**ADVISORY — Line 49:** "I think he was afraid that if he sat down, he would not get up. I think the standing was the only thing keeping him vertical." This is Martín's speculation, framed with "I think." Permissible under the POV contract — Martín is reading Padre Joaquín's behavior and offering an interpretation. The "I think" framing is the correct hedge. However, the next sentence crosses slightly: "The cold had gone into his bones and his bones were holding him up through habit, through the muscle memory of fifty years of standing." This is more omniscient — Martín cannot know the priest's muscle memory or the internal mechanics of his body. The detail about "fifty years of standing" is Martín's inference from knowing Padre Joaquín's age, which is acceptable. Borderline. Flag for review.

**CLEAN — All other passages.** Tomás's interiority is rendered through behavior only (face still, hands steady, pressing his body against Martín's). Vidal's interiority is rendered through voice and action (lean face, moving eyes, dropped register). Padre Joaquín's interiority is rendered through what Martín observes (limp, breath, face, the decision not to sit).

**No omniscient exposition.** No future-tense knowledge leaks. No "the boy" variant. Clean on the meta-critic's P1 and P10 tracking.

---

## 3. CALLBACK TRACKING

### Callbacks that pay off in Ch10:

| Callback | Seed | Ch10 Payoff | Status |
|----------|------|-------------|--------|
| `vidal_competence` | Ch2 | Vidal's cold-weather protocols, the officer's meeting, "Dig deep" | ✅ PAYOFF |
| `padre_joaquin_blessings_01` | Ch1 | Blessings reduced to rote — same words, same breath, same hand on the blanket | ✅ PAYOFF |
| `shaking_stopping` | Ch3 | "My fingers were inside my gloves and every sensation was gone" (line 25) — numbness progression | ✅ PAYOFF |
| `first_kill` | Ch3 | "I shot him. He fell." (line 85) — second kill rendered with same spare construction | ✅ PAYOFF |

### Callbacks scheduled for Ch10 but NOT present:

| Callback | Seed | Scheduled | Status |
|----------|------|-----------|--------|
| `army_of_africa` | Ch4 | Ch10 | ❌ NOT PRESENT — No reference to Regulares/Legionnaires at Teruel. The Republicans are described generically. |
| `failed_assault` | Ch4 | Ch10 | ❌ NOT PRESENT — The Republic's surprise offensive at Teruel could echo the failed Nationalist assault on Madrid, but no callback connection is made. |
| `sounds_of_madrid` | Ch4 | Ch10 | ❌ NOT PRESENT — No auditory callback to Madrid's soundscape. The chapter's soundscape is new (frozen wire snapping, glass crunching, rifle reports in cold air). |

**Assessment:** The three missing callbacks are advisory, not blocking. The chapter establishes its own sensory world (cold, frost, frozen steel) without relying on Madrid callbacks. However, `failed_assault` has a natural structural parallel — the Republic's surprise offensive at Teruel mirrors the failed Nationalist assault on Madrid — that could deepen the irony if seeded.

### Callbacks seeded in Ch10:

None explicitly seeded. The chapter is a compression chapter — survival, not seeding.

---

## 4. TIMELINE

**Chapter date:** December 1937 – February 1938
**Prior chapter (Ch9):** August – October 1937
**Gap:** ~2 months (October → December 1937)

**Historical verification:**
- Battle of Teruel: December 15, 1937 – February 22, 1938. ✅ CORRECT
- Republic launched surprise offensive to take Teruel before Franco could respond. ✅ CORRECT (line 15)
- Franco's reinforcements arrived and retook the city. ✅ CORRECT (lines 123–125)
- The cold was historically severe — one of the worst winters in Spanish history. ✅ CORRECT

**Timeline sequence within chapter:**
- December 1937: March north from the Ebro into mountains around Teruel. ✅
- December 21: Reached the line. Republic had launched offensive three days before (Dec 18). ✅ HISTORICALLY CORRECT
- Christmas Eve: Republican attack. ✅
- January: Cold deepened. House-to-house fighting began in late January. ✅
- February: City retaken. ✅

**BLOCKING — Martín's age:** Line 151: "I was twenty-three." Martín was born in 1914 (character profile). In December 1937, he is 23. In February 1938, he turns 24 (assuming birthday in the first half of the year, which is unspecified). The statement "I was twenty-three" is placed in the retrospective narration after the fall of Teruel in February 1938. If Martín's birthday is before February, he would be 24. If after February, he is still 23. The character profile does not specify month of birth. **This is ambiguous and should be resolved.** Either specify the birth month in the character profile or adjust the line to "I was in my twenty-third year" or similar.

---

## 5. READER-STATE

**Current reader belief phase (from `reader_state.json`):** `misdirection_collapsed`
**Expected after Ch10:** The war is a machine. The crusade was the fuel.

**Assessment:** Chapter 10 delivers the expected reader-state transition. The outline specifies Act IV as "the truth: the war is a machine. The crusade was the fuel." The chapter achieves this through:
- The erasure of theology: "There was no theology here. There is no crusade. There is survival." (rendered through the chapter's absence of ideological content, not through stated thesis)
- The reduction of the world to physical need: blankets, body heat, bread, staying awake
- Padre Joaquín's blessings stripped to machinery: "He stood, he knelt, he spoke, he rose."

**No reader-state violations.** The chapter does not reveal information the reader shouldn't have. It does not collapse future knowledge into the present. The retrospective narrator ("I am writing this in the back room of the hardware store") maintains the frame.

---

## 6. PROPS

### Prop tracking:

| Prop | Location in Ch10 | Consistency |
|------|-------------------|-------------|
| **Wooden crucifix** | Line 169: "The crucifix in my pocket." | ✅ Consistent with Ch9 (breast pocket) |
| **Red beret** | Line 161: "The red beret on my head." Line 147: "His red beret was white with frost" (Tomás). | ✅ Present |
| **Tomás's scapular** | NOT MENTIONED | ⚠️ ADVISORY — The scapular is established as "on Tomás's chest" (callback_ledger). In winter, under a greatcoat, it would not be visible. Acceptable absence, but the chapter could acknowledge it in an intimate moment (e.g., when Tomás presses his face against Martín's neck, line 117). |
| **Yoke-and-arrows pin** | NOT MENTIONED | ❌ **BLOCKING** — The pin was established in Ch5 as forced onto the beret. In Ch9, Tomás's beret has "a brass yoke-and-arrows pin on the band" (line 11). In Ch10, the beret is mentioned multiple times but the pin is never referenced. At the end (line 161), "The red beret on my head" — no mention of the pin. This is a prop continuity error. The pin should be visible on Martín's beret. |
| **Alphabet chart** | NOT MENTIONED | ⚠️ ADVISORY — Established in Ch8 as "folded in Martín's jacket." Not referenced. Acceptable in a chapter focused on survival, but the jacket detail could anchor the physical object. |
| **Tomás's blanket(s)** | Complex — see below | ❌ **BLOCKING** — See finding below. |
| **Padre Joaquín's leather pouch** | Line 95: "He had his leather pouch — the communion wafers, the wine, the prayer book." | ✅ Consistent with Ch9 |
| **Padre Joaquín's limp** | Lines 41, 49, 141 — referenced multiple times | ✅ Consistent. "Childhood injury" per character profile. |
| **Padre Joaquín's cassock** | Line 41: "His cassock was under the military blanket." Line 99: visible when he blesses. | ✅ Consistent |

### BLOCKING — Tomás's blanket continuity:

The chapter contains a prop contradiction regarding Tomás's blankets:

1. **Line 27:** "Tomás pulled the blanket from his own shoulders and put it over me. He pulled a second blanket — I never learned where he got it — and wrapped it around my legs."
   - Tomás gives away TWO blankets to Martín. He now has ZERO blankets.

2. **Line 113:** "He wrapped my feet in strips of cloth torn from his blanket when my boots cracked."
   - Tomás is tearing "his blanket" into strips. But he gave both blankets to Martín. Which blanket is being torn?

3. **Line 153:** "Tomás had torn his blanket into strips for my feet and for wrapping the rifle bolts and for covering the frozen dead. His blanket was half its original size."
   - This implies Tomás has a blanket that is being progressively torn apart. But the blankets were given to Martín in lines 27.

**Possible readings:**
- (a) Tomás acquired a third blanket at some point (unstated).
- (b) The "strips of cloth torn from his blanket" in line 113 refers to one of the blankets Tomás gave to Martín — i.e., Martín is now tearing the blanket Tomás gave him. But the possessive "his blanket" (Tomás's) is ambiguous.
- (c) The second blanket (the mysterious one) was torn into strips before being given to Martín, and the strips were used for feet/bolts/dead.

**Resolution needed:** The blanket logic must be clarified. The simplest fix: Tomás had one blanket (not two), which he shares with Martín in the trench (covering both of them), and which he progressively tears into strips for various survival uses. The "second blanket" detail creates an unresolvable continuity problem.

---

## 7. ADDITIONAL FINDINGS

### ADVISORY — Padre Joaquín's age/physicality consistency:
Character profile says Padre Joaquín was born 1886, making him 51–52 during Ch10. Line 49 references "the muscle memory of fifty years of standing." This is approximately correct but imprecise. Minor.

### ADVISORY — Etxeberria surname:
Line 63: "A section leader named Etxeberria." The surname Etxeberria is also used for Amaia (Ch8). Different individuals sharing a surname in the same battalion is plausible in a Navarrese requeté unit (common Basque surnames), but the reader may conflate them. Consider a different surname or a clarifying detail.

### ADVISORY — Frame-narrator return:
The chapter opens and closes with the hardware-store frame. The opening ("I am writing this in the back room of the hardware store") enters through the cold of the table — a new sensory detail (the cold of wood on forearms). This is CLEAN per meta-critic refinement note #3 ("each 'I am at the table' return must enter through a new sensory detail"). The closing returns to the road, the crucifix, the beret — standard frame closure.

### ADVISORY — "I never understood why he did this. I never asked." (line 114):
This is a variant of the "I did not know" refrain tracked in meta-critic P2. The cumulative count is now 20+ instances across 10 chapters. The meta-critic limit is 1 instance per chapter. This chapter has the "I never" variant, which counts toward the same limit. Flag for naturalism critic.

### ADVISORY — Tomás calls Martín "cura" (line 113):
"Stay awake, cura." This is consistent with the character profile (Tomás calls Martín "cura" as a nickname). First use since Ch1–3. Clean callback to Tomás's voice register.

---

## 8. PROSE-LEVEL CONTINUITY (meta-critic pattern tracking)

These are not strictly continuity findings but are tracked here per meta-critic protocol:

| Pattern | Ch10 Count | Limit | Status |
|---------|-----------|-------|--------|
| "The same" anaphora | ~10 instances | ≤12/chapter | PASS (barely) |
| Triplet/triadic parallel | ~15+ sequences | ≤10/chapter | FAIL |
| Polysyndeton chains | ~12 lines with 3+ "and" | ≤8/chapter | FAIL |
| "I did not know" / "I never" refrain | 1 (line 114) | ≤1/chapter | PASS |
| Em-dashes | ~15 | ≤1.5/page (~22) | PASS |
| "Not X but Y" construction | 0 | 0 | PASS |
| Named emotions | 0 | 0 | PASS |

**Note:** The triplet and polysyndeton counts are consistent with the regressed pattern identified in meta-critic P4 and P9 (Ch9 at 41+32). Ch10 continues the trend. This is a prose-level issue for the naturalism critic, not a continuity error.

---

## SUMMARY

| Category | Finding | Severity |
|----------|---------|----------|
| Props | Yoke-and-arrows pin absent from beret references | BLOCKING |
| Props | Tomás's blanket logic contradictory (gives 2 away, then tears "his" into strips) | BLOCKING |
| Timeline | Martín's age ("twenty-three") ambiguous in February 1938 context | BLOCKING |
| Callbacks | 3 of 3 scheduled callbacks absent (army_of_africa, failed_assault, sounds_of_madrid) | ADVISORY |
| Props | Tomás's scapular not mentioned (acceptable under winter clothing) | ADVISORY |
| POV | Padre Joaquín's "muscle memory" line borderline omniscient | ADVISORY |
| Refrain | "I never understood / I never asked" = variant of P2 refrain (cumulative 20+) | ADVISORY |
| Naming | Etxeberria surname shared with Amaia — potential reader confusion | ADVISORY |

**Verdict: CONDITIONAL PASS.** Resolve the 3 blocking issues (pin, blankets, age) before advancing. Advisory findings are noted for other critics.
