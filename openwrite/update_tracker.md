# Open-Write Update Tracker

*Tracks all changes made to the Open-Write project across versions.*

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
