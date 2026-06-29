# Definition of Done — Screenplay v2.0

*Every autonomous screenplay workflow must satisfy all items below. The verification tool reads this as a specification; the producer instantiates a concrete manifest from it at run start.*

---

## How This Works

1. At run start, once the outline is locked and the scene count is known, the producer writes `state/completion_manifest.json` — a concrete list of every file that must exist and its acceptance test.
2. Throughout the run, `python tools/verify_completion.py` checks the manifest against disk. It now also validates critic substance (located findings), scene hashes (stale artifacts fail), and runs the deterministic lint suite.
3. The run may be reported COMPLETE only when the verifier returns PASS AND `python tools/finalize.py` returns 0. `finalize.py` runs both `verify_completion.py` AND `tools/lints.py` (blocking lints: hollow critics, padding, refrains, negative density, em-dash, factual review). Both must PASS.

A passing manifest certifies **completeness and integrity** — that every required artifact exists, meets its minimum bar, contains substantive evidence, and passes deterministic content lints. It does NOT certify quality. Quality is the job of critics and editorial.

---

## Required Artifact Classes

### Pre-Production

| # | Artifact | Path Pattern | Acceptance Test |
|---|----------|-------------|-----------------|
| 1 | History base | `reference/history_base*.md` | exists, nonempty |
| 2 | Concept files (≥3) | `reference/*concept*` | glob_count ≥ 3 |
| 3 | Concept selection record | `coverage_reports/concept_selection*.md` | exists, nonempty |
| 4 | Bible: concept | `bible/01_concept.md` | exists, nonempty |
| 5 | Bible: mythology | `bible/02_mythology.md` | exists, nonempty |
| 6 | Bible: character profiles | `bible/03_characters/*.md` | glob_count ≥ principals |
| 7 | Bible: outline | `bible/04_outline.md` | exists, nonempty |
| 8 | Bible: ending notes | `bible/05_ending_notes.md` | exists, nonempty |
| 9 | Bible: craft | `bible/06_craft_feeling.md` | exists, nonempty |
| 10 | Bible: format rules | `bible/07_format_rules.md` | exists, nonempty |
| 11 | Bible-auditor pass | `coverage_reports/bible_audit*` | exists |
| 12 | Locked voice spec | `bible/LOCKED_VOICE_SPEC.md` | exists, nonempty |
| 13 | Outline editorial review | `coverage_reports/editorial_review_outline*` | exists, verdict present |

### Per-Scene (repeated for each scene N = 1..S)

| # | Artifact | Path Pattern | Acceptance Test |
|---|----------|-------------|-----------------|
| 14 | Architect plan | `critic_outputs/scene_{N}_plan.md` | exists, nonempty |
| 15 | Fountain draft | `script/scenes/{N}_*.fountain` | word_floor ≥ 250 (≈1 page; stub-detector — never a target to expand toward) |
| 16 | Lint pass | `script/scenes/{N}_*.fountain` | lint_pass: no critical findings, <5 moderate |
| 17 | Show-don't-tell critic | `critic_outputs/scene_{N}_show*.md` | critic_substance: located findings present, scene_hash valid |
| 18 | Voice critic | `critic_outputs/scene_{N}_voice*.md` | critic_substance: located findings present, scene_hash valid |
| 19 | Palette critic | `critic_outputs/scene_{N}_palette*.md` | critic_substance: located findings present, scene_hash valid |
| 20 | Continuity critic | `critic_outputs/scene_{N}_continuity*.md` | critic_substance: located findings present, scene_hash valid |
| 21 | Naturalism critic | `critic_outputs/scene_{N}_naturalism*.md` | critic_substance: located findings present, scene_hash valid |
| 22 | Editorial evaluation | `coverage_reports/editorial_report_scene{N}*.md` | critic_substance: located findings present, scene_hash valid |

### Post-Production

| # | Artifact | Path Pattern | Acceptance Test |
|---|----------|-------------|-----------------|
| 23 | Full adversarial read | `coverage_reports/*adversarial*` | critic_substance: located weaknesses present (min 5 for full screenplay) |
| 24 | Quantitative adversarial | `coverage_reports/*quantitative*` | exists, nonempty |
| 25 | Assembled screenplay | `script/screenplay.fountain` | assembly_match: word count = sum of scene files |
| 26 | Parenthetical audit | `coverage_reports/parenthetical_audit*` | exists |
| 27 | Callback check | `coverage_reports/callback_check*` | exists |
| 28 | Production report | `coverage_reports/production_report*` | exists, nonempty |

---

## What the Gate Verifies (v2.0)

### Presence (existing)
- Every required file exists on disk
- Scene word count ≥ stub-detector floor (250)
- Assembly word count = sum of scene files
- Required verdicts present in editorial/adversarial files

