#!/usr/bin/env node
/**
 * Open-Write State MCP Server v1.1.1
 * Provides constrained operations on the screenplay state files.
 * Prevents JSON schema corruption by validating all operations.
 *
 * v1.1.1 changes:
 *   - Added tool groups for context-aware tool exposure (RAG-style)
 *   - Added --groups CLI flag to filter exposed tools by context
 *   - Added --inspector flag for MCP Inspector debugging support
 *   - Added verbose logging mode for transport debugging
 *
 * Interface:
 *   state.get(path)                    - Read a value from any state file
 *   state.set(path, value)             - Set a value in any state file
 *   state.add_fact(scene, fact)        - Add a fact to project_state.json
 *   state.add_callback(seed)           - Add a callback seed to callback_ledger.json
 *   state.mark_paid_off(seed_id, scene)- Mark a callback as paid off
 *   state.get_active_callbacks()       - Get all unpaid callbacks
 *   state.get_audience_phase(track, scene) - Get the audience belief for a track at a scene
 *   timeline.set(scene, timestamp, t_minus) - Set a timeline entry
 *   state.update_character(character, field, value) - Update a character's state
 *   state.update_scene_counter(scene)  - Update current scene number
 *
 * Tool Groups (for --groups flag):
 *   state      - state.get, state.set
 *   facts      - state.add_fact
 *   callbacks  - state.add_callback, state.mark_paid_off, state.get_active_callbacks
 *   audience   - state.get_audience_phase
 *   timeline   - timeline.set
 *   characters - state.update_character
 *   scenes     - state.update_scene_counter
 *   props      - state.add_prop, state.record_dialogue
 *   all        - everything (default)
 */

const { Server } = require("@modelcontextprotocol/sdk/server/index.js");
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require("@modelcontextprotocol/sdk/types.js");
const fs = require("fs");
const path = require("path");

const STATE_DIR = path.resolve(__dirname, "..", "..", "state");

// ─── CLI Arguments ───

const args = process.argv.slice(2);
const INSPECTOR_MODE = args.includes("--inspector");
const VERBOSE = args.includes("--verbose") || INSPECTOR_MODE;
const groupsArg = args.find((a) => a.startsWith("--groups="));
const requestedGroups = groupsArg
  ? groupsArg.split("=")[1].split(",").map((g) => g.trim().toLowerCase())
  : ["all"];

function log(...msg) {
  if (VERBOSE) console.error("[state-server]", ...msg);
}

// ─── Helpers ───

function readJson(filename) {
  const filepath = path.join(STATE_DIR, filename);
  try {
    return JSON.parse(fs.readFileSync(filepath, "utf-8"));
  } catch (e) {
    if (e.code === "ENOENT") return null;
    throw e;
  }
}

function writeJson(filename, data) {
  const filepath = path.join(STATE_DIR, filename);
  fs.writeFileSync(filepath, JSON.stringify(data, null, 2) + "\n", "utf-8");
}

function resolvePath(obj, dotPath) {
  const parts = dotPath.split(".");
  let current = obj;
  for (const part of parts) {
    if (current == null || typeof current !== "object") return undefined;
    current = current[part];
  }
  return current;
}

function setAtPath(obj, dotPath, value) {
  const parts = dotPath.split(".");
  let current = obj;
  for (let i = 0; i < parts.length - 1; i++) {
    if (!(parts[i] in current) || typeof current[parts[i]] !== "object") {
      current[parts[i]] = {};
    }
    current = current[parts[i]];
  }
  current[parts[parts.length - 1]] = value;
}

// ─── Tool Definitions ───

