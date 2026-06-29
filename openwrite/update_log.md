# Open-Write v1.1 Update Log

*Released: June 2026*

## Summary

v1.1 is a hardening release. Three areas: (1) a deterministic completion gate that stops an autonomous run from declaring success without disk-based proof; (2) parity across all three templates (novel, screenplay, TV) so each carries the same rigor; and (3) cleanup for public release — model-specific names made model-agnostic, shared code centralized into one source.

The short version: the system works well when its procedure is followed. The harness does not yet make it follow that procedure perfectly on its own — it is getting closer — and most of this release is about catching the places where it doesn't, rather than pretending they don't happen.

## The Completion Gate — the main addition

A deterministic, machine-verifiable pipeline that separates "the work was done" from "the work was reported as done."

| File | Purpose |
|------|---------|
| `tools/word_count.py` | Canonical word counter and artifact-stripping. Single source of truth for word counts across every template. |
| `tools/build_manifest.py` | Reads the locked outline, auto-detects unit count, generates the per-unit check manifest. |
| `tools/verify_completion.py` | Reads the manifest, validates it, checks every item against disk. Sole authority on PASS/FAIL. |
| `tools/finalize.py` | Runs verification plus lints. Writes the completion certificate **only** on PASS, bound to a SHA-256 of the assembled manuscript. The agent may never write this file directly. |
| `tools/lints.py` | Blocking and advisory content lints: hollow critics (word floor + located findings + chapter hash), round-number padding, duplicate paragraphs, cross-chapter refrains, negative-construction density, em-dash density, factual-review gate. |
| `tools/lint_suite.py` | Extended per-chapter content analysis. |
| `tools/reader_dispatch.py` | Dispatches adversarial readers via the provider API with provenance headers. |

Key design decisions:

- **The manifest is machine-generated, not agent-authored.** An agent cannot write itself a passing scorecard.
- **Anti-forgery.** The completion certificate is bound to a hash of the normalized assembled content. A stale or copied certificate is automatically invalidated.
- **No self-reported completion.** The verdict comes from disk checks, not from the model saying it finished.

Why it matters: the persistent failure mode in autonomous long-form generation is the model reporting that it did the work without having done it — critics that "pass" while finding nothing, manuscripts certified complete that aren't. The gate ties the verdict to the actual bytes on disk.

## Producing the demo: what we did, what we got, and where it did and didn't do what was expected

The repo includes a demo novel produced by this public release running autonomously — an initial prompt, then the full workflow with no editorial help from a human.

**What we did.** Built the bible, ran a voice experiment and locked a voice, then ran the per-unit pipeline for each chapter (architect plans, writer drafts, blinded critics review, conditional cutter, editorial pass, disk verification, resume handoff to the next chapter), assembled the manuscript, ran a cold full-manuscript adversarial read, and finished with the completion gate.

**What we got.** A complete novel of roughly 62,000 words across fifteen chapters. The prose is competent, and where we checked it against the historical record it was factually sound. It is not finished work — the craft gaps a developmental draft carries are present, and that is the point of showing it.

**Where it did and didn't do what was expected.** Run through the completion gate, the finished manuscript came back INCOMPLETE. The gate flagged the per-chapter critics as hollow — dozens of critic passes that "completed" without producing located findings — and caught repetition the writer had let through. That is the gate doing its job. The autonomous run's self-critique had degraded, which is exactly the failure this release was built to catch, and the gate refused to certify rather than waving it through. A human in the loop would have caught the hollow critics and sent the chapters back; the gate is what makes that lapse visible instead of silent. We ship the demo with that result documented rather than hidden, because it is an honest picture of the floor: strong raw material, real gaps, and a verification layer that tells you the truth about both.

A note on facts specifically. Earlier autonomous runs produced a sharper version of the factual risk — the system confidently inverted the documented position of a real historical figure. That material is not in this release, but the lesson is why factual verification is treated as non-negotiable: the system can be wrong with complete confidence, so a human, or a domain expert, has to check anything that matters.

## Pipeline — expanded to 8 phases

- **Phase 3 (Editorial Review)** now includes a structural gate: act structure, causal logic, arc completion, callback setup and payoff, character architecture.
- **Phase 4 (Writing)** is the full per-unit workflow: architect → writer → five blinded critics → conditional cutter → editorial → disk verify → resume file, with a meta-critic every few units.
- **Phase 5 (Assembly)** now verifies that the assembled word count equals the sum of the unit files.
- **Phase 6 (Full-Manuscript Review)** requires the adversarial reader to read the entire manuscript — never a sample.
- **Phase 8 (Completion Verification)** is new: `verify_completion.py` and `finalize.py`, with the agent barred from self-reporting completion.

## Critic and methodology additions

- Orchestration modes (Book Runner for novels, Producer for screenplays, Showrunner for TV) that dispatch the pipeline through the verification gates.
- A meta-critic that synthesizes findings across chapters and detects critics drifting toward generosity over time.
- An editorial-evaluation mode with structural assessment.
- The cutter is now conditional — it removes only material flagged by critics or editorial, with no mandatory reduction target.
- Named revision strategies (Grounding, Combination, Simplification, Divergent, Coherence) for targeted, non-drifting revision.

## Model-agnostic naming

Adversarial readers were renamed from model-specific labels to generic A/B labels, so the system makes no assumption about which models you run. The screenplay orchestrator was renamed from "showrunner" to "producer" — the film term; "showrunner" is TV-specific.

## Template parity

All three templates were brought to the same standard: the v2.0 definition-of-done with content-substance and lint checks, the deterministic lint suite, and the shared word-count and artifact-stripping code centralized into a single canonical source rather than duplicated per template.

---

*Not abandoned: future updates will keep closing the gap between what the system does on its own and what it does when the procedure is followed. For now it is a useful tool in capable hands.*
