# Continuity Critic — Chapter 12: The River

**Chapter:** `manuscript/chapters/012_the_river.md`
**State files reviewed:** `callback_ledger.json`, `convention_ledger.json`, `timeline.json`, `project_state.json`, `pipeline_status.json`, `resume_chapter_9.json`
**Prior chapters cross-referenced:** Ch1, Ch3, Ch4, Ch5, Ch8, Ch9, Ch10, Ch11
**Character profiles:** `bible/03_characters/tomas.md`
**Outline:** `bible/04_outline.md`

---

## CRITICAL FINDINGS

### 1. IBARRA IS DEAD — Resurrection Error [BLOCKING]

**Severity: CRITICAL — blocks advancement**

Ibarra dies in Chapter 10 (The Cold) at Teruel. He freezes to death in the trench:

> "His name was Ibarra. From Pamplona, a year older than me, a carpenter's son. His mates said he went to sleep without a word. Sat down, pulled his blanket around his shoulders, closed his eyes. In the morning they touched him and he was stiff." — Ch10, line 39

In Chapter 12, Ibarra appears alive twice:

- **Line 15:** "He had taken the extra ammunition belt from Ruiz, who had a bad knee, and the blanket roll from Ibarra, who was seventeen and could barely carry his own rifle."
- **Line 45:** "I saw him give his canteen to Ibarra — the seventeen-year-old, the boy — and drink nothing for an entire afternoon."

Additionally, the character details conflict:
- Ch10: Ibarra is "from Pamplona, a year older than me" (i.e., ~23 at the Ebro)
- Ch12: Ibarra is "seventeen"

This is either a different Ibarra (which needs explicit clarification) or a resurrection of a dead character. The name is uncommon enough that a reader tracking the manuscript will catch this immediately.

**Resolution options:**
1. Replace "Ibarra" in Ch12 with a different name (e.g., a replacement recruit who arrived after Teruel).
2. If this is meant to be a different Ibarra, add a distinguishing detail (first name, origin town) to disambiguate.

---

### 2. TIMELINE INVERSION — Tomás Dies After the Withdrawal [BLOCKING]

**Severity: CRITICAL — blocks advancement**

The chapter establishes Tomás's death on **November 3rd** (line 77: "November 3rd. A Wednesday."). But the withdrawal from the ridge is described as happening **in late October**:

> "In late October, the requeté were pulled from the line." — line 171

Tomás cannot die on November 3rd if the unit was pulled from the line in late October. The timeline is inverted.

**Resolution:** Either change "late October" to "late November" or change the death date from November 3rd to an earlier date (late October). Given the outline says "July–November 1938" and the requeté are "pulled from the line in October," the death date should likely be in late October, not November.

---

## MODERATE FINDINGS

### 3. RUIZ — New Character Without Introduction [ADVISORY]

Ruiz appears once (line 15: "the extra ammunition belt from Ruiz, who had a bad knee") and is never mentioned again. He has no prior introduction in any chapter. This is not a continuity error — the Ebro campaign brought replacements — but his appearance with a named physical detail (bad knee) and no prior presence is worth noting. Consider either introducing him briefly or using an unnamed reference.

---

## CALLBACK VERIFICATION

| Callback | Seed | Ch12 Status | Notes |
|----------|------|-------------|-------|
| `scapular_01` | Ch1 | **PAYOFF** | Recovered from Tomás's body, given to his mother in Aoiz. Matches outline: Ch1 → Ch4 → Ch12 → Ch15. Scapular described consistently: "Brown wool, frayed at the edges, the image of the Virgin faded" (matches Ch1, Ch3, Ch5, Ch8 descriptions). |
| `tell_my_mother_01` | Ch1 | **PAYOFF** | "Tell my mother —" (line 129). Unfinished. Matches outline exactly. Connects to Ch15 visit. |
| `vidal_competence` | Ch2 | **PAYOFF** | Vidal appears at lines 21-22, 55, 155-165. Professional, flat voice, consistent with all prior chapters. "He was a good soldier" — factual, report-like, matches register. |
| `sounds_of_madrid` | Ch4 | **PAYOFF** | Sound motif recurs: artillery, machine guns, aircraft described in layered detail (lines 31-33). Connects to Ch4's "artillery heartbeat, machine-gun breath." |
| `army_of_africa` | Ch4 | **PAYOFF** | Condor Legion, Italian Savoias, Republican Polikarpovs described (line 33). Aerial warfare as constant presence. |
| `tomas_pragmatism` | Ch2 | **PAYOFF** | "At least it's not Teruel" (line 67). Half-smile, shrug. Matches character profile: deflects with humor, practical. |
| `crucifix_01` | Ch1 | CARRIED | "I still carried the crucifix" (line 39). Present in pocket alongside scapular (line 147, 177, 199). Not a payoff chapter per ledger — correct. |

---

## PROPS & MOTIFS VERIFICATION

