# MCP Debugging Guide

*How to debug MCP server tool-call failures using the MCP Inspector and built-in diagnostics.*

---

## When to Use This

- Agent hallucinates tool parameters (wrong field names, invalid enum values)
- Agent calls the wrong tool for the task
- Tool returns unexpected errors or empty results
- State file appears corrupted after tool calls
- Transport connection drops or hangs

---

## Quick Start: MCP Inspector

The MCP Inspector is a local web panel for manually testing MCP server tool calls without running your full agent workflow.

### Install and Run

```bash
# Install the Inspector (one-time)
npx -y @modelcontextprotocol/inspector

# Run against your state server
npx @modelcontextprotocol/inspector node tools/state_server/index.js
```

This opens a local web panel where you can:
1. View all registered tool schemas
2. Manually construct and send tool call payloads
3. Inspect raw JSON-RPC 2.0 request/response packets
4. Test edge cases (missing fields, invalid enums, boundary values)

### What to Check in the Inspector

| Symptom | What to Inspect |
|---------|----------------|
| Agent sends wrong field names | Compare agent's payload against the tool's `inputSchema` |
| Agent uses invalid enum values | Check the `enum` arrays in the schema |
| Tool returns "File not found" | Verify the `file` parameter matches an existing state file |
| Empty or null results | Check the `path` parameter — dot notation must match actual JSON structure |

---

## Built-in Debugging Flags

The state server supports CLI flags for transport-level debugging without the Inspector.

### `--inspector` Mode

```bash
node tools/state_server/index.js --inspector
```

Logs every tool call and its full response to stderr. Use this when:
- You need to see what the agent is actually sending vs. what you expect
- You want to verify the server is returning correct data
- You're debugging a multi-turn workflow and need a trace

### `--verbose` Mode

```bash
node tools/state_server/index.js --verbose
```

Logs diagnostic messages (startup, tool listing, errors) without dumping full payloads. Lighter weight than `--inspector`.

### `--groups=` Filtering

```bash
# Only expose callback and timeline tools
node tools/state_server/index.js --groups=callbacks,timeline
```

Reduces the tool surface to specific groups. Useful for:
- **Debugging**: isolate which tool group causes hallucinations
- **Production**: reduce attention dilution by limiting tools to the current task context

---

## Tool Groups Reference

| Group | Tools Exposed | When to Use |
|-------|---------------|-------------|
| `state` | `state.get`, `state.set` | General state reads/writes |
| `facts` | `state.add_fact` | Recording established facts |
| `callbacks` | `state.add_callback`, `state.mark_paid_off`, `state.get_active_callbacks` | Callback lifecycle management |
| `audience` | `state.get_audience_phase` | Misdirection/audience tracking |
| `timeline` | `timeline.set` | Diegetic time management |
| `characters` | `state.update_character` | Character state updates |
| `scenes` | `state.update_scene_counter` | Scene progress tracking |
| `props` | `state.add_prop`, `state.record_dialogue` | Props and dialogue tracking |
| `all` | Everything (default) | Full access |

Combine groups: `--groups=callbacks,characters,timeline`

---

## Debugging Workflow

```
Step 1: Reproduce
  → Run the failing agent task with --inspector flag
  → Capture the exact tool call payload from stderr

Step 2: Isolate
  → Open MCP Inspector
  → Manually send the same payload
  → Confirm whether the server or the agent is at fault

Step 3: Validate Schema
  → Compare the payload against the tool's inputSchema
  → Check enum values, required fields, type constraints

Step 4: Check State
  → Use state.get to read the relevant state file
  → Verify the JSON structure matches what the tool expects

Step 5: Fix
  → If server bug: fix handler logic in index.js
  → If agent bug: update system prompt or mode rules to constrain tool usage
  → If schema gap: add missing fields or enums to the tool definition
```

---

## Common Issues

### "Unknown tool: X"

The agent is calling a tool that isn't registered. Check:
- Tool name spelling (must match exactly, e.g. `state.get` not `state_get`)
- Tool groups — if using `--groups=`, the tool may be in a different group

### "File not found: X.json"

The state file doesn't exist. Check:
- `state/` directory exists relative to the server's working directory
- File name matches the `file` enum: `project_state`, `callback_ledger`, `audience_state`, `timeline`

### Agent Hallucinates Parameters

The agent invents field names or values not in the schema. Fix:
- Run with `--inspector` to see exactly what the agent sends
- Update the agent's system prompt to reference the tool schema explicitly
- Use `--groups=` to reduce the number of tools (fewer tools = fewer hallucinations)

### State File Corruption

If the JSON file becomes malformed:
1. Stop the server
2. Validate the JSON: `python -c "import json; json.load(open('state/project_state.json'))"`
3. If corrupted, restore from git or rebuild from the template

---

## Chrome DevTools (SSE Transport)

If using SSE transport instead of stdio, Chrome DevTools can trace the HTTP stream:
1. Open Chrome → DevTools → Network tab
2. Filter by "EventStream"
3. Inspect incoming SSE messages for tool call/response payloads

This is only relevant for remote MCP deployments. Local stdio servers use the Inspector instead.

---

*Last updated: 2026-06-15 (v1.1.1)*
