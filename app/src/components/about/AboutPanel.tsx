// components/about/AboutPanel.tsx -- About modal
// ============================================================
// Single modal accessed from the Settings screen (or an About menu entry)
// that surfaces:
//   - App name, version, license
//   - Manual "Check for updates" trigger that re-runs the launch check
//
// Auto-update is disabled in the Open-Write build (no release feed or
// signing key is configured yet), so "Check for updates" simply reports
// "up-to-date". Donation and sponsor UI from the upstream project has been
// removed. The prop interface is kept identical so callers do not need to
// change; the donation-related props are accepted but unused.

import type { UpdateStatus } from "../../hooks/useAppUpdate";


export interface AboutPanelProps {
  version:        string;
  hasDonated:     boolean;
  updateStatus:   UpdateStatus;
  openLink:       (url: string) => void;
  onMarkDonated:  () => void;
  onUnmarkDonated: () => void;
  onCheckUpdates: () => void;
  onClose:        () => void;
}


export function AboutPanel({
  version, updateStatus, onCheckUpdates, onClose,
}: AboutPanelProps) {

  const checking = updateStatus === "checking";

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md max-h-[85vh] overflow-y-auto rounded border border-indigo-700/60 bg-bg-panel shadow-xl"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border px-5 py-3">
          <h2 className="text-base font-semibold text-indigo-300">About</h2>
          <button onClick={onClose} className="text-faint hover:text-text-muted">✕</button>
        </div>

        {/* Identity block: app name + version */}
        <div className="border-b border-border px-5 py-4 text-center">
          <p className="text-lg font-semibold text-text-primary">Open-Write</p>
          <p className="text-xs text-text-muted">Version {version}</p>
        </div>

        {/* Updates */}
        <div className="border-b border-border px-5 py-4">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-faint">
            Updates
          </p>
          <button
            onClick={onCheckUpdates}
            disabled={checking}
            className="rounded border border-border bg-bg-primary px-3 py-1 text-xs text-text-primary hover:border-indigo-500 hover:text-indigo-200 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {checking ? "Checking..." : "Check for updates"}
          </button>
          <p className="mt-1.5 text-[11px] text-faint">
            Automatic updates are not configured for this build.
          </p>
        </div>

        {/* License + tech */}
        <div className="px-5 py-4 text-xs">
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-faint">
            Project
          </p>
          <p className="text-text-primary">Apache License 2.0</p>
          <p className="mt-3 text-[11px] text-faint">
            Built with Tauri, React, CodeMirror, FastAPI, and OpenRouter.
          </p>
        </div>
      </div>
    </div>
  );
}
