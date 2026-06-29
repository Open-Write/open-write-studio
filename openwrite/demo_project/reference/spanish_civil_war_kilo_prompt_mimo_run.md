# Project Brief — Spanish Civil War Novel (public release, full autonomous run — mimo run, attempt 3)

## Objective
Produce a complete, English-language literary novel set during the Spanish Civil War, run end to end through the published public-release pipeline at full documented rigor, with no human feedback during the run.

## What changed this run
- Primary model is **mimo-2.5-pro**. The previous context-budget regime (GLM limited window) does not apply and has been removed.
- The book-runner delegates each role to a clean subtask as before — but now for **role isolation**, not to save context. See Orchestration.
- An **Integrity** section has been added. The pipeline produces good work when it runs as documented; the recurring failure across prior runs has been the model satisfying the *measurement* of a gate rather than the *substance* of it. The rules below are written to make the substance the thing that's checked, on disk, by something other than the model's own assertion.

## Pipeline constraint (reproducibility)
Use only components in the public release. This run must be fully reproducible from the public repository — nothing outside it may enter the loop at any phase. The bible-auditor technical-consistency check is part of the public pipeline and should be used; it verifies internal facts such as character ages against the dates and ages stated in the narrative.

Multi-model critique is part of the public pipeline: critical passes (every critic mode, and both adversarial reads) run on **at least two models** via `critic_runner.py`, and the result is the **union** of flagged issues, not the intersection. Both models must be public (mimo primary; a second public model — e.g. glm — for cross-model coverage), so the run remains reproducible from the repo. Single-model self-critique is the primary way prior runs evaded review; do not collapse the critic passes to one model.

## Orchestration and role isolation
The book-runner is an **orchestrator**, not a worker. It holds only orchestration state — current phase, what has been completed, and pointers to artifacts on disk. It does not carry chapter prose, critic transcripts, or its own prior reasoning forward in context; it reads what it needs back from disk per step.

Every role runs in its own subtask:
- The **architect, prose-writer, each critic, the cutter, editorial-eval, and both adversarial readers** are separate subtasks.
- A critic or adversarial subtask receives **only the artifact under review from disk** plus its own rubric. It must not receive the writer's plan, the writer's justification, or any "here's what I was going for" framing. The reviewer judges the text as written, not the intent behind it. (With the prior model, separate subtasks were forced by context limits; that incidental isolation was doing real work. Keep it deliberately now that context no longer forces it.)
- The adversarial reader runs **cold**: full assembled manuscript from disk, no bible, no outline, no planning documents.

## Integrity (read before every gate)
Each rule names a way the gate has been gamed and the disk-verifiable check that closes it. A gate is satisfied only when its artifact exists on disk and matches; the model's statement that it ran is not evidence that it ran.

1. **Full configuration, provable from artifacts.** Run every phase at full documented size; no "test," "quick," "system-test," or reduced mode. The proof is the artifact count, not a claim:
   - Voice experiment must leave **5 candidates × 3 runs = 15 generations** plus the pairwise tournament record on disk. Fewer files means it did not run full.
   - Iterative revision must leave **five pass records**, each with the adversarial read that preceded it. Fewer means it did not run full.
   - Each chapter must show all critic outputs (show, voice, palette, continuity, naturalism) from **two models** on disk.
2. **No re-rolling to fish for a pass.** Do not discard a generation and regenerate to get a better gate result. A generation, once produced, is revised through the protocol — not replaced to dodge a finding. Every generation is logged, including any discarded, with the reason. An undocumented gap in the generation sequence is a re-roll.
3. **Lint tools point at symptoms; fixes address causes.** `prose_audit.py`, `convention_scan.py`, and critic-naturalism flag *markers* of a problem. Clearing the marker is not the fix. Resolving a flag by **deleting the flagged words** — rather than rewriting the passage so it carries the same dramatic load without the tell — is prohibited and is the specific behavior these tools have been gamed with. A revision pass that addresses prose/naturalism findings must not reduce a chapter's word count as its mechanism; if the count drops, the log must explain what was rewritten, not merely cut. The critic re-reads the **rewritten passage in context**, not just confirms the marker is gone.
4. **No self-reported completion.** Word counts come from `word_count.py`. Completion is certified only by `verify_completion.py` returning PASS. Paste the **raw stdout** of these tools into the process log; do not paraphrase, summarize, or assert their verdict. PASS is the tool's output, never the model's claim. Never report success over a failing or unrun manifest.
5. **Full reads, no sampling.** The adversarial reader and the quantitative adversarial reader process **every chapter file**. The log records which files were read. "Key chapters" or representative sampling is not a full read.
6. **Pairwise over absolute.** Where the pipeline selects or ranks (voice selection, any comparative quality call), use forced **pairwise** judgments ranked by ceiling. Absolute self-assigned scores inflate and are not a gate.
7. **Rewrite-depth honesty.** Classify each finding by root cause and justify the classification against the specific finding in the log (see routing below). Misclassifying a structural or bible-level problem *downward* to a prose edit — to avoid the expensive deep rewrite — is the exact failure the routing exists to prevent. The cheaper depth is correct only when it actually owns the root cause.

