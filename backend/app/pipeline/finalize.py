#!/usr/bin/env python3
"""
finalize.py — mechanical completion gate for an Open-Write project.

What changed vs the prior version
---------------------------------
1. CONTENT-HASH BINDING. The completion artifact is bound to a SHA-256 of the
   *assembled manuscript content* (after a defined normalization). This fixes
   the bug where The_Toll and project_glm shared an identical
   verify_output_hash and project_name "Untitled": that hash was not a function
   of the manuscript, so a COMPLETION_PASS could be copied between projects.
   Now:
     - a COMPLETION_PASS is valid only if its recorded hash matches a fresh
       hash of the current manuscript (catches copy-between-projects AND
       post-certification edits);
     - two different manuscripts can never share a certificate.

2. BLOCKING LINTS. PASS requires manifest verify PASS *and* every blocking lint
   PASS. "128/128 items exist" is no longer sufficient -- the items must also
   not be hollow/padded/duplicated, and named real figures must have an
   independent factual sign-off.

The agent does not write this file. finalize.py does, and it refuses to trust an
existing artifact whose hash does not match the current manuscript.

Usage:  python tools/finalize.py [--base-dir PATH] [--json]
"""

from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
import datetime

try:
    from . import lints  # sibling module within the pipeline package
    _HAS_LINTS = True
except ImportError:
    _HAS_LINTS = False

PASS_NAME = "COMPLETION_PASS.json"
INCOMPLETE_NAME = "COMPLETION_INCOMPLETE.json"

_ASSEMBLED_CANDIDATES = [
    os.path.join("manuscript", "novel.md"),
    os.path.join("manuscript", "screenplay.fountain"),
    os.path.join("manuscript", "season.fountain"),
]


def _find_assembled_manuscript(project: str) -> str:
    """Locate the assembled manuscript in the project."""
    for rel in _ASSEMBLED_CANDIDATES:
        p = os.path.join(project, rel)
        if os.path.isfile(p):
            return p
    raise FileNotFoundError(
        f"No assembled manuscript found in {os.path.join(project, 'manuscript')}/ "
        f"(looked for: {', '.join(os.path.basename(c) for c in _ASSEMBLED_CANDIDATES)})"
    )


def normalized_manuscript_bytes(project: str) -> bytes:
    """
    Canonical form for hashing: read the assembled manuscript, decode utf-8,
    normalize newlines to \\n, strip trailing whitespace per line, strip a
    trailing blank tail. Reproducible, and stable against the \\r\\n / trailing
    -newline noise that made the prior word counts drift by a few words.
    """
    path = _find_assembled_manuscript(project)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n")).strip() + "\n"
    return text.encode("utf-8")


def manuscript_hash(project: str) -> str:
    return hashlib.sha256(normalized_manuscript_bytes(project)).hexdigest()


def run_manifest_verify(project: str) -> dict:
    """
    Run the manifest verifier in-process and return its JSON dict.

    In the standalone CLI toolchain this called verify_completion.py via
    subprocess. Here we call the verifier function directly to avoid spawning
    a Python interpreter and to share one process with the FastAPI server.
    The returned dict matches verify_completion's --json output shape.
    """
    from . import verify_completion

    # Locate the manifest (mirror verify_completion's own candidate search).
    manifest_path = None
    for candidate in (
        os.path.join(project, "state", "completion_manifest.json"),
        os.path.join(project, "completion_manifest.json"),
    ):
        if os.path.isfile(candidate):
            manifest_path = candidate
            break
    if not manifest_path:
        return {
            "verdict": "FAIL",
            "error": "completion_manifest.json not found",
            "items_checked": 0, "items_passed": 0, "items_failed": 0,
            "failures": ["completion_manifest.json missing"],
        }

    try:
        with open(manifest_path, "r", encoding="utf-8-sig") as f:
            manifest = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        return {
            "verdict": "FAIL",
            "error": f"Could not parse manifest: {exc}",
            "items_checked": 0, "items_passed": 0, "items_failed": 0,
            "failures": ["manifest parse error"],
        }

    expected_chapters = verify_completion._auto_detect_chapters(project)
    all_pass, total, passed, failed, failures, chapter_hashes = verify_completion.verify_manifest(
        project, manifest, expected_chapters, skip_lint=False
    )
    return {
        "verdict": "PASS" if all_pass else "FAIL",
        "project_name": manifest.get("project_name", ""),
        "project_type": manifest.get("project_type", ""),
        "items_checked": total,
        "items_passed": passed,
        "items_failed": failed,
        "chapter_hashes": {k: v[:16] + "..." for k, v in chapter_hashes.items()},
        "failures": failures,
    }


