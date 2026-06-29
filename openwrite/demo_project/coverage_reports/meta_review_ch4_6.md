# Meta-Critic Synthesis — Chapters 4–6

**Scope:** 15 critic reports across 3 chapters
**Date:** 2026-06-07
**Prior synthesis:** Ch1–3 (state/meta_critic_notes.md)

---

## 1. Critic Quality Table

| Critic | Ch4 Verdict | Ch5 Verdict | Ch6 Verdict | Findings (total) | Key Strength | Key Weakness |
|--------|-------------|-------------|-------------|-----------------|--------------|--------------|
| Show-don't-tell | CONDITIONAL PASS (14) | REVISE (19) | CONDITIONAL PASS (13) | 46 | Catches narrator interpretation after rendering; identifies named emotions and omniscience leaks | None significant — most consistent critic |
| Voice | CONDITIONAL PASS | PASS | CONDITIONAL PASS | ~24 | Register differentiation; character distinctness; subtext analysis | Missed 6 Tier 1 banned constructions in Ch4 (all caught by naturalism) |
| Palette | PASS (8.2/10) | PASS | PASS | 0 blocking | Consistently strong; catches restraint violations; evaluates sensory texture | None significant |
| Continuity | CONDITIONAL PASS | ADVANCE | ADVANCE | 2 blocking | Cleanest critic; catches prop errors, state staleness, knowledge-delta | None significant |
| Naturalism | FAIL | CONDITIONAL PASS | REVISE | 4C+5M+3A, 1C+7M+2A, 4B+4A | Aggressive pattern density detection; catches mechanical issues no other critic flags | May over-flag justified patterns (e.g., combat polysyndeton) |

**Critic reliability ranking (Ch4–6):**
1. **Show-don't-tell** — highest finding count, catches what voice misses
2. **Naturalism** — catches mechanical patterns invisible to other critics
3. **Palette** — consistent PASS with specific craft praise
4. **Continuity** — cleanest; no manuscript violations, only state-file maintenance
5. **Voice** — strong on registers, weak on format-rule compliance (improving from Ch4 to Ch6)

---

## 2. Verdict Summary

