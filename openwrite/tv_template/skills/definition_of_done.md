# Definition of Done — TV Series v2.0

*Every autonomous TV series workflow must satisfy all items below. The verification tool reads this as a specification; the showrunner instantiates a concrete manifest from it at run start.*

---

## How This Works

1. At run start, once the season arc is locked and episode count is known, the showrunner writes `state/completion_manifest.json` — a concrete list of every file that must exist and its acceptance test.
2. Throughout the run, `python tools/verify_completion.py` checks the manifest against disk. It now also validates critic substance (located findings), episode hashes (stale artifacts fail), and runs the deterministic lint suite.
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
| 4 | Bible: series concept | `bible/01_series_concept.md` | exists, nonempty |
| 5 | Bible: mythology | `bible/02_mythology.md` | exists, nonempty |
| 6 | Bible: character profiles | `bible/03_characters/*.md` | glob_count ≥ principals |
| 7 | Bible: season arc | `bible/04_season_arc.md` | exists, nonempty |
| 8 | Bible: episode outlines | `bible/05_episode_outlines/*.md` | glob_count ≥ episode count |
| 9 | Bible: format rules | `bible/06_format_rules.md` | exists, nonempty |
| 10 | Bible: craft | `bible/07_craft_feeling.md` | exists, nonempty |
| 11 | Bible: writers room notes | `bible/08_writers_room_notes.md` | exists, nonempty |
| 12 | Bible-auditor pass | `coverage_reports/bible_audit*` | exists |
| 13 | Locked voice spec | `bible/LOCKED_VOICE_SPEC.md` | exists, nonempty |
| 14 | Season editorial review | `coverage_reports/editorial_review_season*` | exists, verdict present |

### Per-Episode (repeated for each episode S01EXX)

| # | Artifact | Path Pattern | Acceptance Test |
|---|----------|-------------|-----------------|
| 15 | Episode plan | `critic_outputs/S01EXX_plan.md` | exists, nonempty |
| 16 | Scene files (≥1) | `scripts/scenes/S01EXX/*.fountain` | glob_count ≥ 1 |
| 17 | Assembled episode | `scripts/S01EXX.fountain` | exists, nonempty |
| 18 | Lint pass | `scripts/S01EXX.fountain` | lint_pass: no critical findings, <5 moderate |
| 19 | Show-don't-tell critic | `critic_outputs/S01EXX_show*.md` | critic_substance: located findings present, episode_hash valid |
| 20 | Voice critic | `critic_outputs/S01EXX_voice*.md` | critic_substance: located findings present, episode_hash valid |
| 21 | Palette critic | `critic_outputs/S01EXX_palette*.md` | critic_substance: located findings present, episode_hash valid |
| 22 | Continuity critic | `critic_outputs/S01EXX_continuity*.md` | critic_substance: located findings present, episode_hash valid |
| 23 | Naturalism critic | `critic_outputs/S01EXX_naturalism*.md` | critic_substance: located findings present, episode_hash valid |
| 24 | Episode editorial | `coverage_reports/editorial_report_S01EXX*.md` | critic_substance: located findings present, episode_hash valid |
| 25 | Episode adversarial coverage | `coverage_reports/S01EXX_coverage*.md` | critic_substance: located weaknesses present |

### Post-Production

| # | Artifact | Path Pattern | Acceptance Test |
|---|----------|-------------|-----------------|
| 26 | Full-season adversarial read | `coverage_reports/S01_season_coverage*.md` | critic_substance: located weaknesses present (min 5 for full season) |
| 27 | Assembled season | `scripts/Season_1.fountain` | assembly_match: word count = sum of episodes |
| 28 | Callback audit | `coverage_reports/callback_audit*` | exists |
| 29 | Character arc audit | `coverage_reports/character_arc_audit*` | exists |
| 30 | Production report | `coverage_reports/production_report*` | exists, nonempty |

---

## What the Gate Verifies (v2.0)

### Presence (existing)
- Every required file exists on disk
- Assembly word count = sum of episode files
- Required verdicts present in editorial/adversarial files

