# Features

This is a snapshot of what Open-Write does today. For where it is going next, see [`roadmap.md`](roadmap.md).

## Editor

- CodeMirror 6 Markdown editor with a serif typeface optimized for long reading
- Manual save (`Ctrl+S` or Save button); unsaved-change indicator with a confirm-before-close prompt
- Session undo and redo
- Formatting toolbar, font selector, find and replace
- Light and dark themes (app-wide, persisted)
- Selection highlight persists when the writer moves focus into the chat or Smart Advisor panels

## Project structure

Each project is a folder the user owns. The app reads and writes Markdown files inside that folder; it never touches anything outside it.

- `manuscript/` — one chapter per Markdown file
- `notes/` — outline, style guide, themes, plus any free notes the writer adds
- `profiles/` — character, relationship, location, lore profiles
- `arcs/` — for series projects, per-book overrides on canonical profiles
- `summaries/chapters/` — one summary file per chapter
- `summaries/scenes/<chapter-stem>/scene-NN.md` — per-scene summaries
- `exports/` — combined manuscript file plus dated snapshot folders
- `.open-write/` — local cache (safe to delete; rebuilt from Markdown)

## Profile Builder

A guided workspace for authoring structured project context.

### Profile types

Character, Relationship, Location, Lore. Each type has its own section template (Overview, Personality Traits, History, Tone and Atmosphere, Rule or Concept, etc.) defined in code, not user-edited.

### Character kinds

Characters now support a `character_kind` field that controls the template used:

| Kind | Template | Use case |
|---|---|---|
| **Main** | Full trait-block editor with all sections | Protagonist, antagonist, major supporting characters |
| **Side** | Simplified single-field-per-section | Background characters, walk-ons, named extras |

Side characters drop per-section AI summaries and use a streamlined Quick Build flow for fast creation.

### Trait blocks

Profile sections are made of trait blocks. A trait block is a single trait or a small group of related traits with a description and an importance level.

```md
- trait: observant, punctual, eloquent
  description: "She is the textbook example of someone always on time and has her things together."
  importance: core
```

### Importance levels

Replace an older "influence" scale. Importance controls when (and whether) a trait is sent to the AI.

| Level | Meaning |
|---|---|
| **Core** | Central to identity or narrative role. Always sent to AI at top prompt position |
| **Present** | Regularly relevant. Sent when the character is in the scene |
| **Background** | Exists in canon but rarely surfaced. Sent only when directly relevant |
| **Contextual** | Situational. Sent only when the writer explicitly attaches it |
| **Hidden** | Writer-only reference. Never sent to the AI; AI may not name a hidden trait, only express it as subtext |

### Adaptive word-count gauge

Each trait block shows a word count gauge tuned to its importance level. Higher-importance traits tolerate more words because they need detail to be useful in prompts. Hidden traits have no gauge.

### Profile-level AI tools

| Tool | What it does |
|---|---|
| **Section summary** | Generates a compact `## AI Summary: Section` summary into Markdown |
| **Full profile summary** | Generates a multi-paragraph `# Full AI Summary` synthesizing all sections, weighted by importance. For characters, also reads `profiles/relationships/` and weaves in connected dynamics |
| **"How AI uses this" preview** | Sparkles button on a trait block; on-demand prose explanation of how that trait's importance level shapes AI behavior. Shown in a popover, not stored |
| **AI Trim** | Scissors button that appears when a trait is in the Wordy/Bloated range; rewrites the description to a tighter target length |
| **AI Importance Audit** | Profile-level pass that flags importance-level mismatches across all trait blocks |

### Profile Builder chat

A right-side panel for refining a profile in conversation. Four behavior modes: **Chat**, **Refine**, **Extract Traits**, **Check Consistency**. Chat does not auto-write back to the profile; the writer accepts suggestions manually.

### Profile import and fork

Import a character profile from another project as a fully independent copy. The fork gets a new profile ID and is editable in the new story; there is no sync back to the source.

## Smart Advisor

Inline editor overlays for structured feedback. Three top-level categories trigger from the editor toolbar:

- **Readability** — Grammar, Clarity, Redundancy, Descriptive (subcategory toggles)
- **Structure** — Dialogue, POV, Tone, Character, Pacing
- **Context** — Character Consistency, Relationships, Setting, Lore

