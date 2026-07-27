// PipelineOutputs.tsx -- the Open-Write pipeline Output Library (t-004)
// ====================================================================
// A browsable library of EVERYTHING the pipeline has produced, organized by
// category: Bible, Voice Experiment, Design Documents, Prose (manuscript),
// Reviews (critics + editorial + adversarial), and Manifest & State.
//
// Left pane: categories with their artifacts (present/total counts), grouped.
// Right pane: a reader that renders the selected artifact (markdown as prose,
// JSON pretty-printed for manifest/state). Selecting an artifact also reports
// it up to the parent so the Chat tab can send it as context.
//
// Read-only: this view never edits artifacts. The pipeline/gate remain the
// sole writers.

import { useState, useEffect, useCallback } from "react";
import {
  BookOpen, Mic, FileText, ScrollText, ClipboardCheck, Database,
  RefreshCw, Loader2, FileQuestion, ArrowLeft,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import type { ProjectInfo } from "../types/project";
import {
  fetchCatalog, fetchArtifact,
  type OutputCatalog, type CatalogCategory, type CatalogEntry, type ArtifactContent,
} from "../utils/pipelineApi";

// Category icon + order. Keys match backend CATEGORY_ORDER.
const CATEGORY_META: Record<string, { icon: typeof BookOpen; hint: string }> = {
  bible:    { icon: BookOpen,        hint: "Concept, outline, and format rules" },
  voice:    { icon: Mic,             hint: "Voices tested, the review, and the locked spec" },
  design:   { icon: FileText,        hint: "Outline structure + per-chapter architect plans" },
  prose:    { icon: ScrollText,      hint: "Chapter manuscripts and the assembled novel" },
  reviews:  { icon: ClipboardCheck,  hint: "Critic, editorial, and adversarial coverage" },
  manifest: { icon: Database,        hint: "Completion manifest and run state" },
};

interface PipelineOutputsProps {
  project: ProjectInfo;
  viewedArtifact: string | null;
  onViewedArtifactChange: (path: string | null) => void;
}

export function PipelineOutputs({ project, viewedArtifact, onViewedArtifactChange }: PipelineOutputsProps) {
  const [catalog, setCatalog] = useState<OutputCatalog | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Which categories are expanded in the left list. Default: expand the first
  // category that has any present artifact so the writer immediately sees work.
  const [expanded, setExpanded] = useState<Set<string>>(new Set());

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const cat = await fetchCatalog(project.root_path);
      setCatalog(cat);
      // Auto-expand the first category with artifacts, once.
      setExpanded(prev => {
        if (prev.size > 0) return prev;
        const firstWithWork = cat.categories.find(c => c.exists_count > 0);
        return firstWithWork ? new Set([firstWithWork.key]) : new Set(["bible"]);
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load outputs.");
    } finally {
      setLoading(false);
    }
  }, [project.root_path]);

  useEffect(() => { void refresh(); }, [refresh]);

  function toggle(key: string) {
    setExpanded(prev => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key); else next.add(key);
      return next;
    });
  }

  return (
    <div className="flex min-h-0 flex-1 overflow-hidden">
      {/* ── Left: category browser ──────────────────────────────────────── */}
      <div className="flex w-80 shrink-0 flex-col border-r border-border">
        <div className="flex shrink-0 items-center justify-between border-b border-border px-3 py-2">
          <span className="text-xs font-semibold uppercase tracking-wide text-text-muted">Output Library</span>
          <button
            onClick={() => void refresh()}
            disabled={loading}
            className="rounded p-1 text-text-muted hover:bg-bg-surface hover:text-text-primary disabled:opacity-50"
            title="Refresh the catalog"
          >
            {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RefreshCw className="h-3.5 w-3.5" />}
          </button>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-2 py-2">
          {error && (
            <div className="mb-2 rounded border border-red-500/40 bg-red-500/10 p-2 text-xs text-red-400">{error}</div>
          )}
          {!catalog && loading && (
            <div className="flex items-center gap-2 p-3 text-xs text-text-muted">
              <Loader2 className="h-3.5 w-3.5 animate-spin" /> Loading outputs…
            </div>
          )}
          {catalog?.categories.map(cat => (
            <CategoryBlock
              key={cat.key}
              category={cat}
              expanded={expanded.has(cat.key)}
              onToggle={() => toggle(cat.key)}
              selectedPath={viewedArtifact}
              onSelect={(p) => onViewedArtifactChange(p)}
            />
          ))}
        </div>
      </div>

      {/* ── Right: reader ───────────────────────────────────────────────── */}
      <ArtifactReader
        project={project}
        path={viewedArtifact}
        onBack={() => onViewedArtifactChange(null)}
      />
    </div>
  );
}

