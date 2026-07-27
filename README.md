# Open-Write Studio

A local-first Markdown writing app for fiction and worldbuilding with an autonomous AI production pipeline. Open-Write combines a distraction-free editor with a deterministic completion gate, multi-critic review system, and resumable phase-by-phase pipeline.

> Your manuscript, profiles, and notes are plain Markdown files in a folder you control. Nothing leaves your machine except the AI requests you explicitly trigger, which go directly to your chosen provider. Open-Write supports 22 LLM providers out of the box — OpenRouter, OpenAI, Anthropic, Google AI, Mistral, Groq, xAI, DeepSeek, GLM/Zhipu, Qwen, and more — plus local inference via **LM Studio** and **Ollama** (no API key needed, models run on your hardware) and any OpenAI-compatible custom endpoint.

## Install (end users)

Download the latest `.msi` installer or `-setup.exe` portable installer from the repository's `app/src-tauri/target/release/bundle/` directory (or from GitHub Releases once published). Both bundle the Python backend as a sidecar — **no Python installation required** on the target machine.

- **`.msi`** — standard Windows Installer with Start Menu shortcuts and Add/Remove Programs entry (~28 MB)
- **`-setup.exe`** — portable NSIS installer, runs directly without Start Menu entries (~27 MB)

> Open-Write is not yet code-signed. Windows SmartScreen may show a warning. Click **More info**, then **Run anyway**.

## Development setup

### Prerequisites