### Content (new)
- **Critics have teeth:** Every critic/editorial file must contain located findings (quoted text + position). A bare "PASS" or "ADVANCE" with zero located findings is a hollow artifact and fails the gate.
- **Episode hashing:** Each assembled episode gets a SHA-256 hash of its clean (artifact-stripped) content. Critic/editorial files that embed a stale hash (episode was revised but critic wasn't) fail the gate.
- **Deterministic lints:** The lint suite runs on every episode and the season assembly. Critical findings (duplicate paragraphs, cross-episode refrain, banned constructions, negative-construction tic loops) block advancement.
- **Named figures:** Proper nouns matching known real historical figures are flagged for accuracy review.

### Anti-Forgery (existing + strengthened)
- `finalize.py` recomputes the verdict from BOTH `verify_completion.py` AND `tools/lints.py`. Both must PASS.
- The completion artifact is bound to a SHA-256 of the normalized assembled season content. Stale or copied certificates are auto-invalidated.
- The agent may never write `COMPLETION_PASS.json` directly.
- A stub-stamping loop (writing files that say "VERDICT: PASS" / "Panel Verdict: ADVANCE") fails because: (a) the files lack located findings, (b) the lint suite catches content issues, (c) finalize recomputes the verdict.

---

## Manifest Schema (v2.0)

```json
{
  "version": "2.0",
  "project_name": "Show Title",
  "project_type": "tv",
  "generated_at": "ISO timestamp",
  "scope": {
    "episode_count": 10,
    "principal_characters": ["protagonist", "antagonist", "supporting"],
    "season": 1
  },
  "sections": [
    {
      "name": "Pre-Production",
      "items": [
        {"label": "Series concept", "path": "bible/01_series_concept.md", "check": "nonempty"},
        {"label": "Season arc", "path": "bible/04_season_arc.md", "check": "nonempty"},
        {"label": "Episode outlines", "check": "glob_count", "pattern": "bible/05_episode_outlines/*.md", "min_count": 10},
        {"label": "Format rules", "path": "bible/06_format_rules.md", "check": "nonempty"},
        {"label": "Locked voice spec", "check": "glob_count", "pattern": "bible/LOCKED_VOICE_SPEC*", "min_count": 1}
      ]
    },
    {
      "name": "S01E01",
      "items": [
        {"label": "E01 plan", "path": "critic_outputs/S01E01_plan.md", "check": "nonempty"},
        {"label": "E01 scenes", "check": "glob_count", "pattern": "scripts/scenes/S01E01/*.fountain", "min_count": 1},
        {"label": "E01 assembled", "path": "scripts/S01E01.fountain", "check": "nonempty"},
        {"label": "E01 lint pass", "check": "lint_pass", "path": "scripts/S01E01.fountain"},
        {"label": "E01 show critic substance", "check": "critic_substance", "pattern": "critic_outputs/S01E01_show*"},
        {"label": "E01 voice critic substance", "check": "critic_substance", "pattern": "critic_outputs/S01E01_voice*"},
        {"label": "E01 palette critic substance", "check": "critic_substance", "pattern": "critic_outputs/S01E01_palette*"},
        {"label": "E01 continuity critic substance", "check": "critic_substance", "pattern": "critic_outputs/S01E01_continuity*"},
        {"label": "E01 naturalism critic substance", "check": "critic_substance", "pattern": "critic_outputs/S01E01_naturalism*"},
        {"label": "E01 editorial substance", "check": "critic_substance", "pattern": "coverage_reports/editorial_report_S01E01*"},
        {"label": "E01 adversarial substance", "check": "critic_substance", "pattern": "coverage_reports/S01E01_coverage*"}
      ]
    },
    {
      "name": "Post-Production",
      "items": [
        {"label": "Season adversarial substance", "check": "critic_substance", "pattern": "coverage_reports/S01_season_coverage*"},
        {"label": "Season assembly", "check": "assembly_match", "assembled_path": "scripts/Season_1.fountain", "chapter_pattern": "scripts/S01E*.fountain"},
        {"label": "Callback ledger", "path": "state/callback_ledger.json", "check": "nonempty"},
        {"label": "Convention ledger", "path": "state/convention_ledger.json", "check": "nonempty"}
      ]
    }
  ]
}
```

The showrunner generates one section per episode, expanding the per-episode block for each episode S01E01..S01EXX.

---

## Key Changes from v1.0

| Change | What It Closes |
|--------|---------------|
| `critic_substance` check type | Prevents hollow PASS/ADVANCE assertions with zero evidence |
| `lint_pass` check type | Deterministic content lints catch patterns the agent can't self-approve |
| Episode hash binding | Stale artifacts (episode revised but critic not updated) fail the gate |
| Blinded critics | Each critic reads only episode + rubric, not other critics' output |
| Located findings mandatory | Every critic/editorial must quote specific passages as evidence |
| Revise-then-recheck | Flagged issues must be fixed and re-verified before advance |
| finalize.py runs both verify + lint | Agent cannot stamp its own approval |
| Per-episode critic checks | 5 critics + editorial per episode (not just adversarial + editorial) |
