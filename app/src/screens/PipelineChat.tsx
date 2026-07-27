// PipelineChat.tsx -- the Open-Write pipeline companion chat (t-005)
// ==================================================================
// A conversational panel that knows where the run is and what it has produced,
// so the writer can steer continued output in plain language ("make chapter 3
// more melancholic", "tighten the dialogue and regenerate chapter 2").
//
// Two action levers, surfaced from the chat:
//   1. Apply to Brief -- when the companion proposes a revised creative brief
//      (SUGGESTED_BRIEF), the writer can apply it with one click; every future
//      phase then honors the new direction.
//   2. Re-run Phase   -- regenerate a specific phase (and chapter) so a change
//      takes effect on already-produced material.
//
// Mirrors the Writing Companion UX (App.tsx editor-chat): multi-turn, markdown
// bubbles via ChatMarkdown, abortable requests.

import { useState, useRef, useCallback } from "react";
import { Send, Loader2, AlertCircle, RotateCcw, Sparkles, Check, X } from "lucide-react";
import type { ProjectInfo } from "../types/project";
import { ChatMarkdown } from "../components/ChatMarkdown";
import {
  pipelineChat, updateInstructions, rerunPhase,
  type PipelineChatMessage, type RunStateResponse,
} from "../utils/pipelineApi";

const UNIT_PHASES = ["architect", "writer", "critics", "editorial", "verify_unit"];
const RERUNNABLE_PHASES: { key: string; label: string }[] = [
  { key: "bible",          label: "Bible" },
  { key: "voice",          label: "Voice selection" },
  { key: "editorial_lock", label: "Editorial lock" },
  { key: "architect",      label: "Architect (per chapter)" },
  { key: "writer",         label: "Writer / prose (per chapter)" },
  { key: "critics",        label: "Critics (per chapter)" },
  { key: "editorial",      label: "Editorial eval (per chapter)" },
];

interface PipelineChatProps {
  project: ProjectInfo;
  runState: RunStateResponse | null;
  viewedArtifact: string | null;
  onInstructionsChanged: (brief: string) => void;
  onRunStateChanged: () => void;   // tell the parent to refresh run-state after a rerun/status change
}

