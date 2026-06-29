# Definition of Done — Novel v2.0

*Every autonomous novel workflow must satisfy all items below. The verification tool reads this as a specification; the book-runner instantiates a concrete manifest from it at run start.*

---

## How This Works

1. At run start, once the outline is locked and the chapter count is known, the book-runner writes `state/completion_manifest.json` — a concrete list of every file that must exist and its acceptance test.
2. Throughout the run, `python tools/verify_completion.py` checks the manifest against disk. It now also validates critic substance (located findings), chapter hashes (stale artifacts fail), and runs the deterministic lint suite.
3. The run may be reported COMPLETE only when the verifier returns PASS AND `python tools/finalize.py` returns 0. `finalize.py` runs both `verify_completion.py` AND `tools/lints.py` (blocking lints: hollow critics, padding, refrains, negative density, em-dash, factual review). Both must PASS.

A passing manifest certifies **completeness and integrity** — that every required artifact exists, meets its minimum bar, contains substantive evidence, and passes deterministic content lints. It does NOT certify quality. Quality is the job of critics and editorial.

---

## Required Artifact Classes

### Pre-Production

| # | Artifact | Path Pattern | Acceptance Test |
|---|----------|-------------|-----------------|
| 1 | History base | `reference/history_base*.md` | exists, nonempty |
| 2 | Concept files (≥3) | `reference/three_concepts*.md` or `reference/*concept*` | glob_count ≥ 3 |
| 3 | Concept selection record | `coverage_reports/concept_selection*.md` | exists, nonempty |
| 4 | Bible: concept | `bible/01_concept.md` | exists, nonempty |
| 5 | Bible: mythology | `bible/02_mythology.md` | exists, nonempty |
| 6 | Bible: character profiles | `bible/03_characters/*.md` (one per principal) | glob_count ≥ number of principals |
| 7 | Bible: outline | `bible/04_outline.md` | exists, nonempty |
| 8 | Bible: ending notes | `bible/05_ending_notes.md` | exists, nonempty |
| 9 | Bible: craft | `bible/06_craft_feeling.md` | exists, nonempty |
| 10 | Bible: format rules | `bible/07_format_rules.md` | exists, nonempty |
| 11 | Bible-auditor pass | `coverage_reports/bible_audit*.md` or `state/bible_audit_passed` | exists |
| 12 | Locked voice spec | `bible/LOCKED_VOICE_SPEC.md` or `state/voice_locked` | exists, nonempty |
| 13 | Outline editorial review | `coverage_reports/editorial_review_outline*.md` | exists, verdict present |

### Per-Chapter (repeated for each chapter N = 1..C)

| # | Artifact | Path Pattern | Acceptance Test |
|---|----------|-------------|-----------------|
| 14 | Architect plan | `critic_outputs/chapter_{N}_plan.md` | exists, nonempty |
| 15 | Prose draft | `manuscript/chapters/{N}_*.md` | word_floor ≥ 800 (stub-detector) |
| 16 | Lint pass | `manuscript/chapters/{N}_*.md` | lint_pass: no critical findings, <5 moderate |
| 17 | Show-don't-tell critic | `critic_outputs/chapter_{N}_show*.md` | critic_substance: located findings present, chapter_hash valid |
| 18 | Voice critic | `critic_outputs/chapter_{N}_voice*.md` | critic_substance: located findings present, chapter_hash valid |
| 19 | Palette critic | `critic_outputs/chapter_{N}_palette*.md` | critic_substance: located findings present, chapter_hash valid |
| 20 | Continuity critic | `critic_outputs/chapter_{N}_continuity*.md` | critic_substance: located findings present, chapter_hash valid |
| 21 | Naturalism critic | `critic_outputs/chapter_{N}_naturalism*.md` | critic_substance: located findings present, chapter_hash valid |
| 22 | Editorial evaluation | `coverage_reports/editorial_report_ch{N}*.md` | critic_substance: located findings present, chapter_hash valid |

### Post-Production

| # | Artifact | Path Pattern | Acceptance Test |
|---|----------|-------------|-----------------|
| 23 | Full adversarial read | `coverage_reports/*adversarial*.md` (full-manuscript) | critic_substance: located weaknesses present (min 5 for full manuscript) |
| 24 | Quantitative adversarial | `coverage_reports/*quantitative*.md` | exists, nonempty |
| 25 | Assembled manuscript | `manuscript/novel.md` or `manuscript/{title}.md` | assembly_match: word count = sum of chapter files |
| 26 | Prose audit | `coverage_reports/prose_audit*.md` or output from `tools/prose_audit.py` | exists |
| 27 | Convention scan | `coverage_reports/convention_scan*.md` or output from `tools/convention_scan.py` | exists |
| 28 | Production report | `coverage_reports/production_report*.md` | exists, nonempty |

---

## What the Gate Verifies (v2.0)

### Presence (existing)
- Every required file exists on disk
- Chapter word count ≥ stub-detector floor (800)
- Assembly word count = sum of chapter files
- Required verdicts present in editorial/adversarial files