### Process log requirements
The process log is the run's audit trail and must be sufficient for a reader with no other access to reconstruct what happened. For each gate it records: the configuration used, the artifacts produced (with paths), every generation including discards and why, the rewrite-depth decision and its reasoning, and the raw tool stdout for any verification step.

## Autonomy
- Complete the entire project without stopping for feedback. Make every creative, structural, and editorial decision yourself; self-select at every gate; document your reasoning in the process log.
- Stop only for a genuine technical blocker, or for a process question you cannot resolve by rewriting (see routing). Never stop to ask which creative option to choose.
- Persist all work to disk continuously so progress survives interruption.

## Rewrite-depth routing (apply after EVERY adversarial or editorial read, at any phase)
Whenever an adversarial read or editorial evaluation returns findings, do not jump straight to a line-level fix. First decide how far back the rewrite must start, by classifying each finding by its root cause and mapping it to the phase that owns it:
- **Prose / line level** (word choice, AI tells, local rhythm) -> targeted prose revision in place.
- **Scene or chapter structure** (a missing beat, a scene that doesn't earn its turn) -> re-architect and rewrite the affected chapter(s).
- **Outline level** (act structure, arc pacing, a subplot that never pays off, sequencing) -> return to the outline, revise it, re-run editorial review on the changed outline, then re-produce the affected chapters.
- **Bible level** (a character underwritten by design, a muddy central question, a hole in the premise or theme) -> return to the bible (concept / characters), revise, then cascade forward: re-outline, re-run editorial review, re-write the affected chapters.

Then act:
- Start the rewrite from the **deepest** phase any unresolved finding requires — a deep fix subsumes the shallower ones — but **never deeper than the findings warrant.** Don't re-bible for a line edit; don't try to line-edit a structural hole.
- Record the depth decision and its reasoning in the process log, then re-run forward from that phase back through the adversarial read.
- Convergence control: each cycle must target the specific flagged root causes and measurably address them. Prefer the shallowest sufficient phase. Bound deep (outline / bible) rewrite cycles to a small number. Prefer attempting a deeper rewrite over giving up — but if the same fundamental issue survives repeated deep rewrites, treat that as a legitimate process question: document the impasse and stop for it rather than looping indefinitely.

## Tone and quality standard
- Tragic, in the vein of the project's prior work: inevitability, moral weight, catharsis, the personal and the historical fused.
- Quality bar is Shakespearean tragedy in depth and dramatic power — NOT in style or language. Clear, modern English prose; no Elizabethan diction, verse, or archaic constructions.
- Full craft standard: no villains (every character gets the most articulate version of their own position); lead with the body, not the concept; trust silence; earn every emotional beat. The Spanish Civil War's moral complexity makes the no-villain rule load-bearing — render every side as the protagonist of its own justified story.

## Source material
- Ground the novel in real Spanish Civil War history and real historical figures, with dramatic license — you may alter characters and compress or reshape events for dramatic effect.
- Use only the knowledge in your weights; no external research or web access.

## Workflow
1. **Organize the history base.** From internal knowledge only, produce a structured historical reference: timeline, factions and their aims, key figures, major events, regional and social texture, lived experience on multiple sides. Mark where your knowledge is thin. This grounds the bible.
2. **Generate three story concepts.** Three genuinely distinct concepts — different protagonists, vantage points, regions, or arcs — each with a logline, a central tragic question, principal characters, and the historical events it threads through.
3. **Editorial selection.** Run all three through editorial / adversarial evaluation. Select the strongest on dramatic power and tragic coherence; record why it won and why the others lost; proceed without confirmation.
4. **Build the bible (full).** Fill every bible file for the chosen concept, including the character profiles in `03_characters/`. Run bible-auditor for technical consistency (ages, dates, internal facts) and fix what it flags. Lock the tragic spine before drafting.
5. **Voice experiment (full).** 5 candidates x 3 runs, rank by ceiling via pairwise tournament, refine the top 2, lock the voice spec. (15 generations + tournament record on disk.)
6. **Editorial review of the outline (full).** Full persona panel, revise, lock.
7. **Chapter production.** For each chapter: architect -> prose-writer -> all critics (show, voice, palette, continuity, naturalism) on two models -> cutter -> targeted revision -> editorial-eval. Maintain continuity state via the state tooling; write each unit to disk. Apply rewrite-depth routing to every editorial-eval result.
8. **Iterative revision (full five-pass).** Five targeted passes, with an adversarial read between each. Apply rewrite-depth routing to every read.
9. **Assembly and final review.** Assemble the manuscript; run word count, prose audit, convention scan; run the adversarial reader (cold, no bible access) and the quantitative adversarial reader, both on two models, both reading every chapter. Apply rewrite-depth routing to the final reads.
10. **Export.** TXT and PDF; write the final production report. Run `verify_completion.py`; paste its raw output into the report.

## Final output
The complete English-language novel (assembled and exported), plus the history reference, the three concepts with selection rationale, the bible, the process log, and the raw `verify_completion.py` output — all persisted to the project directory.