### How a pass works

1. Writer clicks a category button. Subcategory checkboxes scope the pass.
2. The chapter (or selected passage) is sent to `/api/ai/editor-pass` with attached context chips.
3. The AI returns structured JSON: a list of issues, each with a verbatim quote, severity (praise / issue / suggestion), category label, explanation, and suggested rewrite.
4. The frontend anchors each issue to its quote and decorates the manuscript with colored underlines (amber / violet / teal). Multi-issue overlaps show a numeric stack badge.

### The popover

Click any highlight to open a popover anchored below the issue:

- Severity badge, category label, explanation
- The original passage and the suggested rewrite, rendered as a word-level diff (additions in green, removals struck through)
- Eight modifier buttons that re-cast the suggestion: **Default** (revert to AI's first take), **Rewrite**, **Expand**, **Shorten**, **Describe**, **Rephrase**, **Add Sensory Detail**, **Change Tone**
- **Accept** / **Ignore** actions

Default is a client-side revert. The other seven call `/api/ai/revise-suggestion` with that single issue and modifier name and replace the suggestion in place.

### Stable anchoring

Issue ranges are managed through a CodeMirror `StateField` that auto-maps positions through every transaction. Accepting one suggestion (which can replace many words) shifts every other issue's anchor to its new correct position automatically. If a future edit collapses an issue's range to zero length, that issue silently drops off — no stale highlights linger.

### Subcategory persistence

Subcategory checkboxes per category persist in `localStorage`, so the writer's preferences survive reloads.

## Writing Companion

The right-side chat panel beside the editor. Three modes of interaction:

- **General chat** — open conversational AI help (brainstorming, voice work, ad-hoc questions)
- **Draft mode** — generates story prose from attached profile materials (800–1200 words, voice-anchored)
- **Enhance mode** — rewrites a highlighted passage with level-governed expansion (Restate / Default / Expanded)

Structured passes are handled by Smart Advisor, not chat.

### Scene break suggestions

A toolbar action that reads the current chapter and proposes where to place `---` scene breaks. Each suggestion is anchored to a verbatim quote with severity (strong / moderate / subtle) and pacing analysis. Review-only — the writer inserts breaks by hand.

### Reasoning toggle

A toggle in the Writing Companion that surfaces the model's reasoning trace alongside the answer. Hidden when the active model does not support reasoning (driven by OpenRouter's `supported_parameters`).

### Canon / Reference toggle

