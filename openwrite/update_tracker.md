# Open-Write Update Tracker

*Tracks all changes made to the Open-Write project across versions.*

---

## v1.0.6 — Storythread Sync

*Date: 2026-08-03*

### Summary

Ported safe updates from StorythreadStudio v1.0.5→v1.0.11 to Open-Write-Studio. This sync brings character creation tools, scene beats, Writing Companion enhancements (Draft/Enhance modes, reasoning toggle, canon/reference toggle), Book Details panel, chapter rename cascade, name generator, and multiple bug fixes — all without breaking Open-Write's multi-provider architecture, pipeline system, or advisory em-dash policy.

### New Files (35)

**Frontend — Sidebar Components:**
- `components/sidebar/ActGroup.tsx` + test
- `components/sidebar/ChapterNavRow.tsx`
- `components/sidebar/NavItem.tsx`
- `components/sidebar/NavSection.tsx`
- `components/sidebar/RowMenu.tsx`

**Frontend — Character Profiles:**
- `components/profiles/NameGeneratorPanel.tsx` + test
- `components/profiles/QuickBuildPanel.tsx`
- `components/profiles/SpinePickers.tsx`

**Frontend — Settings:**
- `components/settings/providerMeta.ts`
- `components/settings/ProviderPanel.tsx` + test

**Frontend — Editor:**
- `components/EditorMenu.tsx`

**Frontend — Data:**
- `data/characterSpines.ts` + test
- `data/traitPools.ts` + test
- `data/names/fantasyNames.ts` + test

**Frontend — Types/Utils/Hooks:**
- `types/structure.ts`
- `utils/autoSizeTextarea.ts`
- `utils/buildEditorChatPayload.ts` + test
- `utils/modelFiltering.ts` + test
- `hooks/useProjectUiState.ts` + test

**Backend:**
- `app/utils/structure_store.py` — Acts-based chapter ordering
- `app/utils/names_store.py` — Character name generator DB
- `app/routers/names.py` — `/api/names` endpoints
- `app/routers/structure.py` — `/api/structure` endpoints
- `app/data/names/*.json` — 4 name data files

### Modified Files

**Backend:**
- `routers/documents.py` — Scene beats, chapter rename cascade, structure store integration
- `routers/profiles.py` — `character_kind`, tolerant parsing
- `routers/projects.py` — Book Details fields, target_word_count
- `routers/ai.py` — Draft/Enhance modes, scene breaks, reasoning toggle, canon/reference, materials echo
- `ai/prompts.py` — New prompt rules for all new features
- `ai/openrouter.py` — `sanitize_mode`, `include_reasoning`, `supports_reasoning`
- `outline_frontmatter.py` — `set_target_word_count()`
- `progress_store.py` — `migrate_file_relpath()`
- `main.py` — Registered names and structure routers

**Frontend:**
- `App.tsx` — Save-time title sync, 300s timeout
- `types/ai.ts` — Beat, EnhanceLevel, SceneBreakSuggestion, supports_reasoning, new EditorChatPayload fields

### Bug Fixes

- **OpenRouter provider resolution** — Model IDs like `"openai/gpt-4o-mini"` no longer incorrectly resolve to the OpenAI provider; they correctly route through OpenRouter
- **Writing Companion clear** — Now properly resets established chips, chapter flag, context chips, and input
- **Sidebar title sync** — Chapter title updates immediately after saving if H1 was edited
- **Chat timeout** — Increased from 180s to 300s for slow reasoning models
- **Chapter numbering** — Uses max(prefix)+1 to avoid collisions after deletes
- **Tolerant profile parsing** — No more 400 errors on malformed profiles

### What Was NOT Changed (intentionally preserved)

- Multi-provider architecture (22+ providers with `resolve()`)
- Pipeline/harness system
- `.open-write/` branding
- Advisory em-dash policy
- "Chapter One" naming
- Screenplay/TV pilot story types

### Tests

- 246 backend tests pass (90 pre-existing + 156 new/adapted)
- TypeScript compiles cleanly
- 5 incompatible Storythread tests removed (provider system references)

---

## v1.1.1 — MCP Hardening Release

*Date: 2026-06-15*
*Basis: PDF review of "Agent Tools & Interoperability" (Google, May 2026)*

### Summary

Two actionable improvements extracted from the Google MCP whitepaper: (1) MCP Inspector integration for debugging tool-call failures, (2) RAG-style tool grouping to reduce attention dilution by exposing only context-relevant tools.

### Changed: `tools/state_server/index.js`

| Feature | v1.1.0 | v1.1.1 |
|---------|--------|--------|
| Version string | 1.0.0 | 1.1.1 |
| Tool groups | All 12 tools always exposed | 8 named groups (`state`, `facts`, `callbacks`, `audience`, `timeline`, `characters`, `scenes`, `props`) |
| `--groups=` flag | N/A | Filter exposed tools by context. Example: `--groups=callbacks,timeline` exposes only 4 tools |
| `--inspector` flag | N/A | Logs all tool calls and responses to stderr for MCP Inspector debugging |
| `--verbose` flag | N/A | Enables diagnostic logging (subset of inspector mode) |
| Server name in protocol | `qg-state-server@1.0.0` | `openwrite-state-server@1.1.1` |

### Changed: `tools/state_server/package.json`

- Version bumped from `1.0.0` to `1.1.1`

### New: `skills/mcp_debugging.md`

- New skill documenting MCP Inspector setup and usage
- Covers tool-call debugging workflow: Inspector → raw JSON-RPC inspection → schema validation
- Documents tool groups and when to use each

### Changed: `skills/start_here.md`

- Added MCP debugging skill to Key Methodologies table
- Added tool groups documentation to State Management section

### Design Decisions

1. **Tool groups are opt-in, default is "all"** — existing workflows are unaffected. Groups activate only with `--groups=` flag.
2. **Inspector mode goes to stderr** — MCP protocol uses stdout for JSON-RPC. All diagnostic logging goes to stderr to avoid corrupting the protocol stream.
3. **Groups are composable** — `--groups=callbacks,timeline` exposes tools from both groups. No need to list individual tool names.
4. **Server name corrected** — open-write server now properly identifies as `openwrite-state-server` (was incorrectly `qg-state-server` in v1.1.0).

### What This Does NOT Change

- No changes to tool schemas, input/output formats, or handler logic
- No changes to `.kilo/mcp.json` configuration (server still runs with `node tools/state_server/index.js`)
- No changes to any state files, bible files, or template files

---

## v1.1.0 — Completion Gate + Template Parity

*See `update_log.md` for full v1.1 changelog.*

---

*v1.1.0 baseline: Completion gate system, template parity, model-agnostic naming.*
