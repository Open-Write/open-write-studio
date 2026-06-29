# [NOVEL TITLE] — Section VII: Prose Discipline

*This document governs all prose generation. **Reload before every chapter.** Without it, the prose swells.*

---

## VII. PROSE DISCIPLINE

### I. THE CORE PRINCIPLE

Every rule in this document exists to prevent a specific failure mode that AI prose defaults toward. If a rule seems arbitrary, it is because the failure it prevents is worse than the constraint it imposes.

---

### II. SCENE VERSUS SUMMARY

**The failure:** AI prose defaults toward summary. *Character spent the morning at their desk* is not a scene. It tells the reader that time passed without rendering any of it.

**The discipline:** Every chapter must specify a summary-to-scene ratio in the architect's plan. Most chapters should be predominantly scene (70%+). Summary is permitted but must earn its place by compressing what scene would belabor.

**The test:** If you can delete a paragraph and the reader loses nothing but the information that time passed, that paragraph was summary that did not earn its place. Either make it scene or cut it.

---

### III. PROSE DISTANCE

**The failure:** AI prose tends toward a uniform middle-distance narration that neither gets close enough to render texture nor pulls back far enough for compressed lyric distance.

**The discipline:** Every chapter has a prose-distance setting. Within that setting, the prose must modulate between:

- **Extreme close-up:** The eye's movement, the breath catching, the specific weight of a hand on a shoulder.
- **Middle distance:** The default for most scene work.
- **Compressed lyric distance:** A season passing in two sentences. A year in a paragraph.

**The test:** Read five consecutive paragraphs. If they all feel the same distance, the prose is flat.

---

### IV. AI TICS — THE SCRUB LIST

#### Tier 1 — Scrub on sight (absolute ban)

- **"Not X but Y" / "Not X. Not Y. Z."** construction. Banned in any form.
- **"The particular X of Y" / "The specific X that Y."** Banned.
- **"In a way that Z"** construction. Rewrite for directness.
- **"Something between X and Y."** Banned. This avoids specificity.
- **Hedge words:** *somewhat, perhaps, in some sense, almost as if.*
- **"She felt that," "he thought that," "they realized that"** — interiority through telling.
- **"There was" / "There is"** (existential expletive). Cut the expletive, lead with the subject.
- **Triadic parallel as default rhythm.** Three-element lists as background music — permitted only when the moment specifically calls for three beats.
- **Meta-address.** The narrator must never step back to explain the novel's own structural choices.

#### Tier 2 — Flag and evaluate

- **Em-dash-followed-by-elaboration** when used more than once per page.
- **Adverbs ending in -ly,** particularly in dialogue tags.
- **Sentences that begin with "And" or "But"** more than twice per paragraph.
- **Polysyndeton chains** used as default rhythm.
- **Verbatim repetition** of phrases across chapters without structural intent.

#### Tier 3 — Monitor

- **"As if" constructions** more than once per page.
- **"It was" constructions** that delay the subject.
- **Simile clusters** — two or more similes in the same paragraph.

---

### V. INTERIORITY MUST DO WORK

**The advantage:** Prose can render interiority directly. This is its main advantage over screenplays.

**The failure:** Generic interiority is worse than no interiority. *She felt sad* is worse than nothing.

**The discipline:** Every interiority passage must:
1. Be specific to this character at this moment.
2. Contain a detail that could only belong to them.
3. Not summarize emotion in general terms.

**The rendering spectrum:**

| Level | Example | Quality |
|-------|---------|---------|
| Named emotion | *She felt grief.* | Bad. Cut or replace. |
| Named emotion with qualifier | *She felt a familiar grief.* | Still bad. |
| Physical symptom | *Her chest tightened.* | Better, but generic. |
| Specific physical detail | *She set the cup down harder than she meant to.* | Good. Behavioral, specific. |
| Rendered consciousness | *The kitchen had not changed since the morning Sofia stopped wanting toast.* | Best. Interiority as perception. |

Aim for levels 4 and 5.

---

### VI. PROSE AS MUSIC

- **Vary sentence length deliberately.** Long and short sentences should alternate.
- **Vary paragraph length.** A page of paragraphs all four sentences long is a page with no rhythm.
- **Read passages aloud in planning.** If you cannot imagine a human reading it with interest, the rhythm is wrong.
- **Flag passages where 5+ consecutive sentences have similar lengths** (within 3 words of each other).

---

### VII. THE AVOIDANCE OF LITERARY CLICHÉ

**The banned list** (scrub on sight):

- *the weight of grief*
- *the architecture of memory*
- *the geography of longing*
- *the texture of silence*
- *the space between heartbeats*
- *the quiet hum of*
- *the slow unfurling of*
- *tangled in*
- *woven through*
- *etched into*
- *burned into*
- *seared by*

**The discipline:** Better to be plain than to be falsely elevated. A simple sentence that means what it says is always better than a decorated sentence that means nothing.

---

### VIII. DIALOGUE IN PROSE

- **Dialogue tags:** *said* and *asked* are the defaults. Use others sparingly. Never use adverbial dialogue tags.
- **Attribution:** Minimize dialogue tags by using action beats instead.
- **Subtext:** Characters do not say what they mean directly. If a character names their own emotional state in dialogue, the line is wrong.
- **Dialogue differentiation is mandatory.** Each character must sound distinct.

---

### IX. THE POV CONTRACT

Each chapter has a designated POV character. The prose stays inside that character's perception, knowledge, and voice for the chapter's duration.

- **Close third** (default): The narrator knows what the POV character knows.
- **Free indirect** (specific moments): The character's voice bleeds into the narration.
- **Omniscient** (sparingly): The narrator can move between consciousnesses. Used with discipline.

---

### X. THE PROSE-CUTTER

The cutter runs only when critics or editorial flag extraneous material — there is no default reduction pass and no target percentage.

**Targets:** Passages that fail the scene-vs-summary test, flat prose distance, AI tics, generic interiority, metric monotony, literary cliché.

**Does NOT:** Cut for word count alone. Remove passages that earn their length through specificity.

---

### XI. THE DETERMINISTIC LINT SUITE

The prose is checked by a model-independent lint suite (`tools/lint_suite.py`) that catches patterns the writer cannot self-approve. These lints run on every chapter and on the assembled manuscript. Critical findings block advancement.

**What the lints catch:**
- **Duplicate paragraphs:** Verbatim repeated text across or within chapters.
- **Cross-chapter refrain:** The same normalized sentence appearing in 3+ chapters (thesis sentences stamped across the book).
- **Negative-construction density:** >15 "not/did not/could not/never/nothing" per 1k words. Pattern loops ("He did not X. He could not Y.") at 3+ instances.
- **Banned constructions:** "Not X but Y", triplet closings (3+ instances), "There was/were" expletive openers, named-emotion verbs.
- **Round-number padding:** Chapters landing within 25 words of 1000, 1500, 2000, 2500, 3000.
- **Pure summary:** Chapters with <5% dialogue ratio AND <5 body-anchor words per 1k.
- **Em-dash overuse:** >2 per page.
- **Intra-chapter refrain:** Same sentence repeated 3+ times within one chapter.

**The lints do NOT judge quality, voice, or craft.** They catch mechanical patterns that are deterministic and falsifiable. Quality remains the job of the human reader and the critics.

---

### XII. THE SUMMARY

Good prose renders. It does not summarize, decorate, hedge, or signal. It earns every sentence through specificity, rhythm, and the disciplined rendering of consciousness.

When in doubt: make it more specific. Make it closer. Make it more this-character, this-moment, this-detail. The novel lives in the particular.

---

*Reload before every chapter.*