When profile chips are attached, a toggle lets the writer declare whether the AI should treat attached profiles as **canon** (enforce strictly) or **reference** (the writer's direction wins).

### Context chips

The writer attaches profiles, summaries, and notes as chips. Each chip has include flags so the writer can choose what part of the profile actually goes into the prompt:

- **Summary** — the profile's `# Full AI Summary` section
- **Traits** — structured trait blocks
- **Overview** — the human-written `# Overview` section
- **Details** — the rest of the body

Defaults are Summary + Traits on. The Profile Builder chat uses a more permissive default that includes the entire profile.

### Multi-character handling

When multiple character chips are attached, each profile's body is wrapped with explicit `=== BEGIN <TYPE>: <NAME> ===` / `=== END ===` delimiters in the prompt so the AI does not conflate traits across characters.

### Selection vs. full chapter

With nothing selected, the chat treats the whole chapter as context (capped at 100K characters). With a passage selected, only that passage is sent (capped at 30K). Selection highlight persists while the chat is focused.

## Series structure

A series is a parent folder that contains multiple book projects plus a shared `series-profiles/` directory.

- **Canonical profiles** live at the series level and stay consistent across books.
- **Arc files** live in each book's `arcs/` folder and overlay book-specific changes onto the canonical profile (different relationship status, new injuries, evolving motivations).
- **Profile merge** combines canonical + arc at request time so AI sees the right state for the book the writer is in.
- The **ChipPicker** offers a "This Book" / "Series Profiles" toggle so the writer can attach either source.
- **Story context** (`series.json` + `project.json`) is automatically prepended to every AI system prompt so the model knows the project's tone, genre, content mode, and POV defaults.

## Summaries

### Chapter summaries

One file per chapter under `summaries/chapters/`. Generated on demand from the chapter prose. Prompt is tuned to "cliff notes" framing: gist as primary directive, grounding rules secondary, no rewriting in polished prose.

### Scene summaries

Per-scene files at `summaries/scenes/<chapter-stem>/scene-NN.md`. Two ways to create them:

- **Auto-split** — the chapter's `---` horizontal rule scene breaks drive a sequential generator; each scene gets its own summary file with a yes / no / cancel overwrite prompt
- **Selection-based** — a modal lets the writer preview a summary of the selected text and pick the slot it belongs in

The sidebar shows scene summaries as expandable grandchildren under each chapter.

### Scene beats

Each scene summary supports a `## Beats` checklist — a list of plot beats the writer wants to hit in the scene. Beats render as checkboxes in the sidebar under each scene. The writer can add, reorder, and check off beats. Beats are preserved across AI summary regeneration — the AI never touches the beats section when regenerating a scene summary.

## Book Details

Project-level narrative parameters stored in `project.json` and automatically injected into every AI system prompt:

- **Theme** — the story's central theme or question
- **Setting** — time period, world, location
- **Point of View** — first person, third limited, omniscient, etc.
- **Tense** — past, present
- **Target Audience** — YA, adult, etc.
- **Target Word Count** — stored in outline frontmatter, drives the progress gauge

These fields ensure the AI always knows the project's narrative context without the writer having to repeat it in every conversation.

## Export

Two export modes, both run from `POST /api/export/full-manuscript` and `POST /api/export/snapshot`:

- **Full manuscript** — combines chapters in order into a single file in `exports/`. Optional flags append chapter summaries, scene summaries, notes, and profiles as `#` appendices.
- **Manual snapshot** — dated folder under `exports/snapshot-YYYY-MM-DD/` mirroring the project layout, with the same opt-in toggles for summaries, notes, and profiles.

## Settings

A modal accessible from the sidebar. Sections:

- **API key** — OpenRouter key with masking and a Test Connection button
- **Default model** — model picker populated from OpenRouter's catalog with a cost-tier slider
- **Multi-provider support** — 22+ providers (OpenRouter, OpenAI, Anthropic, Google, Mistral, Groq, xAI, Together, Fireworks, DeepInfra, Perplexity, DeepSeek, GLM, Qwen, Moonshot, MiniMax, Baichuan, StepFun, SiliconFlow, MiMo, LM Studio, Ollama) with per-provider API keys, base URLs, and curated model lists
- **Content mode** — project-level default (`general`, `mature`, `explicit`) overridable per request
- **Model Routing** — allowlist, blocklist, and per-model content-mode declarations enforced at request time
- **Prompt caching** — toggle for Anthropic-style cache_control headers on repeated requests
- **Theme** — light / dark
- **Debug options**

## Content mode and routing

Three content modes: `general`, `mature`, `explicit`. Project-level default lives in `project.json`; individual requests may override.

Routing enforces two filters today:

- **Content compatibility** — `_validate_model_content_mode()` checks the model's declared `model_content_modes` in settings and rejects the request if the active mode is not allowed for that model
- **Allowlist / blocklist** — `_validate_model_allowed()` enforces per-project model lists

If no eligible model exists for a request, the app shows a clear error rather than silently degrading.

## Em dash policy

Open-Write uses an **advisory** em dash policy. Em dashes and en dashes are a legitimate prose choice and are NOT banned. Density is governed downstream by the deterministic `em_dash` lint (advisory, flags > 2.0 dashes/page) and by the naturalism critic, which hunts em-dash overuse, not presence.

The sanitizer (`backend/app/ai/sanitizer.py`) normalizes whitespace only and does NOT strip em/en dashes. This preserves the writer's punctuation choices and ensures critic reports match the source text.

## Auto-update

The packaged app checks GitHub Releases on launch (production builds only; dev builds skip the check). When a new version is available:

1. A slim banner appears at the top of the app.
2. **View details** opens a modal with the release notes (rendered Markdown), a download progress bar, and an explicit **Download & Install** button.
3. After install completes, the writer clicks **Relaunch** to load the new version.

Updates never download or install automatically.

A first-launch-after-update banner highlights the new version with a changelog link and a donation nudge.

## Open-Write Pipeline

An autonomous, resumable production pipeline that runs the full Open-Write methodology. The pipeline is gated by a deterministic completion gate and driven by the orchestrator (`backend/app/pipeline/orchestrator.py`).

### Pipeline phases

```
Bible → Voice → Editorial Lock → (per unit: Architect → Writer → Critics ×5 → Editorial → Verify) → Assemble → Adversarial Read → Finalize
```

Each phase produces a gate-valid artifact. The pipeline never auto-advances past a FAIL — the writer approves each step.

### Multi-format support

The pipeline adapts to the project's `story_type`:

| Format | Unit | Output | Assembly | Rule source |
|--------|------|--------|----------|-------------|
| Novel | Chapter | Markdown prose (`.md`) | `manuscript/novel.md` | `novel_template/.kilo/` |
| Screenplay | Scene | Fountain (`.fountain`) | `script/screenplay.fountain` | `screenplay_template/.kilo/` |
| TV | Episode | Fountain (`.fountain`) | `scripts/Season_1.fountain` | `tv_template/.kilo/` |

The pipeline labels adapt automatically (e.g. "Screenwriter" instead of "Prose writer", "Scene Critics" instead of chapter critics). The manifest builder detects scene/episode headings in addition to chapter headings. Project creation creates type-appropriate folder structures.

### Pipeline screen (3 tabs)

- **Run tab** — phase roadmap (done/current/pending), gate verdict banner, phase output panel, Run Next Phase / Auto-run / Stop controls, user input override, model routing config
- **Outputs tab** — browsable artifact library organized by category (Bible / Voice Experiment / Design Documents / Prose / Reviews / Manifest) with markdown and JSON rendering
- **Chat tab** — Pipeline Companion: conversational chat with pipeline context, Apply to Brief, Re-run Phase

### Key pipeline features

- **Auto-run** — one-click automatic execution with 2s delay between phases
- **User input overrides** — provide your own content for any phase instead of generating via the model
- **Per-stage model routing** — assign Primary or Critic model to each phase
- **Post-critics revision loop** — REVISE verdict triggers automatic writer rewrite with critic feedback (max 2 retries)
- **Rerun with feedback** — when restarting a project with existing material, choose "Revise with Existing Feedback"
- **Critic model fallback** — if critic provider fails, falls back to primary model
- **Voice experiment** — structured voice selection with multiple candidates, review, and locked spec
- **Outline unification** — bible outline auto-synced to `notes/outline.md` (OutlinePlanner sees it)
- **Skeleton profiles** — auto-generated character profiles from the bible concept
- **Scene summaries** — auto-generated from architect plans
- **Start Fresh** — clear stale failed run state and start over
- **CLI tool** — `backend/tools/ow_cli.py` for command-line debugging

### Pipeline outputs

| Category | Contents |
|----------|----------|
| Bible | Concept, outline, format rules, locked voice spec |
| Voice Experiment | Candidate voices with samples, review/selection rationale, locked spec |
| Design Documents | Outline structure + per-chapter architect plans |
| Prose | Chapter manuscripts + assembled novel |
| Reviews | 5 critics per chapter (show/voice/palette/continuity/naturalism) + editorial + adversarial read |
| Manifest | Completion manifest, pipeline run state, completion certificate |

## Backend health monitor

A `useBackendHealth` hook polls `/health` every ten seconds. If the backend is unreachable, a single fixed-position banner replaces all the per-feature "Failed to fetch" errors that would otherwise clutter the UI. The banner dismisses itself when the backend returns.

## Donation infrastructure

- **About panel** with current version, license, donor self-attest flag, and links to GitHub Sponsors and Ko-fi
- **Periodic donation prompt** every 30–50 launches when the user has not marked themselves a donor (24-hour anti-nag dismiss)
- **Donor flag** is honor-system; checking it stops the prompts and shows a "Thank you for donating!" badge in the sidebar

## Packaging and distribution

- Tauri v2 bundle on Windows, distributed as a signed `.msi` from GitHub Releases
- FastAPI backend frozen via PyInstaller and shipped as a Tauri sidecar so end users do not need Python
- Update bundles are signed with a minisign key; the public key is embedded in the v1.0.0 binary and verified on every update download
- Apache 2.0 license
