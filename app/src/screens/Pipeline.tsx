// Pipeline.tsx -- Open-Write Autonomous Pipeline panel (Phase P)
// ================================================================
// A full-width view that drives the Open-Write production pipeline phase by
// phase, gated by the deterministic completion gate. Each click of [Run Phase]
// advances exactly ONE phase (Bible -> Voice -> Editorial Lock -> per-unit
// Architect -> Writer -> Critics -> Editorial -> Verify -> Assemble ->
// Adversarial Read -> Finalize) and surfaces the artifact + gate verdict for
// human approval before continuing. The orchestrator NEVER auto-advances past
// a FAIL, so the writer stays in control.
//
// Data flow:
//   mount          -> GET  /api/pipeline/run-state   (is a run active?)
//   [Start Run]    -> POST /api/pipeline/start-run
//   [Run Phase]    -> POST /api/pipeline/advance-phase  (one phase)
//   poll after run -> GET  /api/pipeline/run-state
//
// The pipeline backend (backend/app/pipeline/orchestrator.py) is the sole
// authority on phase ordering and gate verdicts; this component only displays
// results and lets the writer choose when to continue.

import { useState, useEffect, useCallback } from "react";
import { ArrowLeft, Play, Loader2, CheckCircle2, XCircle, AlertCircle } from "lucide-react";
import type { ProjectInfo } from "../types/project";

const API_BASE = "http://localhost:8000";

// Mirror of orchestrator.ALL_PHASES, in execution order. Kept here so the UI
// can render the full roadmap (with done/current/pending states) even before
// the backend reports them.
const PHASE_ROADMAP: { key: string; label: string; scope: "project" | "per_unit" }[] = [
  { key: "bible",         label: "Bible (concept / outline / format)", scope: "project" },
  { key: "voice",         label: "Voice selection",                    scope: "project" },
  { key: "editorial_lock",label: "Editorial review + outline lock",    scope: "project" },
  { key: "architect",     label: "Architect (per-unit plan)",          scope: "per_unit" },
  { key: "writer",        label: "Prose writer (draft)",               scope: "per_unit" },
  { key: "critics",       label: "Critics (show/voice/palette/continuity/naturalism)", scope: "per_unit" },
  { key: "editorial",     label: "Editorial eval (per unit)",          scope: "per_unit" },
  { key: "verify_unit",   label: "Verify (per-unit gate)",             scope: "per_unit" },
  { key: "assemble",      label: "Assemble manuscript",                scope: "project" },
  { key: "adversarial",   label: "Adversarial read (full manuscript)", scope: "project" },
  { key: "finalize",      label: "Finalize (the gate)",                scope: "project" },
];

const UNIT_PHASE_KEYS = new Set(["architect", "writer", "critics", "editorial", "verify_unit"]);

interface RunStateResponse {
  active: boolean;
  status?: string;
  current_phase?: string;
  current_phase_label?: string;
  current_unit_index?: number;
  units?: number[];
  instructions?: string;
  last_error?: string | null;
  phase_results?: Record<string, unknown>;
  unit_results?: Record<string, Record<string, unknown>>;
}

interface AdvanceResponse {
  phase: string;
  phase_label?: string;
  result?: Record<string, unknown>;
  next_phase?: string | null;
  next_phase_label?: string | null;
  state?: RunStateResponse;
  model_used?: string;
}

interface PipelineProps {
  project: ProjectInfo;
  onBack: () => void;
}

// ── Pipeline screen ──────────────────────────────────────────────────────────

