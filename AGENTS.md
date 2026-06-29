# AGENTS.md — Open-Write Studio (standalone app)

## What this is

`C:\Open-Write-Studio` is a standalone, local-first Markdown writing app that will host the **Open-Write** creative-writing methodology inside a polished desktop UI. It is derived from [Storythread Studio](https://github.com/StoryThread-Dean/StorythreadStudio) (Apache-2.0) and rebranded to Open-Write.

The long-term goal: take Open-Write's methodology (critic system, completion gate, iterative revision, A/B adversarial reader, autonomous pipeline) — which today lives as markdown modes/skills + Python tools driven by an agentic IDE (Kilo/VS Code) at `C:\Open-Write` — and run it **inside this standalone Tauri app**, independent of any specific editor.

## CONTINUING BOT — START HERE

If you are a bot resuming work in this directory, read this section first.

### What is already done and tested
- **Rebrand** to Open-Write is complete (name, bundle id, cache dir `.open-write`, sidecar `open-write-backend`, updater disabled, donation stripped). Frontend compiles clean under strict `tsc` + Vite.
- **Phase T (deterministic gate)** — DONE + tested. The Open-Write toolchain is ported into `backend/app/pipeline/` and exposed as 9 routes under `/api/pipeline/*`.
- **Phase C (critic runner)** — DONE + tested. `backend/app/pipeline/critics.py` runs the 5 critics + editorial, producing gate-valid artifacts.
- **Phase P (autonomous pipeline)** — DONE + tested. `backend/app/pipeline/orchestrator.py` is the resumable phase state machine; exposed as 4 routes (`start-run`, `run-state`, `advance-phase`, `phase-output`) and a frontend `app/src/screens/Pipeline.tsx` panel.
- **Phase G (profile-system convergence)** — DONE + tested. `backend/app/pipeline/profile_context.py` loads character profiles and routes trait context by importance level (core/present/background/contextual/hidden) into the architect/writer/voice/continuity phases; voice registers surface into the voice critic prompt.
- **Multi-provider LLM routing** — DONE + tested. The backend is provider-agnostic: `backend/app/ai/providers.py` resolves a qualified `"<provider>/<model>"` id (e.g. `glm/glm-4.6`, `mimo/mimo-7b`) to a base_url + key + bare model name, with OpenRouter fallback for legacy unqualified ids. `app/ai/openrouter.py`'s `run_completion`/`run_chat`/`list_models`/`test_connection` all take a `base_url`. Providers (OpenRouter + GLM/Zhipu + MiMo + custom) live in `settings.json` under `providers`; the pipeline uses per-role models (`writer_model` for author phases, `critic_model` for critics/editorial — Open-Write A/B). Settings UI configures each provider's base_url/key/models and the two role models. **MiMo ships with a blank base_url + model list — fill it in Settings (we don't ship a guessed endpoint).**
- **Harness layer (The Architect protocols)** — DONE + tested. `backend/app/harness/` is the orchestration layer ABOVE the pipeline: goal → Planner (`planner.py`) → Router (`router.py`, config-driven via `domains.yaml`) → Runner (`runner.py`, dependency-ordered, resumable) → Verifier (`verifier.py`, `VerifierSpec` kinds: files/tool/manifest/tests — manifest reuses the Open-Write gate) → Reporter (`reporter.py`). The generalized `Task`/`TaskPlan` schema enforces unique ids + acyclic deps. Exposed as 6 routes under `/api/harness/*` (`registry`, `plan`, `start-run`, `run-state`, `advance-task`, `report`). Planner uses `planner_model` (multi-provider). Run state persists to `<project>/state/harness_run.json`.
- **Em-dash policy** — RESOLVED to Open-Write's advisory stance (see Open questions 1).
- **54 backend tests pass** (`test_pipeline.py`, `test_critics.py`, `test_pipeline_routes.py`, `test_orchestrator.py`, `test_profile_context.py`, `test_providers.py`, `test_harness.py`). Re-run anytime (see Build & run).
- The full Open-Write methodology is available locally at `openwrite/` (read-only reference).

### What remains (your job)
1. Resolve the still-open decisions in "Open questions" (release feed + ownership are the blockers before a public release).

### First files to read (in order)
1. This whole `AGENTS.md`.
2. `openwrite/skills/orchestrator_prompt.md` — the canonical pipeline phase sequence (this is the spec for Phase P).
3. `openwrite/novel_template/skills/critic_architecture.md` and `definition_of_done.md` — how critics + the gate are supposed to work in the methodology.
4. `backend/app/pipeline/critics.py` — the critic runner already implemented (reuse its `run_critic` / `compose_artifact`).
5. `backend/app/routers/pipeline.py` — the existing routes you will extend.
6. `openwrite/novel_template/.kilo/rules-*.md` — the authoritative prompt text for each pipeline role (architect, prose-writer, each critic, editorial-eval, cutter, book-runner). The condensed prompts in `critics.py` can be upgraded to load these.

### Canonical-vs-reference rule (do not break this)
- `backend/app/pipeline/` is the **CANONICAL runtime** copy of the gate logic. Edit it.
- `openwrite/` (including `openwrite/tools/`) is a **FROZEN read-only reference** of the upstream methodology. Read its prompts/protocols/templates from it; do **not** edit gate logic there or expect changes there to affect the running app. Never maintain two divergent copies of the gate.
- **Name collision warning:** `openwrite/AGENTS.md`, `openwrite/README.md`, `openwrite/CLAUDE.md`, and `openwrite/skills/start_here.md` belong to the **upstream Open-Write methodology repo**, not this app. The authoritative project memory for THIS project is the root `C:\Open-Write-Studio\AGENTS.md` (this file). Read the `openwrite/` ones only for methodology content, never as instructions about this codebase.

### Environment specifics (this machine)
- Python 3.10.6 is on PATH. `uv` is **NOT** installed; install it (`pip install uv` or the standalone installer) before running the full backend (`uv sync` / `uv run uvicorn`). The pipeline logic tests need only Python stdlib.
- `fastapi`, `pydantic`, `httpx` are installed in the user environment (so the routes test and importing the backend routers work). A fresh checkout still needs `uv sync` to be safe.
- PowerShell execution policy blocks `.ps1` and `npm.ps1`. Use `npm.cmd` for npm, and run `.ps1` via `powershell -ExecutionPolicy Bypass -File <script>`.
- Frontend deps are installed (`app/node_modules` exists). `npm.cmd run build` passes.
- There is no staging URL; the only URL is the local Vite dev server `http://localhost:1420` (during `tauri dev`) and the backend at `http://127.0.0.1:8000`.
- Git: a fresh `git init -b main` was done; **no commits exist yet**. Do not commit unless explicitly asked.

## Origin & licensing

- Codebase origin: Storythread Studio (Apache-2.0, © Dean Peterson). Rebranded to Open-Write with a neutral "Open-Write Contributors" copyright.
- Methodology origin: the `C:\Open-Write` repository (the mode/skill/rules markdown + the deterministic Python toolchain: `word_count.py`, `verify_completion.py`, `finalize.py`, `build_manifest.py`, `lints.py`).
- License: Apache-2.0 (kept). See `LICENSE`.

## Repository structure

```
C:\Open-Write-Studio\
├── app/                     # Tauri v2 + React 19 + TypeScript (Vite) frontend
│   ├── src/                 # React source (screens/, components/, hooks/, types/, utils/)
│   ├── src-tauri/           # Rust shell + tauri.conf.json + sidecar binaries/
│   ├── index.html
│   └── package.json
├── backend/                 # Python FastAPI backend (managed by uv)
│   ├── app/
│   │   ├── main.py          # FastAPI entry + CORS + router registration
│   │   ├── routers/         # projects, documents, profiles, ai, series, export, progress, search, settings, pipeline
│   │   ├── ai/              # openrouter.py, prompts.py, assistants.py, sanitizer.py
│   │   ├── pipeline/        # Open-Write completion-gate toolchain (CANONICAL runtime; Phase T/C):
│   │   │                    #   word_count, build_manifest, verify_completion, lints, lint_suite, finalize, critics
│   │   ├── settings_store.py   # ~/.open-write/settings.json
│   │   ├── recent_projects.py  # ~/.open-write/open-write.json
│   │   ├── progress_store.py   # <project>/.open-write/app.db (SQLite cache)
│   │   └── ...
│   ├── tests/               # test_pipeline.py, test_critics.py, test_pipeline_routes.py, pipeline_fixtures.py (+ upstream tests)
│   ├── pyproject.toml
│   └── backend.spec         # PyInstaller spec (sidecar)
├── openwrite/               # READ-ONLY reference snapshot of the Open-Write methodology (Phase P reads its prompts/protocols from here)
│   ├── skills/              # orchestrator_prompt.md, start_here.md, known_limitations.md
│   ├── novel_template/.kilo/# rules-architect, rules-book-runner, rules-prose-writer, rules-critic-{show,voice,palette,continuity,naturalism}, rules-editorial-eval, rules-cutter, rules-adversarial-reader, modes/, agent/
│   ├── novel_template/skills/  # definition_of_done, critic_architecture, novel_craft, voice_experiment_protocol, editorial_review_protocol, iterative_revision_protocol, meta_critic_protocol, ...
│   ├── novel_template/bible/   # template bible scaffolds (concept, outline, format_rules)
│   ├── screenplay_template/, tv_template/   # the other two formats
│   ├── tools/              # upstream CLI tools (FROZEN reference — the live port is backend/app/pipeline/)
│   └── demo_project/       # a worked example of a full Open-Write project layout
├── docs/                    # product-scope, architecture, features, roadmap, RELEASING
├── scripts/                 # release.ps1, build-backend.ps1
├── tests/                   # manual-smoke.md
├── CLAUDE.md                # upstream coding guide (still accurate for the stack)
└── AGENTS.md                # THIS FILE
```

## Architecture (unchanged from upstream)

Three-layer local app. Nothing leaves the machine except explicit AI requests to OpenRouter.

```
[ Tauri window ]
       |
[ React + TypeScript UI ]      panels, editor, chat, overlays (port 1420 dev)
       |  HTTP on 127.0.0.1:8000
[ FastAPI backend (Python) ]   file I/O, parsing, AI routing, sanitizer
       |
[ Markdown files + SQLite ]    dual storage
```

**Dual storage model:**
- Markdown files = permanent source of truth (chapters, profiles, notes, summaries).
- SQLite (`<project>/.open-write/app.db`) = fast local cache (parsed profiles, settings, model registry, progress events). Rebuildable from Markdown.

**AI write boundary:** AI may write directly only to designated fields (`ai_profile_summary`, `ai_section_summary`, `chapter_summary`, `scene_summary`). All other output is shown for manual copy.

## Build & run

### Backend (run from `backend/`)
```powershell
uv sync
uv run uvicorn app.main:app --reload --port 8000
uv run pytest                # tests
```
Requires `uv` (Python package manager). `uv` is NOT currently on this machine's PATH — install it before running the backend.

The pipeline toolchain (Phase T/C) is stdlib-only, so its logic tests run
with plain Python even without the full backend env:
```powershell
$env:PYTHONIOENCODING="utf-8"
python tests/test_pipeline.py        # 5 logic tests (stdlib only)
python tests/test_critics.py         # 3 critic-composition tests (stdlib only)
# HTTP routes test needs fastapi + httpx:
python tests/test_pipeline_routes.py # 12 end-to-end HTTP tests
```

### Frontend + Tauri (run from `app/`)
```powershell
npm install
npm run tauri dev            # full app (launches Tauri window + Vite + hot reload)
npx tsc --noEmit             # typecheck only
npm run test -- --run        # vitest
npm run tauri build          # production installer (.msi)
```

**Dev mode does not use the sidecar** — start the backend manually with `uv run uvicorn`. The bundled Python exe is only built for release via `scripts/build-backend.ps1`.

## Rebrand done in this setup session

All "Storythread" branding has been replaced with "Open-Write". Concretely:

| Token | Old | New |
|---|---|---|
| Product name | Storythread Studio | Open-Write |
| npm package / Rust crate | storythread-studio | open-write |
| Sidecar binary | storythread-backend | open-write-backend |
| Bundle identifier | studio.storythread.app | studio.openwrite.app |
| Project cache dir | `<project>/.storythread/` | `<project>/.open-write/` |
| Global settings dir | `~/.storythread/` | `~/.open-write/` |
| Recent-projects file | `~/.storythread/storythread.json` | `~/.open-write/open-write.json` |
| localStorage keys | `storythread.*` | `open-write.*` |
| Vault default | `Documents/Storythread Studio` | `Documents/Open-Write` |

**Auto-updater: DISABLED.** `tauri.conf.json` no longer has a `plugins.updater` block, `createUpdaterArtifacts` is `false`, and `useAppUpdate.ts` short-circuits to "up-to-date" without contacting any endpoint. Re-enable it only once Open-Write has its own release feed + a fresh minisign keypair (see `docs/RELEASING.md`). The StoryThread minisign pubkey was removed.

**Donation / sponsor UI: STRIPPED to neutral.** `FUNDING.yml` cleared, donation section removed from `AboutPanel.tsx`, and `useDonationState.ts` neutralized so `shouldShowPrompt` is always `false` (the donor-flag plumbing is kept inert so consumers still type-check; `DonationPrompt.tsx` is retained but never renders). Author attribution changed from "Dean Peterson" to "Open-Write Contributors".

**The only remaining upstream string is in `app/src-tauri/Cargo.lock`** (the local crate's old name). It self-heals on the next `cargo build`.

## Integration roadmap: bringing Open-Write methodology in

This is the real work. The Storythread app is human-driven ("AI reviews, never authors"); Open-Write is methodology-driven (AI authors + critiques + verifies via a deterministic gate). The integration adds Open-Write's rigor without removing Storythread's human-driven UX — they become two modes in one app.

### Phase R — Rebrand (DONE this session)
See above.

### Phase T — Port the deterministic toolchain (DONE)
The canonical Open-Write toolchain is ported verbatim (logic-for-logic) into
`backend/app/pipeline/`:
- `word_count.py` (canonical counter, `strip_artifacts`, `ARTIFACT_PATTERNS`, `count_prose_words_from_text`)
- `build_manifest.py` (generate `completion_manifest.json` from a locked outline)
- `verify_completion.py` (sole PASS/FAIL authority; manifest validation, path-traversal guards, critic-substance + hash-binding checks)
- `lint_suite.py` (deterministic per-chapter / assembly / cross-chapter lints)
- `lints.py` (the 6 finalize blocking/advisory lints)
- `finalize.py` (the gate; writes the SHA-256-bound `COMPLETION_PASS.json`)

The only changes from the CLI originals: sibling `sys.path` hacks became
relative package imports, and `finalize.run_manifest_verify` calls
`verify_completion.verify_manifest` in-process instead of spawning a
subprocess. Fidelity to the gate logic is preserved exactly.

Exposed as 9 FastAPI routes under `POST /api/pipeline/*`
(word-count, build-manifest, manifest GET, verify, lints, lint-suite,
finalize, run-critic, run-all-critics). The agent/caller may NEVER write
`COMPLETION_PASS.json` directly — only `/finalize` (via `finalize.finalize`)
produces it.

Tests: `backend/tests/test_pipeline.py` (5 — logic), `test_pipeline_routes.py`
(12 — HTTP end-to-end through the real router), `pipeline_fixtures.py`
(shared gate-PASS fixture). Run with plain Python or pytest (no FastAPI
needed for the logic suite).

### Phase C — Critic system (DONE)
`backend/app/pipeline/critics.py` runs the 5 Open-Write critics (show, voice,
palette, continuity, naturalism) plus the editorial critic over a chapter via
`app.ai.openrouter.run_chat`. Each critic's system prompt forces located
findings (Line N + quoted span), and `compose_artifact` post-processes the
model reply to guarantee a gate-valid artifact: the real `chapter_hash` is
embedded (proving the critic read the actual file), a `## Findings` heading is
ensured, and the verdict is extracted. Artifacts land in `critic_outputs/`
(or `coverage_reports/` for editorial) at exactly the paths the manifest
verifier expects, so a generated critic artifact passes both the verify
critic-substance check and the finalize `hollow_critics` lint.

Routes: `POST /api/pipeline/run-critic` (one critic) and
`POST /api/pipeline/run-all-critics` (5 critics + editorial, sequential).
Tests: `backend/tests/test_critics.py` (3 — composition + hollow-critic
round-trip, no network).

Known interaction: the app's em-dash sanitizer runs over `run_chat` replies,
so quoted passages inside critic reports may have em-dashes normalized. This
is cosmetic and does not break the gate (located findings still match by line
ref). See open question 1.

### Phase S — State model (decision already made)
Keep the split established in the architecture discussion:
- **SQLite cache** (Storythread model): profiles, model registry, progress, settings cache.
- **JSON files** (Open-Write tracking): `callback_ledger`, `audience_state`, `timeline`, `convention_ledger`, `completion_manifest`, `COMPLETION_PASS`, resume files. These are git-diffable and read directly by the Python tools.
- The Node MCP state server (`C:\Open-Write\tools\state_server/index.js`) is **not** ported — its validation logic moves into the FastAPI backend, and it is project-hardcoded to an old demo anyway.

### Phase P — Autonomous pipeline mode (the differentiator) — DONE

**Implemented:** `backend/app/pipeline/orchestrator.py` is the resumable, phase-by-phase
state machine. Phase sequence: project phases (`bible → voice → editorial_lock`) →
per-unit loop (`architect → writer → critics → editorial → verify_unit` for each chapter) →
closing phases (`assemble → adversarial → finalize`). Run state is persisted to
`<project>/state/pipeline_run.json` (resumable across sessions). The model call is
injectable (`model_call`) so the progression logic is testable without a network key,
mirroring the `critics.py` pattern.

**Reuses the existing pieces (not rebuilt):** critic passes call
`critics.compose_artifact` (gate-valid artifacts guaranteed); the per-unit gate uses
`verify_completion.verify_manifest` restricted to the current chapter; `editorial_lock`
runs `build_manifest` to write `completion_manifest.json` and pre-populate the unit list;
`finalize` calls `finalize.finalize`; system prompts load from the canonical
`openwrite/novel_template/.kilo/rules-*.md` files with condensed operative fallbacks.

**Routes (added to `routers/pipeline.py`):**
`POST /api/pipeline/start-run` · `GET /api/pipeline/run-state` ·
`POST /api/pipeline/advance-phase` (runs ONE phase, never auto-advances past FAIL) ·
`GET /api/pipeline/phase-output`.

**Frontend:** `app/src/screens/Pipeline.tsx` — roadmap of all 11 phases (done/current/pending),
gate-verdict banner, phase-output panel (artifacts, word counts, critic verdicts, manifest
counts), and a [Run Next Phase] control wired to `advance-phase`. Reachable via a new
"Production → Pipeline" left-nav entry. The writer approves each phase explicitly.

**Tests:** `backend/tests/test_orchestrator.py` (7 — run-state persistence, next_phase
ordering for project/per-unit/closing, bible file splitting, editorial_lock manifest
build, critics phase gate-valid artifacts, finalize completion). Uses an injectable
canned `model_call` — no network. Run with `python tests/test_orchestrator.py`.

**Original spec / notes kept below for reference.**
A new app mode that runs the Open-Write pipeline phase-by-phase over OpenRouter, gated by the deterministic tools between phases:
`BIBLE → VOICE → EDITORIAL → (per unit: ARCHITECT → WRITE → CRITIQUE×5 → CONDITIONAL CUT → EDITORIAL → VERIFY) → ASSEMBLE → ADVERSARIAL READ → EXPORT → FINALIZE`.
Human approval gates between phases keep it aligned with Storythread's "no silent auto-apply" rule while enabling Open-Write's autonomous authorship. This is the feature that makes the product independent of Kilo/VS Code.

**Authoritative spec:** `openwrite/skills/orchestrator_prompt.md` (the phase sequence) and `openwrite/novel_template/.kilo/rules-book-runner.md` (the runner that drives it).

**Reuse what already exists — do not rebuild:**
- Critic passes: `backend/app/pipeline/critics.run_critic` (one) / `run_all_critics` (five + editorial) via `POST /api/pipeline/run-all-critics`. These already write gate-valid artifacts.
- The gate between phases: `POST /api/pipeline/verify` (per-chapter completion) and `POST /api/pipeline/finalize` (whole-project certificate). A unit does not advance until its manifest items pass.
- Manifest scope: `POST /api/pipeline/build-manifest` (reads the locked outline, counts chapters).
- LLM calls: `app.ai.openrouter.run_chat` (plain text) and `run_completion` (JSON). API key/model come from `app.settings_store`.

**New pieces to build:**
1. `backend/app/pipeline/orchestrator.py` — a state machine over the phases above. Persists run state to `<project>/state/pipeline_run.json` (resumable across sessions; one Open-Write rule is "reduce context = resume, never abbreviate"). Each phase: build a system prompt from the matching rule file, call OpenRouter, write the artifact to the path the manifest expects, then run the gate for that phase and block on FAIL.
2. Phase → role-file mapping (load these as the system prompts; the condensed versions in `critics.py` can be replaced by the full canonical text):
   | Phase | Reference rule/skill file |
   |---|---|
   | Bible (concept/outline/format) | `openwrite/novel_template/bible/0*` templates + `rules-architect.md` |
   | Voice selection | `openwrite/novel_template/skills/voice_experiment_protocol.md` |
   | Editorial review (outline lock) | `openwrite/novel_template/skills/editorial_review_protocol.md`, `rules-editorial-eval.md` |
   | Architect (per-unit plan) | `openwrite/novel_template/.kilo/rules-architect.md` |
   | Writer (draft) | `openwrite/novel_template/.kilo/rules-prose-writer.md` + `novel_template/skills/novel_craft.md` |
   | Critics ×5 | `rules-critic-{show,voice,palette,continuity,naturalism}.md` (already implemented in `critics.py`) |
   | Conditional cut | `openwrite/novel_template/.kilo/rules-cutter.md` |
   | Editorial eval | `rules-editorial-eval.md` |
   | Verify (per unit) | `verify_completion` (already a route) |
   | Assemble | `openwrite/novel_template/tools/assemble.py` (port the assembly, like the gate was ported) |
   | Adversarial read (full manuscript) | `openwrite/novel_template/.kilo/rules-adversarial-reader.md`, `rules-adversarial-reader-quantitative.md`; run Reader A + Reader B (two models) |
   | Finalize | `finalize.finalize` (already a route) |
3. New routes under `/api/pipeline/*`: `start-run`, `run-state` (GET), `advance-phase`, `get-phase-output`. `advance-phase` runs exactly one phase and returns its artifact + the gate verdict, so the frontend can pause for human approval between phases (never auto-advance past a FAIL, and surface each phase for explicit "continue").
4. Frontend `app/src/screens/Pipeline.tsx` (and a left-nav entry) that shows the phase list, the current phase's output, the gate verdict, and a Continue/Revise control. Reuse the existing issue-overlay/popover pattern from Smart Advisor if you want inline highlights on the draft.

**Project layout decision (resolve open question 5 here):** pipeline-mode projects use the Open-Write layout (`bible/`, `manuscript/chapters/`, `critic_outputs/`, `coverage_reports/`, `state/`, `manuscript/novel.md`). This is what the ported gate expects, so do not try to run the gate over a Storythread-layout project. A pipeline project is a superset: it may also carry `notes/`, `profiles/`, `summaries/` for the human-driven side. See `openwrite/demo_project/` for a worked example of the layout.

**Validate as you go:** after each phase, hit `/api/pipeline/verify` for the in-scope chapters; do not advance until PASS. End-to-end success = `/api/pipeline/finalize` returns `COMPLETE` and writes `state/COMPLETION_PASS.json`. Add orchestrator tests to `backend/tests/` using the injectable model-call pattern already proven in `critics.py`/`test_critics.py`.



### Phase G — Profile system convergence — DONE

**Implemented:** `backend/app/pipeline/profile_context.py` loads character profiles
from `<project>/profiles/characters/*.md` and routes trait context by importance
level into the pipeline phases. The architect receives every level (core/present/
background/contextual/hidden — the full planning picture); the writer receives
core + present + hidden (hidden flagged "NEVER name directly — subtext only");
the voice critic receives core + present; the continuity critic receives core +
present + hidden. Voice material (the `voice_notes` trait-block section) is surfaced
as a `DECLARED VOICE REGISTERS` block into the voice critic's prompt (Phase G step 3),
and the voice critic system prompt in `critics.py` was updated to check dialogue
against those declared registers rather than inferring them.

**Self-contained parser:** `profile_context.py` parses the on-disk profile Markdown
directly (stdlib + PyYAML) rather than importing `app.routers.profiles`, so the
pipeline stays testable without the full FastAPI/async-backend env. No schema
migration is required — it reads the existing trait-block format; "voice registers"
are interpreted as the `voice_notes` section blocks (trait = register name,
description = how/when it surfaces), avoiding a new field.

**Wired into:** orchestrator `_exec_architect` and `_exec_writer` (full character
context appended to the user message), and `_exec_critics` (voice critic gets the
declared registers; continuity critic gets continuity context; other critics stay
blinded, per the Open-Write critic architecture). The human-driven Profile Builder
is untouched (step 4).

**Tests:** `backend/tests/test_profile_context.py` (7 — profile loading, empty-folder
handling, per-consumer importance routing for architect/writer/voice, voice-registers
extraction + no-leak-of-non-voice-material). Run with `python tests/test_profile_context.py`.

---

**Original spec / notes kept below for reference.**

Storythread's trait-block + importance-level model (Core/Present/Background/Contextual/Hidden) is richer than Open-Write's flat character profiles. Adopt it in both directions.

**Steps:**
1. Map the existing Storythread profile system (`backend/app/routers/profiles.py`, the trait-block parsing, the ChipPicker include-flags) onto Open-Write's character concept (voice registers, active_parts, knowledge, physical_state — see `openwrite/demo_project/state/project_state.json` and the Open-Write character profiles).
2. Use importance levels as the routing signal for what context the pipeline attaches to each phase (Core traits always go to the writer + critics; Present only when the character is in the unit; etc.). This replaces Open-Write's flat "attach the profile" with selective, importance-aware context — a real quality improvement.
3. Surface character voice registers (from the profile) into the voice critic's prompt so `rules-critic-voice.md` can check against declared registers rather than inferring them.
4. Keep the human-driven Profile Builder as-is; this is about wiring its richer data into the pipeline prompts.



## Open questions / decisions still needed

1. **Em-dash policy.** RESOLVED — adopted Open-Write's advisory stance. Em dashes are a legitimate prose choice governed by the advisory `em_dash` lint (>2/page) and the naturalism critic, NOT a hard ban. The three Storythread ban layers were unified to this policy: `backend/app/ai/sanitizer.py` now preserves em/en dashes (whitespace-normalize only; `contains_em_dash` kept as an informational detector), `prompts.PUNCTUATION_RULE` and the revise prompt softened to "use sparingly", and the default `notes/style-guide.md` updated. This also fixes the pipeline conflict where the sanitizer was corrupting em dashes inside critic quoted passages.
2. **Repo / git history.** RESOLVED — the Storythread history was dropped and a fresh `git init -b main` was performed (no commits yet). The initial commit will be made when the project goes public to a fresh GitHub repo.
3. **Release feed + signing.** Where will Open-Write releases live? Needed before re-enabling the updater.
4. **Ownership.** Real author/org for LICENSE, FUNDING, and the bundle identifier before release (currently neutral placeholders).
5. **Open-Write project folder layout** vs Storythread's. Open-Write expects `bible/`, `state/`, `manuscript/`, `critics/`, `editorial/`, etc. Storythread expects `manuscript/`, `notes/`, `profiles/`, `summaries/`, `exports/`. The pipeline mode needs a superset; decide how they coexist.

## Testing conventions (from upstream CLAUDE.md)

- Backend tests: `backend/tests/` (pytest + pytest-asyncio).
- Frontend tests: `app/src/**/*.test.{ts,tsx}` (vitest + testing-library, jsdom).
- Manual smoke: `tests/manual-smoke.md` (Tauri-shell flows).
- tsconfig is **strict** with `noUnusedLocals` + `noUnusedParameters` — any edit that leaves an unused import/local will fail `tsc`.
- No staging URL; local Vite dev server at `http://localhost:1420`.