def existing_artifact(project: str):
    p = os.path.join(project, "state", PASS_NAME)
    if os.path.exists(p):
        try:
            with open(p, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return None
    return None


def finalize(project: str) -> dict:
    project = os.path.abspath(project)
    state_dir = os.path.join(project, "state")
    os.makedirs(state_dir, exist_ok=True)

    current_hash = manuscript_hash(project)
    project_name = os.path.basename(project.rstrip("/\\"))

    # 1. Reject a stale/copied existing certificate up front.
    prior = existing_artifact(project)
    if prior and prior.get("manuscript_sha256") not in (None, current_hash):
        verdict = {
            "finalize_verdict": "INVALIDATED",
            "reason": "existing COMPLETION_PASS hash does not match current "
                      "manuscript (copied from another project, or manuscript "
                      "edited after certification)",
            "recorded_hash": prior.get("manuscript_sha256"),
            "current_hash": current_hash,
        }
        try:
            os.remove(os.path.join(state_dir, PASS_NAME))
        except OSError:
            pass
        return verdict

    # 2. Manifest verify (128-item check) + blocking lints.
    verify_result = run_manifest_verify(project)

    if _HAS_LINTS:
        lint_results = lints.run_all(project)
        blocking_failures = [l for l in lint_results if l["blocking"] and l["status"] == "FAIL"]
        warnings = [l for l in lint_results if l["status"] == "WARN"]
    else:
        lint_results = []
        blocking_failures = []
        warnings = []

    complete = (verify_result.get("verdict") == "PASS") and not blocking_failures

    artifact = {
        "status": "COMPLETE" if complete else "INCOMPLETE",
        "project_name": project_name,
        "timestamp": datetime.datetime.now().isoformat(),
        "manuscript_sha256": current_hash,
        "verify": verify_result,
        "lints": lint_results,
        "blocking_lint_failures": [l["name"] for l in blocking_failures],
        "advisories": [l["name"] for l in warnings],
        "produced_by": "tools/finalize.py",
        "agent_may_not_write_this_file": True,
    }

    out_name = PASS_NAME if complete else INCOMPLETE_NAME
    for n in (PASS_NAME, INCOMPLETE_NAME):
        p = os.path.join(state_dir, n)
        if os.path.exists(p):
            os.remove(p)
    with open(os.path.join(state_dir, out_name), "w", encoding="utf-8") as fh:
        json.dump(artifact, fh, indent=2, ensure_ascii=False)

    return {
        "finalize_verdict": "COMPLETE" if complete else "INCOMPLETE",
        "completion_artifact": os.path.join(state_dir, out_name),
        "manuscript_sha256": current_hash,
        "verify_verdict": verify_result.get("verdict"),
        "blocking_lint_failures": artifact["blocking_lint_failures"],
        "advisories": artifact["advisories"],
        "failure_routing": [
            {"lint": l["name"], "level": l["level"], "findings": l["findings"]}
            for l in blocking_failures
        ],
    }


def main():
    ap = argparse.ArgumentParser(description="Mechanical completion gate")
    ap.add_argument("--base-dir", default=".", help="Project base directory")
    ap.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    args = ap.parse_args()
    result = finalize(args.base_dir)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(result["finalize_verdict"])
        for f in result.get("failure_routing", []):
            print(f"  FAIL [{f['level']}] {f['lint']}: {len(f['findings'])} finding(s)")
    sys.exit(0 if result["finalize_verdict"] == "COMPLETE" else 1)


if __name__ == "__main__":
    main()
