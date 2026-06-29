# Continuity Critic — Chapter 15: The Altar

**Date:** 2026-06-08
**Scope:** Factual, prop, timeline, and callback continuity against prior chapters, bible, and state files

---

## Verdict: FAIL — 1 BLOCKING, 3 ADVISORY

---

## BLOCKING FINDINGS

### B1. Don Eusebio Death Year — Hard Contradiction

**Location:** Line 153 — "My father died in 1951. Twelve years after the war."

**Contradiction:**
- Ch1, line 5: "It has been mine since my father died in 1958"
- Ch11, line 203: "My father died in 1958."

Ch15 says 1951. Ch1 and Ch11 say 1958. Both cannot be true.

**Cascading damage:** The "twelve years after the war" arithmetic works only with 1951 (1939 + 12 = 1951). With 1958, the gap is nineteen years. The sentence "He had said nothing for twelve years" is bound to the wrong date. If the death year is corrected to 1958, the entire "twelve years" passage (lines 153–156) must be rewritten.

**Additionally:** The frame narrator in Ch1 is writing ~1962 (age 56 if born ~1914, or adjusted per the frame's internal dating). If Don Eusebio died in 1958, the narrator returned to the store in 1962 — consistent with Ch1 ("I did not come back to it until 1962"). If Don Eusebio died in 1951, there is an 11-year gap between his death and the narrator's return that is unexplained.

**Required fix:** Align Ch15 with Ch1/Ch11. Death year = 1958. Rewrite "twelve years" to "nineteen years." Adjust all dependent language (e.g., "He had said nothing for twelve years" → "He had said nothing for nineteen years").

---

## ADVISORY FINDINGS

### A1. Aoiz Distance Discrepancy

**Location:** Line 29 — "the twenty-seven kilometers south"

**Prior text:** Ch12, line 183 — "Thirty kilometers south."

Ch12 says 30 km (by bus). Ch15 says 27 km (by bicycle). Plausible that cycling and bus routes differ in distance. Not blocking, but inconsistent if both refer to the same road.

**Recommendation:** Harmonize to one distance, or accept the discrepancy as route-dependent.

### A2. Scapular Scene Retelling — Overlap with Ch12

**Location:** Lines 30–57 (the Aoiz visit)

Ch12, lines 183–197 already renders the full Aoiz visit: Martín takes the bus, gives the scapular, says "Tomás asked me to give you this," the mother says "Thank you," closes the door. Ch15 retells the same visit with different details — bicycle instead of bus, "He was brave" instead of "Tomás asked me to give you this," the mother does not speak, the scapular is placed on the table rather than handed directly.

**Problem:** Two incompatible accounts of the same event. Ch12 is the earlier, more compressed version. Ch15 is the fuller, more emotionally developed version. They disagree on:
- Mode of transport (bus vs. bicycle)
- Dialogue ("Tomás asked me to give you this" vs. "He was brave. He was my friend.")
- Physical delivery (handed at door vs. placed on kitchen table)
- Mother's response ("Thank you" + door closed vs. silent, takes scapular to chest)
- Setting (hallway vs. kitchen)

**Recommendation:** One version must be canonical. Ch15 is the final chapter and carries the emotional weight. Revise Ch12 to remove the detailed Aoiz visit or reduce it to a forward reference ("I would go to Aoiz. I would give her the scapular. That is for another chapter."). Alternatively, revise Ch12 to match Ch15's version.

### A3. Frame Narrator Age Consistency

**Location:** Line 5 — "I am fifty-six years old"

Ch1 establishes the narrator is 56, writing in the back room of the hardware store. Ch15 also says 56. If both are written at the same time (the frame is a single writing session), this is consistent. But Ch15's reference to events in 1951 and 1956 ("seventeen years" after 1939 = 1956) suggests the narrator is looking back from a later date. The frame needs to be internally consistent about when the writing occurs.

**Note:** If the narrator is 56 in ~1973 (born 1917, war at age 22 in 1939), and the father died in 1958, then the narrator has been running the store since 1962 — all consistent with Ch1. The 1951 date in Ch15 is the only thing that breaks this. Fix B1 and A3 resolves.

---

## CALLBACK VERIFICATION

| Callback | Seed | Ch15 Payoff | Status |
|----------|------|-------------|--------|
| Wooden crucifix (Ch1) | Don Eusebio gives Martín | Returned to wall above dining table (line 65, 71–73) | ✓ PAID OFF |
| Red beret (Ch1) | Don Eusebio adjusts | Hung on hallway hook (line 85–89) | ✓ PAID OFF |
| Tomás's scapular (Ch1/Ch8) | On Tomás's chest | Returned to mother in Aoiz (lines 39–49) | ✓ PAID OFF |
| "Tell my mother" (Ch12) | Unfinished sentence | Completed by Martín's visit (lines 30–57) | ✓ PAID OFF |
| Amaia's school (Ch8) | Closed school, banned language | Letter from exile (lines 103–121) | ✓ PAID OFF |
| Don Eusebio's silence (Ch1) | Step back, no embrace | Twelve/nineteen years of silence, death without words (lines 151–156) | ✓ PAID OFF (fix year) |
| Yoke-and-arrows (Ch5) | Pin on beret | Badge on beret, ghost of star beneath (lines 19, 81, 85) | ✓ PAID OFF |
| Oak tree (Ch9) | Cut stump | Not directly referenced in Ch15 | ✗ NOT PAID OFF |
| Padre Joaquín's blessings (Ch13) | "I am not sure these are the same blessing" | Not directly referenced in Ch15 | ✗ NOT PAID OFF |
| First kill (Ch3) | Man in the blue shirt | Not directly referenced in Ch15 | ✗ NOT PAID OFF |
| Body prayer (Ch3) | Hands, breath, dark | Not directly referenced in Ch15 | ✗ NOT PAID OFF |

**Note:** The outline (bible/04_outline.md, line 131) lists "The oak tree (Ch9 → Ch15): The cut stump in the Basque village, the implied roots beneath." Ch15 does not reference the oak tree. The outline also lists Padre Joaquín's blessings as ending at Ch13, so that callback's absence in Ch15 is expected. The first kill and body prayer callbacks list Ch15 as a payoff chapter in the callback ledger but are not present — these were seeded in Ch3 and may be optional given Ch15's emotional register.

---

## STATE FILE INCONSISTENCIES

### S1. Pipeline Status Outdated

`state/pipeline_status.json` lists chapters 1–12 as complete and next chapter as 13. Chapters 13–15 have been written but are not reflected in the status file.

### S2. Project State Outdated

`state/project_state.json` lists `current_chapter: 9` and `chapters_completed: [1–9]`. Chapters 10–15 are missing.

### S3. Callback Ledger Outdated

`state/callback_ledger.json` shows "oak_tree_01" and "amaia_school_01" as "not_yet_seeded" despite their seed chapters (8, 9) being written. Several callbacks show `status: "seeded"` when they should show `status: "paid_off"` for chapters already written.

### S4. Timeline Missing Entries

`state/timeline.json` has only Chapter 1's entry. Chapters 2–15 are missing from the timeline.

### S5. Reader State Outdated

`state/reader_state.json` shows `current_act: 3` and only tracks chapters 1–9. Act 4 (Ch10–12) and Act 5 (Ch13–15) are untracked.

---

## STRUCTURAL NOTES

### The Frame Narrative Ch15 Establishes

Ch15 introduces a present-tense frame ("I am here again. At the table.") that is the same frame as Ch1 but deepens it. The narrator is now explicitly aware of the three objects (crucifix, letter, beret) as the novel's structural anchors. The frame is clean and consistent with Ch1's frame — same room, same inkwell, same crack, same thumb. The seventeen-years-later reference (line 147: "The letter has been on the table for seventeen years") places the frame at 1956 if the letter is dated February 1939. This is internally consistent with the narrator being 56 if he was born in 1900 (1939 - 22 = 1917... actually, the narrator says he was 22 in Ch1 in 1936, so born 1914, making him 56 in 1970 — but 1939 + 17 = 1956, which would make the narrator 42). The "seventeen years" and "fifty-six years old" cannot both be true unless the frame writing occurs at a different time than the letter's placement on the table. This is not blocking but is worth noting for frame consistency.

---

## SUMMARY

| Category | Blocking | Advisory |
|----------|----------|----------|
| Factual contradiction | 1 (death year) | 1 (Aoiz distance) |
| Scene retelling conflict | 0 | 1 (Aoiz visit) |
| Frame consistency | 0 | 1 (age/timeline) |
| State file sync | 0 | 5 (all outdated) |
| Callback gaps | 0 | 2 (oak tree, first kill/body prayer) |

**The blocking finding (B1) must be resolved before the chapter can pass continuity review.** The Don Eusebio death year contradiction between Ch15 (1951) and Ch1/Ch11 (1958) is a reader-breaking factual error in the novel's final chapter.
