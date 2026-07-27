// pipelineApi.ts -- typed client for the Open-Write pipeline Output Library +
// live-control + chat endpoints (the t-001/t-002/t-003 backend).
//
// Kept in one place so both the Output Library tab and the Pipeline Chat tab
// share the same fetch logic and response shapes. Mirrors the hand-rolled
// fetch pattern already used in Pipeline.tsx for run-state/advance-phase.

export const PIPELINE_API_BASE = "http://localhost:8000";

// ── Catalog types (mirrors backend/app/pipeline/outputs.py) ──────────────────

export interface CatalogEntry {
  path: string;
  exists: boolean;
  words: number | null;
  mtime?: string;
  label?: string;
  group?: string;
  chapter?: number;
  critic_type?: string;
}

export interface CatalogCategory {
  key: "bible" | "voice" | "design" | "prose" | "reviews" | "manifest";
  label: string;
  count: number;
  exists_count: number;
  entries: CatalogEntry[];
}

export interface OutputCatalog {
  project_path: string;
  generated_at: string;
  categories: CatalogCategory[];
}

export interface ArtifactContent {
  path: string;
  exists: boolean;
  content: string;
  words: number | null;
  kind: "markdown" | "json";
}

// ── Run-state (mirrors Pipeline.tsx RunStateResponse) ────────────────────────

export interface RunStateResponse {
  active: boolean;
  status?: string;
  current_phase?: string;
  current_phase_label?: string;
  current_unit_index?: number;
  units?: number[];
  instructions?: string;
  last_error?: string | null;
}

// ── Chat types (mirrors backend PipelineChatResponse) ────────────────────────

export interface PipelineChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface PipelineChatResponse {
  reply: string;
  suggested_instructions: string | null;
  model_used: string;
}

// ── Calls ────────────────────────────────────────────────────────────────────

function qs(projectPath: string, extra: Record<string, string> = {}): string {
  const params = new URLSearchParams({ project_path: projectPath, ...extra });
  return params.toString();
}

export async function fetchCatalog(projectPath: string): Promise<OutputCatalog> {
  const res = await fetch(`${PIPELINE_API_BASE}/api/pipeline/outputs?${qs(projectPath)}`);
  if (!res.ok) throw new Error("Could not load pipeline outputs.");
  return res.json();
}

export async function fetchArtifact(projectPath: string, path: string): Promise<ArtifactContent> {
  const res = await fetch(
    `${PIPELINE_API_BASE}/api/pipeline/output-file?${qs(projectPath, { path })}`,
  );
  if (!res.ok) throw new Error("Could not load that artifact.");
  return res.json();
}

export async function fetchRunState(projectPath: string): Promise<RunStateResponse> {
  const res = await fetch(`${PIPELINE_API_BASE}/api/pipeline/run-state?${qs(projectPath)}`);
  if (!res.ok) throw new Error("Could not load pipeline state.");
  return res.json();
}

export async function updateInstructions(projectPath: string, instructions: string): Promise<RunStateResponse> {
  const res = await fetch(`${PIPELINE_API_BASE}/api/pipeline/update-instructions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ project_path: projectPath, instructions }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? "Could not update the brief.");
  }
  return res.json();
}

export async function rerunPhase(projectPath: string, phase: string, chapter?: number): Promise<RunStateResponse> {
  const res = await fetch(`${PIPELINE_API_BASE}/api/pipeline/rerun-phase`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ project_path: projectPath, phase, chapter }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? "Could not re-run that phase.");
  }
  return res.json();
}

export async function setRunStatus(projectPath: string, status: "running" | "paused" | "complete" | "failed"): Promise<RunStateResponse> {
  const res = await fetch(`${PIPELINE_API_BASE}/api/pipeline/set-status`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ project_path: projectPath, status }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? "Could not change run status.");
  }
  return res.json();
}

export async function pipelineChat(
  projectPath: string,
  messages: PipelineChatMessage[],
  opts: { modelId?: string; contextArtifact?: string; contextChapter?: number } = {},
): Promise<PipelineChatResponse> {
  const res = await fetch(`${PIPELINE_API_BASE}/api/pipeline/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      project_path: projectPath,
      messages,
      model_id: opts.modelId,
      context_artifact: opts.contextArtifact,
      context_chapter: opts.contextChapter,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? "The pipeline companion could not respond.");
  }
  return res.json();
}