- **Windows 10 or 11**
- **Python 3.11+** — `python` must be on PATH
- **Node.js 18+** — `npm` must be on PATH
- **Rust toolchain** — needed for Tauri (install via [rustup](https://rustup.rs/))
- **uv** (Python package manager) — install with `pip install uv` or the [standalone installer](https://docs.astral.sh/uv/getting-started/installation/)

### Clone and install

```powershell
git clone https://github.com/fredbrown1856/open-write-studio.git
cd open-write-studio
```

**Backend (Python):**

```powershell
cd backend
uv sync --dev
```

**Frontend (Node):**

```powershell
cd app
npm install
```

### Run in development

Open **two terminals** from the repo root:

```powershell
# Terminal 1 — Backend
cd backend
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend + Tauri shell
cd app
npm run tauri dev
```

The Tauri window opens at `http://localhost:1420` (Vite dev server) with hot reload. The backend runs at `http://127.0.0.1:8000`.

> Dev mode does **not** use the sidecar. The backend must be running manually.

### Build the installer

One command builds everything — backend sidecar, frontend, and Windows installer:

```powershell
.\scripts\build.ps1
```

Outputs:
- `app/src-tauri/target/release/bundle/msi/Open-Write_*.msi`
- `app/src-tauri/target/release/bundle/nsis/Open-Write_*-setup.exe`

Flags: `-SkipBackend` (reuse existing sidecar), `-Debug` (debug build).

### First run

1. Open Settings (gear icon) — pick a model from the **Recommended Models** panel (works without any API key configured) or paste your own provider API key
2. Click **New Project** on the home screen and choose a folder
3. Your project is just a folder of Markdown files. Back it up, sync it, or version-control it as you like.

## Architecture

```
[ Tauri window ]
       |
[ React + TypeScript UI ]      panels, editor, chat, overlays (port 1420 dev)
       |  HTTP on 127.0.0.1:8000
[ FastAPI backend (Python) ]   file I/O, parsing, AI routing, pipeline, gate
       |
[ Markdown files + SQLite ]    dual storage (Markdown = truth, SQLite = cache)
```

- **Frontend:** React 19 + TypeScript + Vite, CodeMirror 6 editor, Zustand state, shadcn/ui + Tailwind CSS v4
- **Backend:** FastAPI + uvicorn, managed by `uv`. 22-provider LLM routing with curated model catalog (including local inference via LM Studio and Ollama)
- **Shell:** Tauri v2 (Rust) — native window, OS integration, sidecar packaging
- **Storage:** Markdown files (source of truth) + SQLite cache (rebuildable from Markdown)

## Running tests

**Backend (54+ tests):**

```powershell
cd backend
uv run pytest
```

Pipeline logic tests are stdlib-only and can run without the full backend env:

```powershell
$env:PYTHONIOENCODING="utf-8"
python tests/test_pipeline.py          # 5 logic tests
python tests/test_critics.py           # 3 critic composition tests
python tests/test_orchestrator.py      # 7 pipeline orchestrator tests
python tests/test_profile_context.py   # 7 profile context tests
python tests/test_providers.py         # multi-provider routing tests
python tests/test_pipeline_routes.py   # 12 HTTP end-to-end tests (needs fastapi + httpx)
python tests/test_pipeline_outputs.py  # 27 output catalog + control + chat tests
python tests/test_harness.py           # harness layer tests
```

**Frontend:**

```powershell
cd app
npm run test -- --run
```

**Typecheck:**

```powershell
cd app
npx tsc --noEmit
```

## Key features

- **Markdown editor** — distraction-free writing with CodeMirror 6, serif typeface, light + dark themes
- **Profile system** — characters, relationships, locations, lore with structured trait blocks and importance levels (core/present/background/contextual/hidden)
- **Smart Advisor** — Readability, Structure, and Context passes with inline highlights and accept/ignore/re-cast controls
- **Writing Companion** — chat panel for brainstorming, voice work, ad-hoc questions
- **Open-Write Pipeline** — autonomous, resumable phase-by-phase production: bible → voice → editorial lock → (per-unit: architect → writer → critics ×5 → editorial → verify) → assemble → adversarial read → finalize
- **Pipeline Output Library** — browsable artifact catalog organized by category (Bible / Voice Experiment / Design Documents / Prose / Reviews / Manifest) with markdown and JSON rendering
- **Pipeline Companion** — conversational chat that knows the run state, can propose creative brief changes (Apply to Brief), and can trigger phase re-runs
- **Auto-run** — one-click automatic pipeline execution with 2-second delay between phases, stops on complete or fail
- **User input overrides** — provide your own content for any pipeline phase instead of generating via the model (paste your own bible, voice spec, chapter prose, etc.)
- **Per-stage model routing** — assign "Primary" or "Critic" model to each pipeline phase via settings
- **Post-critics revision loop** — when critics say REVISE, the writer automatically rewrites with critic feedback (max 2 retries per chapter)
- **Rerun with feedback** — when restarting a project with existing material, choose "Revise with Existing Feedback" to rewrite using existing critic reports
- **Deterministic completion gate** — word counting, manifest building, verification, linting, SHA-256-bound completion certificate
- **Multi-provider LLM routing** — 22 providers (OpenRouter, OpenAI, Anthropic, Google AI, Mistral, Groq, xAI, DeepSeek, GLM, Qwen, LM Studio, Ollama, and more) with a curated model catalog organized by tier and strength. Local providers run models on your hardware with no API key.
- **Harness layer** — goal → planner → router → runner → verifier → reporter orchestration above the pipeline
- **Export** — full manuscript, dated snapshots, TXT/DOCX/EPUB/Markdown
- **CLI debugging tool** — `backend/tools/ow_cli.py` for driving the pipeline from the command line

## Project structure

```
app/                     Tauri v2 + React 19 + TypeScript (Vite) frontend
  src/                   React source (screens/, components/, hooks/, types/, utils/)
  src-tauri/             Rust shell + tauri.conf.json + sidecar binaries
backend/                 Python FastAPI backend (managed by uv)
  app/
    main.py              FastAPI entry + CORS + router registration
    routers/             API routes (projects, documents, profiles, ai, pipeline, ...)
    ai/                  LLM routing, model catalog (26 curated models), prompts, sanitizer
    pipeline/            Open-Write gate toolchain (word_count, manifest, verify, lints, finalize, critics, orchestrator, outputs, profile_context)
    harness/             Architect protocols (planner, router, runner, verifier, reporter)
    tools/               CLI debugging tool (ow_cli.py)
  tests/                 pytest test suite
openwrite/               READ-ONLY reference of the Open-Write methodology
docs/                    Product scope, architecture, features, roadmap, releasing
scripts/                 Build and release scripts (build.ps1, build-backend.ps1, release.ps1)
```

## Documentation

| Doc | Description |
|---|---|
| [`AGENTS.md`](AGENTS.md) | Project memory — what's done, what remains, architecture decisions, canonical-vs-reference rules |
| [`docs/product-scope.md`](docs/product-scope.md) | Core goals, writing philosophy, locked product rules |
| [`docs/architecture.md`](docs/architecture.md) | Three-layer architecture, dual storage, folder layout, API surface |
| [`docs/features.md`](docs/features.md) | Detailed feature inventory |
| [`docs/roadmap.md`](docs/roadmap.md) | Scheduled, proposed, and nice-to-have features |
| [`CHANGELOG.md`](CHANGELOG.md) | Shipped changes per version |
| [`LICENSE`](LICENSE) | Apache License 2.0 |

## License

Apache License 2.0. See [LICENSE](LICENSE) for the full text.

## Acknowledgements

Derived from [Storythread Studio](https://github.com/StoryThread-Dean/StorythreadStudio) by Dean Peterson (Apache-2.0). Built with [Tauri](https://tauri.app/), [React](https://react.dev/), [CodeMirror](https://codemirror.net/), [FastAPI](https://fastapi.tiangolo.com/), and [OpenRouter](https://openrouter.ai/).