### Content (new)
- **Critics have teeth:** Every critic/editorial file must contain located findings (quoted text + position). A bare "PASS" or "ADVANCE" with zero located findings is a hollow artifact and fails the gate.
- **Scene hashing:** Each scene gets a SHA-256 hash of its clean (artifact-stripped) content. Critic/editorial files that embed a stale hash (scene was revised but critic wasn't) fail the gate.
- **Deterministic lints:** The lint suite runs on every scene and the assembly. Critical findings (duplicate paragraphs, cross-scene refrain, banned constructions, negative-construction tic loops) block advancement.
- **Anti-padding:** Scenes landing within 25 words of a round number (500, 1000, 1500) are flagged.
- **Named figures:** Proper nouns matching known real historical figures are flagged for accuracy review.

### Anti-Forgery (existing + strengthened)
- `finalize.py` recomputes the verdict from BOTH `verify_completion.py` AND `tools/lints.py`. Both must PASS.
- The completion artifact is bound to a SHA-256 of the normalized assembled screenplay content. Stale or copied certificates are auto-invalidated.
- The agent may never write `COMPLETION_PASS.json` directly.
- A stub-stamping loop (writing files that say "VERDICT: PASS" / "Panel Verdict: ADVANCE") fails because: (a) the files lack located findings, (b) the lint suite catches content issues, (c) finalize recomputes the verdict.

---

## Manifest Schema (v2.0)

```json
{
  "version": "2.0",
  "project_name": "Film Title",
  "project_type": "screenplay",
  "generated_at": "ISO timestamp",
  "scope": {
    "scene_count": 40,
    "principal_characters": ["protagonist", "antagonist"],
    "word_floor": 250
  },
  "sections": [
    {
      "name": "Pre-Production",
      "items": [
        {"label": "History base", "path": "reference/history_base.md", "check": "nonempty"},
        {"label": "Concept files", "check": "glob_count", "pattern": "reference/*concept*", "min_count": 3},
        {"label": "Bible: concept", "path": "bible/01_concept.md", "check": "nonempty"},
        {"label": "Bible: outline", "path": "bible/04_outline.md", "check": "nonempty"},
        {"label": "Bible: format rules", "path": "bible/07_format_rules.md", "check": "nonempty"},
        {"label": "Locked voice spec", "check": "glob_count", "pattern": "bible/LOCKED_VOICE_SPEC*", "min_count": 1}
      ]
    },
    {
      "name": "Scene 1",
      "items": [
        {"label": "Scene 1 plan", "path": "critic_outputs/scene_1_plan.md", "check": "nonempty"},
        {"label": "Scene 1 draft", "check": "word_floor", "path": "script/scenes/01_*.fountain", "floor": 250},
        {"label": "Scene 1 lint pass", "check": "lint_pass", "path": "script/scenes/01_*.fountain"},
        {"label": "Scene 1 show critic substance", "check": "critic_substance", "pattern": "critic_outputs/scene_1_show*"},
        {"label": "Scene 1 voice critic substance", "check": "critic_substance", "pattern": "critic_outputs/scene_1_voice*"},
        {"label": "Scene 1 palette critic substance", "check": "critic_substance", "pattern": "critic_outputs/scene_1_palette*"},
        {"label": "Scene 1 continuity critic substance", "check": "critic_substance", "pattern": "critic_outputs/scene_1_continuity*"},
        {"label": "Scene 1 naturalism critic substance", "check": "critic_substance", "pattern": "critic_outputs/scene_1_naturalism*"},
        {"label": "Scene 1 editorial substance", "check": "critic_substance", "pattern": "coverage_reports/editorial_report_scene1*"}
      ]
    },
    {
      "name": "Post-Production",
      "items": [
        {"label": "Adversarial read substance", "check": "critic_substance", "pattern": "coverage_reports/*adversarial*"},
        {"label": "Assembly integrity", "check": "assembly_match", "assembled_path": "script/screenplay.fountain", "chapter_pattern": "script/scenes/*.fountain"},
        {"label": "Callback ledger", "path": "state/callback_ledger.json", "check": "nonempty"},
        {"label": "Convention ledger", "path": "state/convention_ledger.json", "check": "nonempty"}
      ]
    }
  ]
}
```

The producer generates one section per scene, expanding the per-scene block for each scene 1..S.

---

## Key Changes from v1.0

| Change | What It Closes |
|--------|---------------|
| `critic_substance` check type | Prevents hollow PASS/ADVANCE assertions with zero evidence |
| `lint_pass` check type | Deterministic content lints catch patterns the agent can't self-approve |
| Scene hash binding | Stale artifacts (scene revised but critic not updated) fail the gate |
| Blinded critics | Each critic reads only scene + rubric, not other critics' output |
| Located findings mandatory | Every critic/editorial must quote specific passages as evidence |
| Revise-then-recheck | Flagged issues must be fixed and re-verified before advance |
| finalize.py runs both verify + lint | Agent cannot stamp its own approval |