### Content (new)
- **Critics have teeth:** Every critic/editorial file must contain located findings (quoted text + position). A bare "PASS" or "ADVANCE" with zero located findings is a hollow artifact and fails the gate.
- **Chapter hashing:** Each chapter gets a SHA-256 hash of its clean (artifact-stripped) content. Critic/editorial files that embed a stale hash (chapter was revised but critic wasn't) fail the gate.
- **Deterministic lints:** The lint suite (`tools/lint_suite.py`) runs on every chapter and the assembly. Critical findings (duplicate paragraphs, cross-chapter refrain, banned constructions, negative-construction tic loops, pure summary) block advancement. Moderate findings (5+ per chapter) also block.
- **Anti-padding:** Chapters landing within 25 words of a round number (1000, 1500, 2000, 2500, 3000) are flagged.
- **Named figures:** Proper nouns matching known real historical figures are flagged for accuracy review.

### Anti-Forgery (existing + strengthened)
- `finalize.py` recomputes the verdict from BOTH `verify_completion.py` AND `tools/lints.py`. Both must PASS.
- The completion artifact is bound to a SHA-256 of the normalized assembled manuscript content. Stale or copied certificates are auto-invalidated.
- The agent may never write `COMPLETION_PASS.json` directly.
- A stub-stamping loop (writing files that say "VERDICT: PASS" / "Panel Verdict: ADVANCE") fails because: (a) the files lack located findings, (b) the lint suite catches content issues, (c) finalize recomputes the verdict.

---

## Manifest Schema (v2.0)

```json
{
  "version": "2.0",
  "project_name": "The Title",
  "project_type": "novel",
  "generated_at": "ISO timestamp",
  "scope": {
    "chapter_count": 15,
    "principal_characters": ["alice", "bob", "carol"],
    "word_floor": 800
  },
  "sections": [
    {
      "name": "Pre-Production",
      "items": [
        {"label": "Bible: concept", "path": "bible/01_concept.md", "check": "nonempty"},
        {"label": "Bible: outline locked", "path": "bible/04_outline.md", "check": "nonempty"},
        {"label": "Bible: format rules", "path": "bible/07_format_rules.md", "check": "nonempty"},
        {"label": "Locked voice spec", "check": "glob_count", "pattern": "bible/LOCKED_VOICE_SPEC*", "min_count": 1}
      ]
    },
    {
      "name": "Chapter 1",
      "items": [
        {"label": "Ch1 plan", "path": "critic_outputs/chapter_1_plan.md", "check": "nonempty"},
        {"label": "Ch1 draft", "check": "word_floor", "path": "manuscript/chapters/001_*.md", "floor": 800},
        {"label": "Ch1 lint pass", "check": "lint_pass", "path": "manuscript/chapters/001_*.md"},
        {"label": "Ch1 show critic substance", "check": "critic_substance", "pattern": "critic_outputs/chapter_1_show*"},
        {"label": "Ch1 voice critic substance", "check": "critic_substance", "pattern": "critic_outputs/chapter_1_voice*"},
        {"label": "Ch1 palette critic substance", "check": "critic_substance", "pattern": "critic_outputs/chapter_1_palette*"},
        {"label": "Ch1 continuity critic substance", "check": "critic_substance", "pattern": "critic_outputs/chapter_1_continuity*"},
        {"label": "Ch1 naturalism critic substance", "check": "critic_substance", "pattern": "critic_outputs/chapter_1_naturalism*"},
        {"label": "Ch1 editorial substance", "check": "critic_substance", "pattern": "coverage_reports/editorial_report_ch1*"}
      ]
    },
    {
      "name": "Post-Production",
      "items": [
        {"label": "Adversarial read substance", "check": "critic_substance", "pattern": "coverage_reports/*adversarial*"},
        {"label": "Assembly integrity", "check": "assembly_match", "assembled_path": "manuscript/novel.md", "chapter_pattern": "manuscript/chapters/*.md"},
        {"label": "Callback ledger", "path": "state/callback_ledger.json", "check": "nonempty"},
        {"label": "Convention ledger", "path": "state/convention_ledger.json", "check": "nonempty"}
      ]
    }
  ]
}
```

The book-runner generates one section per chapter, expanding the per-chapter block for each chapter 1..C.

---

## Key Changes from v1.0

| Change | What It Closes |
|--------|---------------|
| `critic_substance` check type | Prevents hollow PASS/ADVANCE assertions with zero evidence |
| `lint_pass` check type | Deterministic content lints catch patterns the agent can't self-approve |
| Chapter hash binding | Stale artifacts (chapter revised but critic not updated) fail the gate |
| Blinded critics | Each critic reads only chapter + rubric, not other critics' output |
| Located findings mandatory | Every critic/editorial must quote specific passages as evidence |
| Revise-then-recheck | Flagged issues must be fixed and re-verified before advance |
| finalize.py runs both verify + lint | Agent cannot stamp its own approval |