| Chapter | Show | Voice | Palette | Continuity | Naturalism | Composite |
|---------|------|-------|---------|------------|------------|-----------|
| 4 — The Siege | CONDITIONAL PASS | CONDITIONAL PASS | PASS | CONDITIONAL PASS | **FAIL** | CONDITIONAL PASS (naturalism blocking) |
| 5 — The Yoke and the Arrows | **REVISE** | PASS | PASS | ADVANCE | CONDITIONAL PASS | CONDITIONAL PASS (show-don't-tell blocking) |
| 6 — The Field of Jarama | CONDITIONAL PASS | CONDITIONAL PASS | PASS | ADVANCE | **REVISE** | CONDITIONAL PASS (naturalism blocking) |

**Pattern:** No chapter passes all five critics. Each chapter has 1–2 blocking critics. Palette and continuity never block. Naturalism blocks in 2 of 3 chapters.

---

## 3. Recurring Issues (Cross-Chapter Patterns)

### R1. "Not X but Y" / "Not X. Not Y. Z." Banned Construction — CRITICAL, PERSISTENT

| Chapter | Count | Caught by |
|---------|-------|-----------|
| Ch4 | 5 instances | Naturalism (C2), Voice (6 Tier 1), Show (F10) |
| Ch5 | 0–2 (borderline) | Voice (borderline pass) |
| Ch6 | 4 instances | Voice (blocking), Show (implied) |

**Status:** NOT RESOLVED from Ch1–3. The construction appears in every chapter. Voice critic catches it inconsistently — Ch4 voice found 6 instances but still passed; Ch6 voice found 4 and flagged as blocking. The show-don't-tell critic catches related constructions (F10 in Ch4) but does not systematically scan for the banned pattern.

**Refinement:** All critics must scan for "Not X but Y" and "Not X. Not Y. Z." as a first-pass mechanical check. Voice critic should auto-fail any chapter with 3+ instances.

### R2. Em-Dash Density — REGRESSED

| Chapter | Density | Threshold | Status |
|---------|---------|-----------|--------|
| Ch4 | 2.64/250w | >2/250w | Exceeded |
| Ch5 | 2.4/250w | >2/250w | Exceeded |
| Ch6 | 58 total (~3.0/250w) | >2/250w | Blocking |

**Status:** REGRESSED from Ch1–3 synthesis (which reported "resolved: Ch3 = 0.25/250w"). Em-dash density has returned with force. Ch6 has 58 em-dashes in 277 lines — one every 4.8 lines. This is the most persistent mechanical fingerprint.

**Refinement:** Naturalism critic must continue flagging. Target: ≤2/250w. Ch7–9 revision must prioritize em-dash reduction.

### R3. "The Way" Comparison Density — PERSISTENT, WORSENING

| Chapter | Density | Threshold |
|---------|---------|-----------|
| Ch4 | 2.69/1k | ≤2/1k |
| Ch5 | 2.5/1k | ≤2/1k |
| Ch6 | 5 instances (blocking) | max 2 |

**Status:** WORSENING from Ch1–3 (Ch1: 0.71/1k, Ch2: 1.77/1k, Ch3: 0.70/1k). Ch4–6 all exceed the threshold. The pattern "the way a [noun] [verb]s" is a clear AI fingerprint.

**Refinement:** All critics should flag "the way" constructions. Naturalism continues primary tracking. Target: ≤2/1k words.

### R4. Triplet/Triadic Parallel as Default Rhythm — CRITICAL, PERSISTENT

| Chapter | Count | Caught by |
|---------|-------|-----------|
| Ch4 | 10+ instances | Naturalism (A2), Palette (7a) |
| Ch5 | ~12 instances | Naturalism (M7) |
| Ch6 | 10 instances (blocking) | Naturalism (blocking) |

**Status:** PERSISTENT. Every chapter defaults to three-beat lists when the prose has nothing specific to say. The pattern is most damaging in non-scenic passages (descriptions, transitions). It is sometimes earned (blessing sequences, combat) but overused as default rhythm.

**Refinement:** Naturalism continues primary tracking. Show-don't-tell should flag when triplets appear in non-earned contexts. Target: ≤5 per chapter in non-scenic passages.

### R5. Negative Construction Density — IMPROVING BUT ELEVATED

| Chapter | Density | Threshold |
|---------|---------|-----------|
| Ch4 | 19.2/1k | >15/1k = critical |
| Ch5 | 12.9/1k | >10/1k = moderate |
| Ch6 | 13.7% | >15% = concern |

**Status:** IMPROVING from Ch4 (critical) to Ch5–6 (moderate). But still above the <10/1k target set in Ch1–3 synthesis. The "did not / was not / could not" loop remains the default construction for rendering contrast.

**Refinement:** Naturalism continues tracking. Target: <10/1k by Ch9.

### R6. Chapter-Ending Narrator Intrusion — CRITICAL, PERSISTENT

| Chapter | Final 15% findings | Type |
|---------|-------------------|------|
| Ch4 | 3 findings (F12: "The boy is wrong," "sounds will go on for three years") | Authorial intrusion, historical knowledge assertion |
| Ch5 | 3 findings (#16 omniscience leak, #17 meta-commentary thesis, #14 refrain) | Omniscience, thesis statement |
| Ch6 | 4 findings (V10–V13: interpretation, omniscience, summary) | Interpretation after rendering |

**Status:** PERSISTENT from Ch1–3. The narrator (older Martín) consistently steps in during the final 15% to explain, interpret, or assert knowledge the character cannot have. This is the single most damaging pattern in the manuscript.

**Refinement:** All critics must treat final 15% as high-risk zone. Show-don't-tell and naturalism should apply doubled scrutiny to chapter endings. Any passage in the final 200 words that names emotions, explains scenes, or delivers thesis = automatic flag.

### R7. "I Did Not Know" Cross-Chapter Refrain — ESCALATING

| Chapter | Instances | Max allowed |
|---------|-----------|-------------|
| Ch4 | 4 (critical) | 1 |
| Ch5 | 1 (at max) | 1 |
| Ch6 | 2 (blocking) | 1 |

**Cross-chapter total (Ch1–6):** 15+ instances across 6 chapters.

**Status:** ESCALATING. The phrase functions as the narrator's retrospective admission, but at 15+ instances across 6 chapters it has become a mechanical tic rather than a earned refrain. Ch5 respected the cap; Ch4 and Ch6 did not.

**Refinement:** Maximum 1 per chapter. Cross-chapter cumulative tracking by naturalism critic. At 10+ total instances, flag as structural overuse.

### R8. "The X. The Y. The Z." Sentence Architecture — CRITICAL (NEW)

| Chapter | Density | Caught by |
|---------|---------|-----------|
| Ch4 | Present but not quantified | Naturalism (implied by polysyndeton) |
| Ch5 | 73/241 lines (30%) — **critical** | Naturalism (C1) |
| Ch6 | 11 instances (advisory) | Naturalism (advisory) |

**Status:** NEW CRITICAL PATTERN. Ch5's 30% density is the highest AI-identifiable fingerprint in the manuscript. The sentence architecture defaults to declarative noun-phrase chains beginning with "The." This was not tracked in Ch1–3 synthesis.

**Refinement:** Naturalism critic must track as primary metric. Target: <15% of prose lines using "The X. The Y. The Z." pattern.

### R9. Omniscience Leaks — PERSISTENT

| Chapter | Instances | Target |
|---------|-----------|--------|
| Ch4 | 3 (F5: Tomás's interiority) | 0 |
| Ch5 | 1 (#16: external view of Martín) | 0 |
| Ch6 | 2 (V6, V13: Padre Joaquín's internal state) | 0 |

**Status:** PERSISTENT. The narrator accesses other characters' interiority in every chapter. Most common target: Tomás (Ch4) and Padre Joaquín (Ch6). The leaks are subtle — they appear as interpretive glosses on observable behavior rather than direct thought-rendering.

**Refinement:** Show-don't-tell and voice critics must flag any assertion about another character's cognitive state. "He saw X" (asserting perception), "the certainty was slower" (asserting internal quality), "the pragmatism of a man who..." (asserting motivation) — all violations.

### R10. Named Emotions After Showing — VARIABLE

| Chapter | Severity | Key instances |
|---------|----------|---------------|
| Ch4 | Moderate | "I felt something else," "something the sun did not do" |
| Ch5 | **Critical** | "content," "skeptical," "open," "indifference," "desperation" — 5 critical findings |
| Ch6 | Low | "conviction" (borderline), "fear" (physical-anchored) |

**Status:** VARIABLE. Ch5 is the worst offender with 5 named emotions in a single chapter. Ch6 improved significantly. The pattern is: narrator renders a physical contrast then names the emotional meaning.

**Refinement:** Show-don't-tell continues primary tracking. Any named emotion that the rendered scene already communicates = automatic critical finding.

---

## 4. Blind Spots

### B1. Voice Critic Format-Rule Compliance Gap
Ch4 voice critic found 6 Tier 1 banned constructions but still passed the chapter. Ch5 voice found 0 violations. Ch6 voice found 4 and flagged as blocking. The voice critic's format-rule compliance check is inconsistent — it identifies violations but does not consistently weight them as blocking.

**Recommendation:** Voice critic must auto-fail any chapter with 3+ Tier 1 banned constructions. The show-don't-tell verdict is operative when disagreement occurs (per P5 in Ch1–3 synthesis).

### B2. Cross-Chapter Refrain Cumulative Tracking
No single critic tracks cumulative refrain density across chapters. "I did not know" has appeared 15+ times across Ch1–6, but each critic only evaluates within its chapter. The naturalism critic notes cross-chapter risk but does not produce a cumulative count.

**Recommendation:** Naturalism critic must maintain a running refrain counter. At 10+ cumulative instances of any phrase, flag as structural overuse.

### B3. Sentence Architecture Uniformity
"The X. The Y. The Z." sentence pattern was only caught as critical in Ch5 (30% density). Other critics (show, voice, palette, continuity) do not track sentence openers. This pattern is the most AI-identifiable fingerprint after em-dash density.

**Recommendation:** Naturalism critic must track sentence opener distribution as a primary metric. Any sentence opener pattern exceeding 20% of prose lines = moderate flag; exceeding 30% = critical.

### B4. Prose Distance Modulation
Noted in Ch1–3 synthesis as a blind spot. Still not systematically covered. Ch4 palette notes "five consecutive paragraphs at similar distance: checked" but this is an isolated observation, not a systematic check.

**Recommendation:** Show-don't-tell or palette critic should check for 5+ consecutive paragraphs at the same prose distance (extreme close-up, middle distance, compressed lyric).

### B5. Substitution Pattern Detection
Ch1–3 synthesis noted that "one fingerprint decreasing while another increases" is not tracked. Confirmed: em-dash density decreased in Ch3 but returned in Ch4–6. "The way" density was low in Ch1–3 but spiked in Ch4–6. No critic tracks these substitution dynamics.

**Recommendation:** Naturalism critic should compare current chapter's pattern densities against the rolling average of the prior 3 chapters. Any pattern that increases by >50% over the rolling average = flag.

---

## 5. Resolved Patterns (from Ch1–3)

| Pattern | Ch1–3 Status | Ch4–6 Status | Notes |
|---------|-------------|-------------|-------|
| Em-dash density | "Resolved" (Ch3 = 0.25/250w) | **REGRESSED** (Ch4–6: 2.4–3.0/250w) | Not actually resolved — was Ch3 an outlier? |
| Negative construction density | Improving (Ch1: 18.0 → Ch3: 13.8) | Mixed (Ch4: 19.2, Ch5: 12.9, Ch6: 13.7%) | Ch4 spike, then improvement |
| Scapular callback | Seeded and active | Confirmed — present in all 3 chapters | Advisory: Ch4 payoff thin |
| "The body" as agent | 3+ instances flagged | Present in Ch4 (body-filing-system metaphor) | Monitor: not critical in Ch4–6 |

---

## 6. Refinement Notes for Ch7–9 Critics

### For All Critics
1. **Final 15% = high-risk zone.** Double scrutiny on chapter endings. Any passage that names emotions, explains scenes, or delivers thesis in the final 200 words = automatic flag.
2. **"Not X but Y" scan is mandatory.** First-pass mechanical check before qualitative evaluation. 3+ instances = auto-fail.
3. **Cross-chapter refrain tracking.** "I did not know" cumulative count: 15+. Maximum 1 per chapter. Any additional instance beyond 1 = flag.
4. **Em-dash target: ≤2/250 words.** Current average across Ch4–6: ~2.7/250w. Must decrease.

### For Show-Don't-Tell Critic
1. **Named emotions after showing** — the pattern is: narrator renders physical contrast, then names the emotional meaning. Ch5 was worst (5 critical). Flag any named emotion that the rendered scene already communicates.
2. **Omniscience assertions** — "He saw X," "the certainty was slower," "the pragmatism of a man who..." — all assert interiority. Flag as Tier 1.
3. **Authorial intrusion in endings** — the narrator steps back to explain, interpret, or assert knowledge. This is the dominant failure mode in chapter closings.

### For Voice Critic
1. **Format-rule compliance must be weighted as blocking.** Ch4 voice found 6 Tier 1 violations and still passed. Auto-fail at 3+ Tier 1 instances.
2. **Chinese character artifact** appeared in Ch6 line 23. Check for text-generation artifacts in all chapters.
3. **Hedge words ("maybe")** — Ch6 had 4 instances. Monitor for accumulation. Character-appropriate in dialogue but not in narration.

### For Palette Critic
1. **Palette critic is the most reliable.** All 3 chapters PASS. Continue current approach.
2. **Watch for restraint violations in Ch7–9** — as the war intensifies, the temptation to name emotions will increase. The palette critic's restraint check is the last line of defense.

### For Continuity Critic
1. **State files are consistently stale.** Ch4–6 all noted stale project_state.json, reader_state.json, timeline.json. The book-runner must update state files after each chapter.
2. **Martín's yoke-and-arrows pin** — not explicitly on his beret in Ch6. Track prop presence across chapters.
3. **Callback underdelivery** — Ch4 scapular payoff was thin. Monitor that payoff chapters deliver substantive moments, not just prop-presence.

### For Naturalism Critic
1. **"The X. The Y. The Z." sentence architecture** — new critical pattern. Track as primary metric. Target: <15% of prose lines.
2. **Em-dash density** — primary mechanical fingerprint. Target: ≤2/250w. Current average: ~2.7/250w.
3. **"The way" density** — worsening. Target: ≤2/1k. Current average: ~2.6/1k.
4. **Triplet closings** — primary AI-tic. Target: ≤5 per chapter in non-scenic passages.
5. **Cross-chapter refrain counter** — maintain running total for "I did not know," "the boy does not know," and any other recurring phrase.

---

## 7. Chapter-Specific Strengths (Not to Lose in Revision)

| Chapter | Strength | Risk in Revision |
|---------|----------|-----------------|
| Ch4 | Assault sequence (lines 69–84) — rendered through sound and vibration | Do not add interiority; the body's learning is the point |
| Ch4 | Padre Joaquín blessing sequence — ritual repetition carrying theological weight | Do not explain what "Hijo" means; the silence is the scene |
| Ch4 | Tomás as voice anchor — "Big" refrain, spare dialogue | Do not give Tomás interiority; his pragmatism is the counterweight |
| Ch5 | Salazar's persuasiveness — genuinely well-constructed argument | Do not undercut with easy dismissals; the pull must be real |
| Ch5 | Pin-crucifix contrast through physical objects — weight, temperature, texture | Do not name the betrayal; the objects do the work |
| Ch5 | Don Eusebio's letter — crossed-out word, crowded handwriting | Do not interpret the letter; the forensic detail is sufficient |
| Ch6 | Sound-based worldbuilding — ears as primary instrument | Do not shift to sight-based descriptions; the acoustic architecture is the chapter's identity |
| Ch6 | Confession scene — Padre Joaquín's doubt rendered through hands and pauses | Do not access Joaquín's interiority; the shaking hands are the confession |
| Ch6 | Foreign voices — propaganda categories dissolving through ears | Do not add political analysis; the sound of men talking is enough |
