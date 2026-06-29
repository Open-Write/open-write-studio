"""
harness/verifier.py — certify a task done on disk.

Cross-domain implementation of Open-Write's verify-not-trust discipline: the
system that does the work never grades whether it's done. Adapted from
``C:\\The_Architect\\runtime\\verifier.py``.

Kinds:
    files    — every file in files_expected exists under the project
    tool     — run a tool; the `gate` token must appear in its output
    manifest — the project completion gate passes (reuses the Open-Write gate
               in-process for the whole-project verdict, or reads a manifest
               entry when manifest_key is set)
    tests    — run the project test command (from metadata); exit 0

All path checks are relative to the project workspace.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .models import VerifierKind, VerifierSpec


@dataclass(frozen=True)
class VerificationResult:
    passed: bool
    kind: str
    detail: str
    evidence: list[str]


class Verifier:
    """Certifies task completion on disk. Never raises on failure — returns it."""

    def verify(self, spec: Optional[VerifierSpec], workspace: str,
               task_metadata: Optional[dict] = None,
               effective_spec: Optional[VerifierSpec] = None) -> VerificationResult:
        """
        Verify a task. ``effective_spec`` (the task's spec or the domain default)
        takes precedence over ``spec``; both fall back to a files check using
        ``task_metadata['files_expected']``.
        """
        ws = Path(workspace)
        metadata = task_metadata or {}
        s = effective_spec or spec

        if s is None:
            return self._verify_files(ws, metadata.get("files_expected", []), fallback=True)

        if s.kind == VerifierKind.FILES:
            return self._verify_files(ws, s.files_expected)
        if s.kind == VerifierKind.MANIFEST:
            return self._verify_manifest(ws, s.manifest_key, s.gate)
        if s.kind == VerifierKind.TOOL:
            return self._verify_tool(ws, s.tool, s.gate)
        if s.kind == VerifierKind.TESTS:
            return self._verify_tests(ws, metadata.get("test_cmd"))
        return VerificationResult(False, "unknown", f"Unknown verifier kind: {s.kind}", [])

    # ------------------------------------------------------------------
    def _verify_files(self, ws: Path, files_expected: list[str],
                      fallback: bool = False) -> VerificationResult:
        if not files_expected:
            label = "files (fallback, none specified)"
            return VerificationResult(False, "files", f"{label}: no files declared", [])
        missing, evidence = [], []
        for rel in files_expected:
            p = ws / rel
            ok = p.exists()
            evidence.append(f"{'OK' if ok else 'MISSING'}  {rel}")
            if not ok:
                missing.append(rel)
        label = "files (fallback)" if fallback else "files"
        detail = (f"{label}: {len(files_expected) - len(missing)}/{len(files_expected)} present"
                  + (f"; missing: {missing}" if missing else ""))
        return VerificationResult(not missing, "files", detail, evidence)

    def _verify_manifest(self, ws: Path, manifest_key: Optional[str], gate: str) -> VerificationResult:
        # No key: run the whole-project Open-Write gate in-process. This reuses
        # the deterministic verifier that the completion gate already trusts.
        if not manifest_key:
            try:
                from app.pipeline import finalize as finalize_mod
                result = finalize_mod.run_manifest_verify(ws)
                passed = result.get("verdict", "").upper() == "PASS"
                return VerificationResult(
                    passed, "manifest",
                    f"gate verdict={result.get('verdict')} "
                    f"({result.get('items_passed', 0)}/{result.get('items_checked', 0)})",
                    [f"items_failed={result.get('items_failed', 0)}"],
                )
            except Exception as exc:  # noqa: BLE001 — verifier never raises
                return VerificationResult(False, "manifest", f"gate error: {exc}", [])

        mf = ws / "state" / "completion_manifest.json"
        if not mf.exists():
            return VerificationResult(False, "manifest", f"no manifest at {mf}", [])
        try:
            data = json.loads(mf.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            return VerificationResult(False, "manifest", f"manifest unreadable: {exc}", [])
        node: object = data
        for part in manifest_key.split("."):
            node = node.get(part) if isinstance(node, dict) else None
        val = str(node).lower() if node is not None else ""
        passed = val == gate.lower()
        return VerificationResult(passed, "manifest",
                                  f"manifest[{manifest_key}]={val!r} (need {gate!r})", [str(mf)])

    def _verify_tool(self, ws: Path, tool: Optional[str], gate: str) -> VerificationResult:
        if not tool:
            return VerificationResult(False, "tool", "tool verifier declared but no tool path given", [])
        # Bounds-check: the tool path must resolve inside the workspace. `tool`
        # originates from VerifierSpec (LLM/planner output), so a traversal like
        # tools/../../<x>.py must not escape and execute. Same realpath guard the
        # rest of the pipeline applies.
        tool_path = (ws / tool).resolve()
        base = ws.resolve()
        if not (str(tool_path) == str(base) or str(tool_path).startswith(str(base) + os.sep)) or not tool_path.is_file():
            return VerificationResult(
                False, "tool",
                f"tool path escapes project or is missing: {tool}", [],
            )
        try:
            proc = subprocess.run(
                ["python", str(tool_path)], cwd=str(ws), capture_output=True,
                text=True, timeout=600, encoding="utf-8", errors="replace",
            )
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            return VerificationResult(False, "tool", f"tool not runnable: {exc}", [])
        out = proc.stdout or ""
        hit = bool(re.search(rf"\b{re.escape(gate)}\b", out, re.IGNORECASE))
        return VerificationResult(
            hit, "tool",
            f"tool {tool} exit={proc.returncode}; gate '{gate}' {'found' if hit else 'NOT found'}",
            [f"rc={proc.returncode}", out[:500]],
        )

    def _verify_tests(self, ws: Path, test_cmd: Optional[str]) -> VerificationResult:
        # test_cmd must come from trusted config, not LLM output. Run without a
        # shell (shlex.split) to avoid injection from a hostile string.
        if not test_cmd:
            return VerificationResult(False, "tests", "tests verifier requires metadata.test_cmd", [])
        try:
            argv = shlex.split(test_cmd)
        except ValueError as exc:
            return VerificationResult(False, "tests", f"could not parse test_cmd: {exc}", [])
        try:
            proc = subprocess.run(
                argv, cwd=str(ws), shell=False, capture_output=True, text=True,
                timeout=900, encoding="utf-8", errors="replace",
            )
        except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
            return VerificationResult(False, "tests", f"test command failed to run: {exc}", [])
        passed = proc.returncode == 0
        return VerificationResult(
            passed, "tests", f"test_cmd exit={proc.returncode}",
            [(proc.stdout or "")[:500], (proc.stderr or "")[:500]],
        )