export function Pipeline({ project, onBack }: PipelineProps) {
  const [runState, setRunState] = useState<RunStateResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [lastAdvance, setLastAdvance] = useState<AdvanceResponse | null>(null);
  const [instructions, setInstructions] = useState("");
  const [error, setError] = useState<string | null>(null);

  // Load the current run state on mount and after each phase.
  const refresh = useCallback(async () => {
    try {
      const params = new URLSearchParams({ project_path: project.root_path });
      const res = await fetch(`${API_BASE}/api/pipeline/run-state?${params}`);
      if (!res.ok) throw new Error("Could not load pipeline state.");
      const data: RunStateResponse = await res.json();
      setRunState(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load run state.");
    } finally {
      setLoading(false);
    }
  }, [project.root_path]);

  useEffect(() => { void refresh(); }, [refresh]);

  async function handleStartRun() {
    setLoading(true);
    setError(null);
    setLastAdvance(null);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/start-run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_path: project.root_path,
          project_name: project.title,
          instructions: instructions,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? "Could not start run.");
      }
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Start run failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleAdvance() {
    setRunning(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/advance-phase`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_path: project.root_path,
          instructions: instructions,
        }),
      });
      const data: AdvanceResponse = await res.json();
      if (!res.ok) {
        throw new Error((data as unknown as { detail?: string }).detail ?? "Phase failed.");
      }
      setLastAdvance(data);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Advance failed.");
    } finally {
      setRunning(false);
    }
  }

  // ── Derive roadmap state (done / current / pending) ─────────────────────
  const currentPhase = runState?.current_phase;
  const runComplete = runState?.status === "complete";
  const runFailed = runState?.status === "failed";
  const flatOrder = PHASE_ROADMAP.map(p => p.key);
  const currentIndex = currentPhase ? flatOrder.indexOf(currentPhase) : -1;

  const phaseStatus = (key: string): "done" | "current" | "pending" => {
    if (runComplete) return "done";
    const idx = flatOrder.indexOf(key);
    if (currentIndex < 0) return "pending";
    if (idx < currentIndex) return "done";
    if (idx === currentIndex) return "current";
    return "pending";
  };

  // Gate verdict from the last advance (for the current/just-run phase).
  const lastGate = extractGate(lastAdvance?.result);
  const gateVerdict = lastGate?.verdict;

  return (
    <div className="flex min-w-0 flex-1 flex-col overflow-hidden bg-bg-base">

      {/* ── Title bar ────────────────────────────────────────────────────── */}
      <div className="flex shrink-0 items-center justify-between border-b border-border bg-bg-panel px-4 py-2">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="rounded p-1 text-text-muted hover:bg-bg-surface hover:text-text-primary transition-colors"
            title="Back to editor"
          >
            <ArrowLeft className="h-4 w-4" />
          </button>
          <h1 className="text-sm font-semibold text-text-primary">Autonomous Pipeline</h1>
          {runState?.active && (
            <span className={`rounded px-2 py-0.5 text-xs ${
              runComplete ? "bg-green-500/15 text-green-400" :
              runFailed   ? "bg-red-500/15 text-red-400" :
                            "bg-blue-500/15 text-blue-400"
            }`}>
              {runComplete ? "complete" : runFailed ? "failed" : runState.status}
            </span>
          )}
        </div>
        <div className="text-xs text-text-muted">
          {runState?.active && runState.units && runState.units.length > 0 && (
            <span>Unit {Math.min((runState.current_unit_index ?? 0) + 1, runState.units.length)} / {runState.units.length}</span>
          )}
        </div>
      </div>

      <div className="flex min-h-0 flex-1 overflow-hidden">

        {/* ── Left: phase roadmap ──────────────────────────────────────── */}
        <div className="w-72 shrink-0 overflow-y-auto border-r border-border p-4">
          {!runState?.active ? (
            <div className="rounded border border-dashed border-border p-4 text-center">
              <p className="mb-3 text-sm text-text-muted">No pipeline run in progress.</p>
              <div className="mb-3 text-left">
                <label className="mb-1 block text-xs font-medium text-text-muted">
                  Custom Instructions (optional)
                </label>
                <textarea
                  value={instructions}
                  onChange={(e) => setInstructions(e.target.value)}
                  placeholder="e.g. 'Write in the style of Cormac McCarthy. Focus on themes of isolation and memory. Target 90k words across 12 chapters.'"
                  rows={4}
                  className="w-full rounded border border-border bg-bg-surface px-2 py-1.5 text-xs text-text-base placeholder:text-text-muted focus:border-accent focus:outline-none"
                />
                <p className="mt-1 text-xs text-text-muted">
                  These instructions are appended to every phase's prompt — the LLM will honor them across bible, writer, and critic phases.
                </p>
              </div>
              <button
                onClick={handleStartRun}
                disabled={loading}
                className="inline-flex items-center gap-2 rounded bg-accent px-3 py-1.5 text-sm font-medium text-white hover:bg-accent/90 disabled:opacity-50"
              >
                <Play className="h-4 w-4" /> Start Run
              </button>
            </div>
          ) : (
            <ol className="space-y-1">
              {PHASE_ROADMAP.map((phase) => {
                const status = phaseStatus(phase.key);
                const isUnit = phase.scope === "per_unit";
                return (
                  <li key={phase.key}>
                    <div className={`flex items-start gap-2 rounded px-2 py-1.5 text-sm ${
                      status === "current" ? "bg-accent/10 text-text-primary" : "text-text-muted"
                    }`}>
                      <span className="mt-0.5 shrink-0">
                        {status === "done" ? (
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                        ) : status === "current" ? (
                          <Loader2 className="h-4 w-4 animate-spin text-accent" />
                        ) : (
                          <span className="block h-4 w-4 rounded-full border border-border" />
                        )}
                      </span>
                      <span className="leading-tight">
                        {phase.label}
                        {isUnit && runState.units && (
                          <span className="ml-1 text-xs text-text-muted">
                            (per chapter)
                          </span>
                        )}
                      </span>
                    </div>
                  </li>
                );
              })}
            </ol>
          )}
        </div>

        {/* ── Right: current phase output + controls ──────────────────── */}
        <div className="min-w-0 flex-1 overflow-y-auto p-6">

          {error && (
            <div className="mb-4 flex items-start gap-2 rounded border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-400">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}
          {runState?.last_error && (
            <div className="mb-4 rounded border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-400">
              {runState.last_error}
            </div>
          )}

          {runState?.active && runState.instructions && (
            <div className="mb-4 rounded border border-accent/30 bg-accent/5 p-3">
              <div className="mb-1 text-xs font-semibold text-accent">Creative Brief</div>
              <p className="text-xs text-text-muted whitespace-pre-wrap">{runState.instructions}</p>
            </div>
          )}

          {!runState?.active ? (
            <div className="text-sm text-text-muted">
              <p className="mb-2">The Open-Write pipeline runs the full novel-production sequence, gated by the deterministic completion gate:</p>
              <p className="font-mono text-xs leading-relaxed">
                BIBLE → VOICE → EDITORIAL LOCK → (per chapter: ARCHITECT → WRITE → CRITICS → EDITORIAL → VERIFY) → ASSEMBLE → ADVERSARIAL READ → FINALIZE
              </p>
              <p className="mt-3">Each phase produces a gate-valid artifact. The pipeline never auto-advances past a FAIL — you approve each step.</p>
            </div>
          ) : (
            <>
              {/* Current phase header */}
              <div className="mb-4">
                <div className="text-xs uppercase tracking-wide text-text-muted">Current phase</div>
                <div className="text-lg font-semibold text-text-primary">
                  {runComplete ? "Run complete" : runState.current_phase_label ?? runState.current_phase}
                </div>
                {!runComplete && runState.units && UNIT_PHASE_KEYS.has(currentPhase ?? "") && (
                  <div className="text-sm text-text-muted">
                    Chapter {runState.units[currentUnitIndexClamped(runState)]}
                  </div>
                )}
              </div>

              {/* Gate verdict banner */}
              {lastGate && (
                <GateBanner verdict={gateVerdict} gate={lastGate} />
              )}

              {/* Last phase result */}
              {lastAdvance?.result && (
                <PhaseResult result={lastAdvance.result} phase={lastAdvance.phase} />
              )}

              {/* Controls */}
              <div className="mt-6 flex items-center gap-3">
                {!runComplete && (
                  <button
                    onClick={handleAdvance}
                    disabled={running}
                    className="inline-flex items-center gap-2 rounded bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent/90 disabled:opacity-50"
                  >
                    {running ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                    {running ? "Running..." : "Run Next Phase"}
                  </button>
                )}
                {runComplete && (
                  <span className="inline-flex items-center gap-2 text-sm text-green-400">
                    <CheckCircle2 className="h-4 w-4" /> Pipeline complete — COMPLETION_PASS written.
                  </span>
                )}
                {lastAdvance?.model_used && (
                  <span className="text-xs text-text-muted">model: {lastAdvance.model_used}</span>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function currentUnitIndexClamped(run: RunStateResponse): number {
  const idx = run.current_unit_index ?? 0;
  if (!run.units || run.units.length === 0) return idx;
  return Math.min(idx, run.units.length - 1);
}

// The gate shape varies by phase. It can be a chapter gate ({verdict, ...}) or
// a finalize result ({finalize_verdict, ...}). Normalize to a {verdict, ...} view.
function extractGate(result?: Record<string, unknown>): { verdict?: string } & Record<string, unknown> | null {
  if (!result) return null;
  if (result.gate && typeof result.gate === "object") {
    return result.gate as { verdict?: string } & Record<string, unknown>;
  }
  if (result.finalize_result && typeof result.finalize_result === "object") {
    const fr = result.finalize_result as { finalize_verdict?: string };
    return { verdict: fr.finalize_verdict, ...fr };
  }
  return null;
}

function GateBanner({ verdict, gate }: { verdict?: string; gate: Record<string, unknown> }) {
  if (!verdict) return null;
  const pass = verdict === "PASS" || verdict === "COMPLETE";
  const fail = verdict === "FAIL" || verdict === "INCOMPLETE" || verdict === "INVALIDATED";
  const Icon = pass ? CheckCircle2 : fail ? XCircle : AlertCircle;
  const color = pass ? "text-green-400" : fail ? "text-red-400" : "text-yellow-400";
  const border = pass ? "border-green-500/40 bg-green-500/10"
              : fail ? "border-red-500/40 bg-red-500/10"
                     : "border-yellow-500/40 bg-yellow-500/10";
  const chapterFailures = Array.isArray(gate.chapter_failures) ? gate.chapter_failures : [];
  return (
    <div className={`mb-4 flex items-start gap-2 rounded border ${border} p-3 text-sm`}>
      <Icon className={`mt-0.5 h-4 w-4 shrink-0 ${color}`} />
      <div className="min-w-0">
        <div className={`font-medium ${color}`}>Gate: {verdict}</div>
        {chapterFailures.length > 0 && (
          <ul className="mt-1 list-disc pl-4 text-xs text-text-muted">
            {chapterFailures.slice(0, 8).map((f, i) => (
              <li key={i}>{typeof f === "string" ? f : JSON.stringify(f)}</li>
            ))}
            {chapterFailures.length > 8 && <li>...and {chapterFailures.length - 8} more</li>}
          </ul>
        )}
      </div>
    </div>
  );
}

function PhaseResult({ result, phase }: { result: Record<string, unknown>; phase: string }) {
  // Render the artifact path(s) and a JSON preview of the result.
  const artifacts: string[] = [];
  if (typeof result.artifact === "string") artifacts.push(result.artifact);
  if (Array.isArray(result.artifacts)) artifacts.push(...result.artifacts.filter((a): a is string => typeof a === "string"));
  const critics = Array.isArray(result.critics) ? result.critics as Array<Record<string, unknown>> : [];
  const wordCount = typeof result.word_count === "number" ? result.word_count : null;
  const manifest = result.manifest as { chapters_detected?: number; total_items?: number } | undefined | null;

  return (
    <div className="rounded border border-border bg-bg-panel p-4">
      <div className="mb-2 text-xs uppercase tracking-wide text-text-muted">Phase output — {phase}</div>
      {wordCount !== null && (
        <div className="mb-2 text-sm text-text-primary">Word count: <span className="font-mono">{wordCount}</span></div>
      )}
      {manifest && (
        <div className="mb-2 text-sm text-text-primary">
          Manifest: <span className="font-mono">{manifest.chapters_detected}</span> chapters, <span className="font-mono">{manifest.total_items}</span> check items
        </div>
      )}
      {artifacts.length > 0 && (
        <div className="mb-2">
          <div className="text-xs text-text-muted">Artifacts written:</div>
          <ul className="mt-1 list-disc pl-4 font-mono text-xs text-text-primary">
            {artifacts.map((a, i) => <li key={i}>{a}</li>)}
          </ul>
        </div>
      )}
      {critics.length > 0 && (
        <div className="mb-2">
          <div className="text-xs text-text-muted">Critics ({critics.length}):</div>
          <ul className="mt-1 space-y-1 text-xs">
            {critics.map((c, i) => (
              <li key={i} className="font-mono text-text-primary">
                {String(c.critic_type ?? "")}: verdict={String(c.verdict ?? "?")} findings={String(c.located_findings ?? 0)} {c.gate_substance_ok ? "✓" : "✗"}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