export function PipelineChat({
  project, runState, viewedArtifact, onInstructionsChanged, onRunStateChanged,
}: PipelineChatProps) {
  const [messages, setMessages] = useState<PipelineChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestedBrief, setSuggestedBrief] = useState<string | null>(null);
  const [modelUsed, setModelUsed] = useState<string | null>(null);

  // Re-run controls.
  const [rerunPhaseKey, setRerunPhaseKey] = useState<string>("writer");
  const [rerunChapter, setRerunChapter] = useState<number | null>(null);
  const [rerunBusy, setRerunBusy] = useState(false);
  const [rerunMsg, setRerunMsg] = useState<string | null>(null);

  const endRef = useRef<HTMLDivElement | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const active = runState?.active;
  const currentPhase = runState?.current_phase;
  const currentUnit = runState?.units?.[runState.current_unit_index ?? 0] ?? null;

  const send = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;
    const userMsg: PipelineChatMessage = { role: "user", content: text };
    const next = [...messages, userMsg];
    setMessages(next);
    setInput("");
    setLoading(true);
    setError(null);
    setSuggestedBrief(null);
    setTimeout(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), 40);

    try {
      const data = await pipelineChat(project.root_path, next, {
        modelId: project.default_model ?? undefined,
        contextArtifact: viewedArtifact ?? undefined,
        contextChapter: currentUnit ?? undefined,
      });
      setModelUsed(data.model_used);
      setMessages(prev => [...prev, { role: "assistant", content: data.reply }]);
      if (data.suggested_instructions) setSuggestedBrief(data.suggested_instructions);
      setTimeout(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), 40);
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") {
        setError("Request cancelled.");
      } else {
        setError(err instanceof Error ? err.message : "The companion could not respond.");
      }
    } finally {
      setLoading(false);
    }
  }, [input, loading, messages, project.root_path, project.default_model, viewedArtifact, currentUnit]);

  function cancel() {
    abortRef.current?.abort();
  }

  async function applyBrief() {
    if (!suggestedBrief) return;
    try {
      await updateInstructions(project.root_path, suggestedBrief);
      onInstructionsChanged(suggestedBrief);
      setSuggestedBrief(null);
      setMessages(prev => [...prev, {
        role: "assistant",
        content: "Applied — the creative brief is updated. Every phase that runs next will honor the new direction. To revise material already written, use **Re-run Phase** below.",
      }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not apply the brief.");
    }
  }

  async function doRerun() {
    setRerunBusy(true);
    setRerunMsg(null);
    setError(null);
    try {
      const isUnit = UNIT_PHASES.includes(rerunPhaseKey);
      const ch = isUnit ? (rerunChapter ?? currentUnit ?? undefined) : undefined;
      await rerunPhase(project.root_path, rerunPhaseKey, ch);
      onRunStateChanged();
      setRerunMsg(`Re-targeted the run at ${rerunPhaseKey}${ch ? ` (chapter ${ch})` : ""}. Click Run Next Phase in the Run tab to regenerate it.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not re-run that phase.");
    } finally {
      setRerunBusy(false);
    }
  }

  return (
    <div className="flex min-h-0 flex-1 overflow-hidden">
      {/* ── Main chat column ────────────────────────────────────────────── */}
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        {/* Status strip */}
        <div className="shrink-0 border-b border-border bg-bg-panel px-4 py-2 text-xs text-text-muted">
          {active ? (
            <span>
              <span className="text-text-primary">Run:</span> {runState?.status}
              {" · "}
              phase <span className="text-text-primary">{runState?.current_phase_label ?? currentPhase}</span>
              {currentUnit != null && <> · chapter <span className="text-text-primary">{currentUnit}</span></>}
              {viewedArtifact && <> · viewing <span className="font-mono">{viewedArtifact}</span></>}
            </span>
          ) : (
            <span>No active run. Start one in the Run tab, then chat here to steer it.</span>
          )}
        </div>

        {/* Messages */}
        <div className="min-h-0 flex-1 overflow-y-auto px-4 py-4">
          {messages.length === 0 && (
            <div className="mx-auto max-w-2xl rounded border border-dashed border-border p-4 text-sm text-text-muted">
              <p className="mb-1 font-medium text-text-primary">Pipeline Companion</p>
              <p>Ask anything about the run, or request a change. Examples:</p>
              <ul className="mt-2 ml-4 list-disc space-y-1">
                <li>“Make chapter 3 quieter and more interior — revise the brief.”</li>
                <li>“What did the voice experiment conclude and why?”</li>
                <li>“The critics flagged chapter 2 dialogue — re-run the writer for it.”</li>
              </ul>
              <p className="mt-2">I can see the run state and a summary of which artifacts exist.</p>
            </div>
          )}

          <div className="mx-auto max-w-2xl space-y-3">
            {messages.map((m, i) => (
              <div key={i} className={m.role === "user" ? "flex justify-end" : "flex justify-start"}>
                <div
                  className={`max-w-[85%] rounded-lg px-3 py-2 text-sm ${
                    m.role === "user"
                      ? "bg-accent/20 text-text-primary"
                      : "bg-bg-panel text-text-primary"
                  }`}
                >
                  <ChatMarkdown content={m.content} />
                </div>
              </div>
            ))}

            {/* Suggested brief card */}
            {suggestedBrief && (
              <div className="rounded-lg border border-indigo-500/40 bg-indigo-500/10 p-3">
                <div className="mb-1 flex items-center gap-1.5 text-xs font-semibold text-indigo-300">
                  <Sparkles className="h-3.5 w-3.5" /> Suggested new creative brief
                </div>
                <p className="mb-2 whitespace-pre-wrap text-xs text-text-muted">{suggestedBrief}</p>
                <div className="flex gap-2">
                  <button
                    onClick={applyBrief}
                    className="inline-flex items-center gap-1 rounded bg-accent px-2.5 py-1 text-xs font-medium text-white hover:bg-accent/90"
                  >
                    <Check className="h-3.5 w-3.5" /> Apply to Brief
                  </button>
                  <button
                    onClick={() => setSuggestedBrief(null)}
                    className="inline-flex items-center gap-1 rounded border border-border px-2.5 py-1 text-xs text-text-muted hover:bg-bg-surface"
                  >
                    <X className="h-3.5 w-3.5" /> Dismiss
                  </button>
                </div>
              </div>
            )}

            {loading && (
              <div className="flex justify-start">
                <div className="rounded-lg bg-bg-panel px-3 py-2 text-sm text-text-muted">
                  <Loader2 className="inline h-3.5 w-3.5 animate-spin" /> Thinking…
                </div>
              </div>
            )}
            {error && (
              <div className="flex items-start gap-2 rounded border border-red-500/40 bg-red-500/10 p-2 text-xs text-red-400">
                <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" /> {error}
              </div>
            )}
            <div ref={endRef} />
          </div>
        </div>

        {/* Composer */}
        <div className="shrink-0 border-t border-border bg-bg-panel p-3">
          <div className="mx-auto flex max-w-2xl items-end gap-2">
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => {
                if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); void send(); }
              }}
              rows={2}
              placeholder="Ask the pipeline companion, or request a change…"
              className="min-w-0 flex-1 resize-none rounded border border-border bg-bg-surface px-2 py-1.5 text-sm text-text-base placeholder:text-text-muted focus:border-accent focus:outline-none"
            />
            {loading ? (
              <button onClick={cancel} className="inline-flex h-9 items-center gap-1 rounded border border-border px-3 text-sm text-text-muted hover:bg-bg-surface">
                Cancel
              </button>
            ) : (
              <button
                onClick={() => void send()}
                disabled={!input.trim()}
                className="inline-flex h-9 items-center gap-1 rounded bg-accent px-3 text-sm font-medium text-white hover:bg-accent/90 disabled:opacity-50"
              >
                <Send className="h-4 w-4" />
              </button>
            )}
          </div>
          {modelUsed && (
            <div className="mx-auto mt-1 max-w-2xl text-right text-[10px] text-text-muted">model: {modelUsed}</div>
          )}
        </div>
      </div>

      {/* ── Right: steering controls ────────────────────────────────────── */}
      <div className="hidden w-72 shrink-0 overflow-y-auto border-l border-border p-4 lg:block">
        <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-text-muted">Steering</div>
        <p className="mb-3 text-xs text-text-muted">
          Change the creative direction or regenerate material. The companion can propose these for you; apply them directly here too.
        </p>

        {/* Re-run phase */}
        <div className="mb-4 rounded border border-border bg-bg-panel p-3">
          <div className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-text-primary">
            <RotateCcw className="h-3.5 w-3.5 text-accent" /> Re-run a phase
          </div>
          <label className="mb-1 block text-[10px] uppercase tracking-wide text-text-muted">Phase</label>
          <select
            value={rerunPhaseKey}
            onChange={e => setRerunPhaseKey(e.target.value)}
            className="mb-2 w-full rounded border border-border bg-bg-surface px-2 py-1 text-xs text-text-base focus:border-accent focus:outline-none"
          >
            {RERUNNABLE_PHASES.map(p => (
              <option key={p.key} value={p.key}>{p.label}</option>
            ))}
          </select>
          {UNIT_PHASES.includes(rerunPhaseKey) && (
            <>
              <label className="mb-1 block text-[10px] uppercase tracking-wide text-text-muted">Chapter</label>
              <select
                value={rerunChapter ?? currentUnit ?? ""}
                onChange={e => setRerunChapter(e.target.value ? Number(e.target.value) : null)}
                className="mb-2 w-full rounded border border-border bg-bg-surface px-2 py-1 text-xs text-text-base focus:border-accent focus:outline-none"
              >
                {(runState?.units ?? []).map(u => (
                  <option key={u} value={u}>Chapter {u}</option>
                ))}
              </select>
            </>
          )}
          <button
            onClick={() => void doRerun()}
            disabled={rerunBusy || !active}
            className="inline-flex w-full items-center justify-center gap-1.5 rounded bg-accent px-3 py-1.5 text-xs font-medium text-white hover:bg-accent/90 disabled:opacity-50"
          >
            {rerunBusy ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RotateCcw className="h-3.5 w-3.5" />}
            Re-target run
          </button>
          {rerunMsg && <p className="mt-2 text-[11px] text-green-400">{rerunMsg}</p>}
        </div>

        {/* Current brief (read-only here; edit it in the Run tab) */}
        {active && runState?.instructions && (
          <div className="rounded border border-accent/30 bg-accent/5 p-3">
            <div className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-accent">Current creative brief</div>
            <p className="whitespace-pre-wrap text-xs text-text-muted">{runState.instructions}</p>
          </div>
        )}
      </div>
    </div>
  );
}