// ── Category block (collapsible list of entries) ─────────────────────────────

function CategoryBlock({
  category, expanded, onToggle, selectedPath, onSelect,
}: {
  category: CatalogCategory;
  expanded: boolean;
  onToggle: () => void;
  selectedPath: string | null;
  onSelect: (path: string) => void;
}) {
  const meta = CATEGORY_META[category.key] ?? { icon: FileText, hint: "" };
  const Icon = meta.icon;
  return (
    <div className="mb-1">
      <button
        onClick={onToggle}
        className="flex w-full items-center gap-2 rounded px-2 py-1.5 text-left hover:bg-bg-surface"
        title={meta.hint}
      >
        <Icon className="h-4 w-4 shrink-0 text-accent" />
        <span className="min-w-0 flex-1">
          <span className="block truncate text-sm font-medium text-text-primary">{category.label}</span>
          <span className="block truncate text-xs text-text-muted">{meta.hint}</span>
        </span>
        <span className="shrink-0 rounded bg-bg-panel px-1.5 py-0.5 font-mono text-[10px] text-text-muted">
          {category.exists_count}/{category.count}
        </span>
      </button>
      {expanded && (
        <ul className="mb-1 ml-2 border-l border-border pl-2">
          {/* Group entries by their `group` tag so e.g. Voice shows candidates
              together and Reviews groups critics vs editorial vs structural. */}
          {groupedEntries(category.entries).map(({ label, entries }) => (
            <li key={label}>
              {label && (
                <div className="mt-1.5 px-1 text-[10px] font-semibold uppercase tracking-wide text-text-muted">
                  {label}
                </div>
              )}
              {entries.map(e => (
                <EntryRow
                  key={e.path}
                  entry={e}
                  selected={selectedPath === e.path}
                  onSelect={() => onSelect(e.path)}
                />
              ))}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// Group entries by their `group` field, preserving order of first appearance.
function groupedEntries(entries: CatalogEntry[]): { label: string; entries: CatalogEntry[] }[] {
  const order: string[] = [];
  const map = new Map<string, CatalogEntry[]>();
  for (const e of entries) {
    const g = e.group ?? "";
    if (!map.has(g)) { map.set(g, []); order.push(g); }
    map.get(g)!.push(e);
  }
  // Humanize group names for display.
  const humanize = (g: string) => g
    ? g.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())
    : "";
  return order.map(g => ({ label: humanize(g), entries: map.get(g)! }));
}

function EntryRow({
  entry, selected, onSelect,
}: {
  entry: CatalogEntry;
  selected: boolean;
  onSelect: () => void;
}) {
  const missing = !entry.exists;
  return (
    <button
      onClick={onSelect}
      disabled={missing}
      className={`mt-0.5 flex w-full items-center gap-2 rounded px-2 py-1 text-left text-xs transition-colors disabled:cursor-not-allowed disabled:opacity-40 ${
        selected ? "bg-accent/15 text-text-primary" : "text-text-muted hover:bg-bg-surface hover:text-text-primary"
      }`}
      title={entry.path}
    >
      <span className="min-w-0 flex-1 truncate">
        {entry.label ?? entry.path}
        {entry.critic_type && (
          <span className="ml-1 rounded bg-bg-panel px-1 py-0.5 font-mono text-[9px] uppercase text-text-muted">
            {entry.critic_type}
          </span>
        )}
      </span>
      {entry.words != null && entry.exists && (
        <span className="shrink-0 font-mono text-[10px] text-text-muted">{entry.words}w</span>
      )}
      {missing && <span className="shrink-0 text-[10px] text-text-muted">—</span>}
    </button>
  );
}

// ── Reader pane ──────────────────────────────────────────────────────────────

function ArtifactReader({
  project, path, onBack,
}: {
  project: ProjectInfo;
  path: string | null;
  onBack: () => void;
}) {
  const [artifact, setArtifact] = useState<ArtifactContent | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!path) { setArtifact(null); setError(null); return; }
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchArtifact(project.root_path, path)
      .then(a => { if (!cancelled) setArtifact(a); })
      .catch(err => { if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load."); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [project.root_path, path]);

  if (!path) {
    return (
      <div className="flex flex-1 items-center justify-center p-8 text-center text-sm text-text-muted">
        <div>
          <FileQuestion className="mx-auto mb-2 h-8 w-8 opacity-40" />
          Select an artifact on the left to read it here.
          <br />
          Every file the pipeline has written to disk is listed by category.
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
      <div className="flex shrink-0 items-center justify-between gap-2 border-b border-border bg-bg-panel px-4 py-2">
        <div className="flex min-w-0 items-center gap-2">
          <button onClick={onBack} className="rounded p-1 text-text-muted hover:bg-bg-surface hover:text-text-primary" title="Close reader">
            <ArrowLeft className="h-4 w-4" />
          </button>
          <span className="truncate font-mono text-xs text-text-muted" title={path}>{path}</span>
        </div>
        {artifact?.exists && artifact.words != null && (
          <span className="shrink-0 font-mono text-xs text-text-muted">{artifact.words} words</span>
        )}
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        {loading && (
          <div className="flex items-center gap-2 p-6 text-sm text-text-muted">
            <Loader2 className="h-4 w-4 animate-spin" /> Loading…
          </div>
        )}
        {error && (
          <div className="m-4 rounded border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-400">{error}</div>
        )}
        {artifact && !artifact.exists && (
          <div className="p-6 text-sm text-text-muted">
            This artifact hasn't been produced yet. It will appear here once the
            matching pipeline phase runs.
          </div>
        )}
        {artifact?.exists && artifact.kind === "json" && (
          <pre className="overflow-x-auto p-4 font-mono text-xs leading-relaxed text-text-primary">
            {prettyJson(artifact.content)}
          </pre>
        )}
        {artifact?.exists && artifact.kind === "markdown" && (
          // Render prose artifacts as readable markdown. react-markdown is
          // already a dependency (ChatMarkdown); here we use the default
          // renderer with a serif, comfortable line length for long reading.
          <div className="mx-auto max-w-3xl px-6 py-6 font-serif text-[15px] leading-relaxed text-text-primary">
            <ReactMarkdown
              components={{
                h1: ({ children }) => <h1 className="mb-3 mt-2 font-sans text-2xl font-bold">{children}</h1>,
                h2: ({ children }) => <h2 className="mb-2 mt-5 font-sans text-xl font-semibold">{children}</h2>,
                h3: ({ children }) => <h3 className="mb-2 mt-4 font-sans text-lg font-semibold">{children}</h3>,
                p: ({ children }) => <p className="mb-3">{children}</p>,
                ul: ({ children }) => <ul className="mb-3 ml-6 list-disc">{children}</ul>,
                ol: ({ children }) => <ol className="mb-3 ml-6 list-decimal">{children}</ol>,
                li: ({ children }) => <li className="mb-1">{children}</li>,
                blockquote: ({ children }) => (
                  <blockquote className="my-3 border-l-2 border-accent/50 pl-3 italic text-text-muted">{children}</blockquote>
                ),
                code: ({ children }) => <code className="rounded bg-bg-panel px-1 py-0.5 font-mono text-xs">{children}</code>,
                hr: () => <hr className="my-4 border-border" />,
              }}
            >
              {artifact.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}

function prettyJson(raw: string): string {
  try { return JSON.stringify(JSON.parse(raw), null, 2); }
  catch { return raw; }
}