const TOOLS = [
  {
    name: "state.get",
    description:
      "Read a value from any state file. Path uses dot notation: 'project_state.characters.mira.knowledge'",
    inputSchema: {
      type: "object",
      properties: {
        file: {
          type: "string",
          enum: ["project_state", "callback_ledger", "audience_state", "timeline"],
          description: "Which state file to read from",
        },
        path: {
          type: "string",
          description: "Dot-notation path to the value (omit for entire file)",
        },
      },
      required: ["file"],
    },
  },
  {
    name: "state.set",
    description:
      "Set a value in a state file. Path uses dot notation. Validates that the file exists.",
    inputSchema: {
      type: "object",
      properties: {
        file: {
          type: "string",
          enum: ["project_state", "callback_ledger", "audience_state", "timeline"],
        },
        path: {
          type: "string",
          description: "Dot-notation path to set",
        },
        value: {
          description: "The value to set (any JSON type)",
        },
      },
      required: ["file", "path", "value"],
    },
  },
  {
    name: "state.add_fact",
    description: "Add a fact to project_state.json facts_established array",
    inputSchema: {
      type: "object",
      properties: {
        scene: { type: "number", description: "Scene number where fact is established" },
        fact: { type: "string", description: "The fact to record" },
      },
      required: ["scene", "fact"],
    },
  },
  {
    name: "state.add_callback",
    description: "Add a new callback seed to callback_ledger.json",
    inputSchema: {
      type: "object",
      properties: {
        id: { type: "string", description: "Unique seed identifier (snake_case)" },
        seeded_in_scene: { type: "number" },
        must_pay_off_by_scene: { type: "number" },
        payoff_description: { type: "string" },
      },
      required: ["id", "seeded_in_scene", "must_pay_off_by_scene", "payoff_description"],
    },
  },
  {
    name: "state.mark_paid_off",
    description: "Mark a callback seed as paid off in callback_ledger.json",
    inputSchema: {
      type: "object",
      properties: {
        seed_id: { type: "string", description: "The seed ID to mark as paid off" },
        scene: { type: "number", description: "Scene number where payoff occurred" },
      },
      required: ["seed_id", "scene"],
    },
  },
  {
    name: "state.get_active_callbacks",
    description: "Get all unpaid callbacks from the ledger",
    inputSchema: {
      type: "object",
      properties: {},
    },
  },
  {
    name: "state.get_audience_phase",
    description: "Get the audience belief phase for a specific track at a specific scene",
    inputSchema: {
      type: "object",
      properties: {
        track_name: {
          type: "string",
          description:
            "Track name: great_filter_belief, qg_threat_response_belief, or theo_lines_reading",
        },
        scene: { type: "number", description: "Scene number to check" },
      },
      required: ["track_name", "scene"],
    },
  },
  {
    name: "timeline.set",
    description: "Set a timeline entry in timeline.json",
    inputSchema: {
      type: "object",
      properties: {
        scene: { type: "number", description: "Scene number" },
        diegetic_time: { type: "string", description: "Diegetic time string" },
        note: { type: "string", description: "Optional note" },
        orpheus_t_minus_hours: {
          type: "number",
          description: "Optional Orpheus countdown hours",
        },
      },
      required: ["scene", "diegetic_time"],
    },
  },
  {
    name: "state.update_character",
    description: "Update a field on a character in project_state.json",
    inputSchema: {
      type: "object",
      properties: {
        character: {
          type: "string",
          enum: ["mira", "daniel", "theo", "okafor", "thorn", "vessel"],
        },
        field: {
          type: "string",
          enum: ["active_parts", "knowledge", "info_asymmetry_owed", "physical_state"],
        },
        action: {
          type: "string",
          enum: ["set", "add", "remove"],
          description: "set replaces entire value, add appends, remove removes",
        },
        value: {
          description: "The value (string for set, string item for add/remove)",
        },
      },
      required: ["character", "field", "action", "value"],
    },
  },
  {
    name: "state.update_scene_counter",
    description: "Update the current_scene number in project_state.json",
    inputSchema: {
      type: "object",
      properties: {
        scene: { type: "number", description: "New current scene number" },
      },
      required: ["scene"],
    },
  },
  {
    name: "state.add_prop",
    description: "Add a prop/motif to project_state.json",
    inputSchema: {
      type: "object",
      properties: {
        name: { type: "string" },
        established_scene: { type: "number" },
        status: {
          type: "string",
          enum: ["active", "pending", "seeded_offscreen", "retired"],
        },
      },
      required: ["name"],
    },
  },
  {
    name: "state.record_dialogue",
    description: "Record a claimed dialogue line in project_state.json",
    inputSchema: {
      type: "object",
      properties: {
        line: { type: "string", description: "The dialogue line" },
        character: { type: "string" },
        scene: { type: "number" },
      },
      required: ["line", "character", "scene"],
    },
  },
];

// ─── Tool Groups (RAG-style context-aware exposure) ───

const TOOL_GROUPS = {
  state: ["state.get", "state.set"],
  facts: ["state.add_fact"],
  callbacks: ["state.add_callback", "state.mark_paid_off", "state.get_active_callbacks"],
  audience: ["state.get_audience_phase"],
  timeline: ["timeline.set"],
  characters: ["state.update_character"],
  scenes: ["state.update_scene_counter"],
  props: ["state.add_prop", "state.record_dialogue"],
};

function getToolsForGroups(groups) {
  if (groups.includes("all")) return TOOLS;
  const allowed = new Set();
  for (const g of groups) {
    if (TOOL_GROUPS[g]) TOOL_GROUPS[g].forEach((t) => allowed.add(t));
  }
  return TOOLS.filter((t) => allowed.has(t.name));
}