| Prop | Ch12 Status | Prior Chapters | Consistent? |
|------|-------------|----------------|-------------|
| Wooden crucifix | In Martín's pocket | Ch1 (given by Don Eusebio), Ch3 (held at night), Ch10 (implied), Ch11 (on wall in Pamplona) | ✅ |
| Tomás's scapular | Recovered, given to mother | Ch1 (cord visible), Ch3 (touched before battle), Ch4 (on chest while sleeping), Ch5 (on chest), Ch8 (frayed edge, origin story), Ch9 (visible at collar), Ch10 (mentioned), Ch11 (Martín confirms Tomás alive) | ✅ Described consistently as brown wool, frayed, Virgin image faded |
| Red beret | Not mentioned in Ch12 | — | ⚠️ Absent but not a conflict — chapter is Ebro combat, beret may be under helmet or irrelevant to scene |
| Shared blanket | Used to wrap Tomás's body | Ch10 (shared for warmth at Teruel) | ✅ Poetic inversion — blanket that kept him alive now wraps his body |

---

## CHARACTER VOICE & BEHAVIOR VERIFICATION

### Tomás
- **Voice registers used:** The Companion (humor, "At least it's not Teruel"), The Son ("Tell my mother —"), silent pragmatism (organizing water, digging channels)
- **Physical description:** Stocky, broad-shouldered, dark hair too long, large scarred hands — all match Ch1 and character profile
- **Behavior:** Carries others' loads (Ruiz's ammunition, Ibarra's blanket roll), organizes water, dictates letters to mother — all established patterns from Ch1-Ch11
- **Writing to mother:** "Tell my mother the food is not so bad. Tell her I am well. Tell her the heat is worse than the cold" — matches The Son register from character profile and Ch3/Ch5 letter scenes
- **Scapular touching before battle:** "he touched it before the mortar came" — matches Ch3, Ch4, Ch5 pattern
- **Death scene:** "Tell my mother —" unfinished sentence — matches outline exactly. Not heroic, not meaningful — matches character arc specification
- ✅ **Consistent** (aside from the Ibarra resurrection issue which affects Tomás's caregiving scene)

### Martín
- **Narrative voice:** First-person retrospective from hardware store (1962 framing) — consistent with Ch1, Ch10, Ch11 framing
- **Faith erosion:** "I still prayed — haltingly, the words coming slower each week" — continues trajectory from Ch11 ("words came haltingly")
- **Body knowledge:** "The body knows what the hand resists" — matches established body-anchored interiority
- **Refrain:** "I am looking. I am calling it." (lines 73, 201) — matches Ch1 closing ("I am looking.")
- ✅ **Consistent**

### Vidal
- **Voice:** Flat, professional, factual — "Dig deeper. The rock is soft on the north side. Mortars walk across this ridge every morning at six" — matches Ch2, Ch4, Ch6, Ch10
- **Behavior:** Quick count, assessment, calculation — same pattern as Ch4 ("He looked at us the way he always looked at men arriving at a position")
- **Death scene reaction:** "He was a good soldier" — flat, factual, a report filed. Matches professional register
- ✅ **Consistent**

---

## TIMELINE VERIFICATION

| Event | Ch12 Date | Historical Accuracy | Notes |
|-------|-----------|---------------------|-------|
| Ebro crossing | July 1938 | ✅ | Battle of the Ebro began July 25, 1938 |
| Ridge fighting | July–October 1938 | ✅ | Battle lasted until November 1938 |
| Republican counterattack | September 1938 | ✅ | Republicans launched counterattacks across the Ebro |
| Rain/cold | October 1938 | ✅ | Autumn weather change |
| Tomás's death | November 3rd | ⚠️ | Date itself plausible, but conflicts with "late October" withdrawal (see Finding #2) |
| Withdrawal | "Late October" | ⚠️ | Conflicts with November 3rd death date |
| Visit to Aoiz | 1939 (post-war) | ✅ | After the war ends |
| Return crossing | Night, after withdrawal | ✅ | Matches July crossing (symmetry) |

---

## STRUCTURAL VERIFICATION

### Outline Compliance
- ✅ Battle of the Ebro — correct setting, correct timeline span
- ✅ Martín and Tomás share a position on a ridge — matches outline
- ✅ Air war constant — German, Italian, Republican aircraft described
- ✅ Tomás killed by mortar round — "Not heroic. Not meaningful." — matches outline exactly
- ✅ "Tell my mother" — unfinished sentence — matches outline exactly
- ✅ Martín wraps him in blanket, marks position — matches outline
- ✅ 120 entered, 63 walked out — matches outline exactly
- ✅ Emotional palette: [Grief], [Desolation] — achieved
- ✅ Act Four closure — "END OF ACT FOUR" territory

### Chapter Count & Word Count
- Chapter 12 of 15 — correct position
- Estimated ~4,500–5,000 words — within target range for a key dramatic chapter

---

## VERDICT

**FAIL — two blocking continuity errors must be resolved before advancement.**

1. **Ibarra resurrection** — a character who died in Ch10 appears alive in Ch12 with conflicting biographical details.
2. **Timeline inversion** — Tomás dies November 3rd but the unit withdraws "in late October."

Both are mechanical errors that a careful reader will catch. The prose itself is strong — the death scene earns its weight, the callback architecture is well-executed, and Tomás's characterization is consistent with eleven chapters of establishment. But continuity is binary: it holds or it doesn't. These two findings break it.

**Recommended fix:**
1. Replace "Ibarra" in Ch12 lines 15 and 45 with a new name for a replacement recruit.
2. Change "In late October" (line 171) to "In late November" to preserve the November 3rd death date, OR change the death date to late October to preserve the withdrawal timing.

---

*Reviewed against: 11 prior chapters, 7 state files, 7 character profiles, full outline.*