// ─── Tool Handlers ───

function handleStateGet(args) {
  const filename = args.file + ".json";
  const data = readJson(filename);
  if (!data) return { content: [{ type: "text", text: `File not found: ${filename}` }] };
  const value = args.path ? resolvePath(data, args.path) : data;
  return {
    content: [{ type: "text", text: JSON.stringify(value, null, 2) }],
  };
}

function handleStateSet(args) {
  const filename = args.file + ".json";
  const data = readJson(filename);
  if (!data) return { content: [{ type: "text", text: `File not found: ${filename}` }] };
  setAtPath(data, args.path, args.value);
  writeJson(filename, data);
  return {
    content: [{ type: "text", text: `Set ${args.file}.${args.path} = ${JSON.stringify(args.value)}` }],
  };
}

function handleAddFact(args) {
  const data = readJson("project_state.json");
  if (!data) return { content: [{ type: "text", text: "project_state.json not found" }] };
  if (!Array.isArray(data.facts_established)) data.facts_established = [];
  data.facts_established.push({ fact: args.fact, scene: args.scene });
  writeJson("project_state.json", data);
  return {
    content: [{ type: "text", text: `Added fact: "${args.fact}" (scene ${args.scene})` }],
  };
}

function handleAddCallback(args) {
  const data = readJson("callback_ledger.json");
  if (!data) return { content: [{ type: "text", text: "callback_ledger.json not found" }] };
  if (!Array.isArray(data.seeds)) data.seeds = [];
  
  // Check for duplicate ID
  if (data.seeds.some((s) => s.id === args.id)) {
    return { content: [{ type: "text", text: `Error: Seed "${args.id}" already exists` }] };
  }
  
  data.seeds.push({
    id: args.id,
    seeded_in_scene: args.seeded_in_scene,
    must_pay_off_by_scene: args.must_pay_off_by_scene,
    paid_off: false,
    payoff_description: args.payoff_description,
  });
  writeJson("callback_ledger.json", data);
  return {
    content: [{ type: "text", text: `Added callback seed: "${args.id}"` }],
  };
}

function handleMarkPaidOff(args) {
  const data = readJson("callback_ledger.json");
  if (!data) return { content: [{ type: "text", text: "callback_ledger.json not found" }] };
  const seed = data.seeds.find((s) => s.id === args.seed_id);
  if (!seed) {
    return { content: [{ type: "text", text: `Error: Seed "${args.seed_id}" not found` }] };
  }
  seed.paid_off = true;
  seed.paid_off_in_scene = args.scene;
  writeJson("callback_ledger.json", data);
  return {
    content: [{ type: "text", text: `Marked "${args.seed_id}" as paid off (scene ${args.scene})` }],
  };
}

function handleGetActiveCallbacks() {
  const data = readJson("callback_ledger.json");
  if (!data) return { content: [{ type: "text", text: "callback_ledger.json not found" }] };
  const active = data.seeds.filter((s) => !s.paid_off);
  return {
    content: [{ type: "text", text: JSON.stringify(active, null, 2) }],
  };
}

function handleGetAudiencePhase(args) {
  const data = readJson("audience_state.json");
  if (!data) return { content: [{ type: "text", text: "audience_state.json not found" }] };
  const track = data.tracks.find((t) => t.name === args.track_name);
  if (!track) {
    return { content: [{ type: "text", text: `Track "${args.track_name}" not found` }] };
  }
  
  for (const phase of track.phases) {
    const [start, end] = phase.scenes.split("-").map((s) => s.trim());
    const startNum = parseInt(start);
    const endNum = end === "end" ? 999 : parseInt(end);
    if (args.scene >= startNum && args.scene <= endNum) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              { track: args.track_name, scene: args.scene, ...phase },
              null,
              2
            ),
          },
        ],
      };
    }
  }
  return {
    content: [{ type: "text", text: `No phase found for scene ${args.scene} in track "${args.track_name}"` }],
  };
}

function handleTimelineSet(args) {
  const data = readJson("timeline.json");
  if (!data) return { content: [{ type: "text", text: "timeline.json not found" }] };
  if (!data.scenes) data.scenes = {};
  const entry = { diegetic_time: args.diegetic_time };
  if (args.note) entry.note = args.note;
  if (args.orpheus_t_minus_hours !== undefined) entry.orpheus_t_minus_hours = args.orpheus_t_minus_hours;
  data.scenes[String(args.scene)] = entry;
  writeJson("timeline.json", data);
  return {
    content: [{ type: "text", text: `Timeline set for scene ${args.scene}: ${args.diegetic_time}` }],
  };
}

function handleUpdateCharacter(args) {
  const data = readJson("project_state.json");
  if (!data) return { content: [{ type: "text", text: "project_state.json not found" }] };
  if (!data.characters) data.characters = {};
  if (!data.characters[args.character]) data.characters[args.character] = {};
  const char = data.characters[args.character];
  
  switch (args.action) {
    case "set":
      char[args.field] = args.value;
      break;
    case "add":
      if (!Array.isArray(char[args.field])) char[args.field] = [];
      if (!char[args.field].includes(args.value)) char[args.field].push(args.value);
      break;
    case "remove":
      if (Array.isArray(char[args.field])) {
        char[args.field] = char[args.field].filter((v) => v !== args.value);
      }
      break;
  }
  
  writeJson("project_state.json", data);
  return {
    content: [{ type: "text", text: `Updated ${args.character}.${args.field} (${args.action}): ${JSON.stringify(args.value)}` }],
  };
}

function handleUpdateSceneCounter(args) {
  const data = readJson("project_state.json");
  if (!data) return { content: [{ type: "text", text: "project_state.json not found" }] };
  data.current_scene = args.scene;
  writeJson("project_state.json", data);
  return {
    content: [{ type: "text", text: `Current scene updated to ${args.scene}` }],
  };
}

function handleAddProp(args) {
  const data = readJson("project_state.json");
  if (!data) return { content: [{ type: "text", text: "project_state.json not found" }] };
  if (!Array.isArray(data.props_and_motifs)) data.props_and_motifs = [];
  data.props_and_motifs.push({
    name: args.name,
    established_scene: args.established_scene ?? null,
    appearances: [],
    status: args.status || "pending",
  });
  writeJson("project_state.json", data);
  return {
    content: [{ type: "text", text: `Added prop: "${args.name}"` }],
  };
}

function handleRecordDialogue(args) {
  const data = readJson("project_state.json");
  if (!data) return { content: [{ type: "text", text: "project_state.json not found" }] };
  if (!Array.isArray(data.claimed_dialogue_lines)) data.claimed_dialogue_lines = [];
  data.claimed_dialogue_lines.push({
    line: args.line,
    character: args.character,
    scene: args.scene,
  });
  writeJson("project_state.json", data);
  return {
    content: [{ type: "text", text: `Recorded dialogue: "${args.line.substring(0, 60)}..." (${args.character})` }],
  };
}

// ─── Server Setup ───

const HANDLERS = {
  "state.get": handleStateGet,
  "state.set": handleStateSet,
  "state.add_fact": handleAddFact,
  "state.add_callback": handleAddCallback,
  "state.mark_paid_off": handleMarkPaidOff,
  "state.get_active_callbacks": handleGetActiveCallbacks,
  "state.get_audience_phase": handleGetAudiencePhase,
  "timeline.set": handleTimelineSet,
  "state.update_character": handleUpdateCharacter,
  "state.update_scene_counter": handleUpdateSceneCounter,
  "state.add_prop": handleAddProp,
  "state.record_dialogue": handleRecordDialogue,
};

const server = new Server(
  { name: "openwrite-state-server", version: "1.1.1" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  const filtered = getToolsForGroups(requestedGroups);
  log(`Listing ${filtered.length}/${TOOLS.length} tools (groups: ${requestedGroups.join(",")})`);
  return { tools: filtered };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  if (INSPECTOR_MODE) {
    log(`CALL ${name}`, JSON.stringify(args, null, 2));
  }
  const handler = HANDLERS[name];
  if (!handler) {
    log(`ERROR: Unknown tool: ${name}`);
    return {
      content: [{ type: "text", text: `Unknown tool: ${name}` }],
      isError: true,
    };
  }
  try {
    const result = handler(args || {});
    if (INSPECTOR_MODE) {
      log(`RESPOND ${name}`, JSON.stringify(result, null, 2));
    }
    return result;
  } catch (e) {
    log(`ERROR ${name}:`, e.message);
    return {
      content: [{ type: "text", text: `Error: ${e.message}` }],
      isError: true,
    };
  }
});

// ─── Start ───

async function main() {
  const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
  const transport = new StdioServerTransport();
  await server.connect(transport);
  log("Open-Write State MCP Server v1.1.1 running on stdio");
  if (INSPECTOR_MODE) log("Inspector mode enabled — all tool calls and responses will be logged");
  log(`Tool groups: ${requestedGroups.join(", ")} (${getToolsForGroups(requestedGroups).length} tools exposed)`);
}

main().catch((e) => {
  console.error("Fatal:", e);
  process.exit(1);
});
