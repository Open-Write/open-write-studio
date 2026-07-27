"""
test_pipeline_outputs.py — HTTP-level tests for the pipeline Output Library +
live-control + chat support routes (t-001 / t-002 / t-003).

Mounts ONLY the pipeline router on a minimal FastAPI app (same pattern as
test_pipeline_routes.py), then exercises:
  - GET  /outputs           structured catalog by category
  - GET  /output-file       read one artifact (incl. path-traversal rejection)
  - POST /update-instructions
  - POST /set-status
  - POST /rerun-phase
  - the SUGGESTED_BRIEF extractor for the chat route

Runs directly with plain Python (stdlib logic) or via pytest. Requires
fastapi + httpx (TestClient).
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routers import pipeline
from pipeline_fixtures import build_project


def _make_client():
    app = FastAPI()
    app.include_router(pipeline.router)
    return TestClient(app)


# ── Catalog + reader ──────────────────────────────────────────────────────────

def _run_outputs():
    failures = 0

    def check(name, cond, detail=""):
        nonlocal failures
        if cond:
            print(f"  PASS  {name}")
        else:
            failures += 1
            print(f"  FAIL  {name}: {detail}")

    with tempfile.TemporaryDirectory() as root:
        build_project(root)
        client = _make_client()

        # 1. catalog endpoint returns all six categories.
        r = client.get("/api/pipeline/outputs", params={"project_path": root})
        check("outputs status 200", r.status_code == 200, r.text)
        cat = r.json()
        keys = [c["key"] for c in cat["categories"]]
        check("catalog has 6 categories in order",
              keys == ["bible", "voice", "design", "prose", "reviews", "manifest"], keys)

        by = {c["key"]: c for c in cat["categories"]}
        # The fixture writes concept/outline/format-rules + locked voice spec.
        check("bible present >= 4", by["bible"]["exists_count"] >= 4, by["bible"])
        # Locked voice spec is the voice "locked" group entry.
        voice_paths = [e["path"] for e in by["voice"]["entries"]]
        check("voice lists locked spec", "bible/LOCKED_VOICE_SPEC.md" in voice_paths, voice_paths)
        # Fixture wrote 5 critics + editorial + adversarial + outline-lock.
        check("reviews present >= 4", by["reviews"]["exists_count"] >= 4, by["reviews"])
        # Fixture wrote one chapter + assembled novel.
        check("prose present >= 2", by["prose"]["exists_count"] >= 2, by["prose"])

        # 2. read a real artifact.
        r = client.get("/api/pipeline/output-file", params={
            "project_path": root, "path": "bible/01_concept.md"})
        check("output-file 200", r.status_code == 200, r.text)
        check("output-file exists", r.json().get("exists") is True, r.text)
        check("output-file has content", bool(r.json().get("content")), r.text)
        check("output-file kind markdown", r.json().get("kind") == "markdown", r.json().get("kind"))

        # 3. missing artifact -> exists False (not a crash).
        r = client.get("/api/pipeline/output-file", params={
            "project_path": root, "path": "voice_experiments/review.md"})
        check("output-file missing returns exists False",
              r.status_code == 200 and r.json().get("exists") is False, r.text)

        # 4. path traversal is rejected with 400.
        r = client.get("/api/pipeline/output-file", params={
            "project_path": root, "path": "../../etc/passwd"})
        check("output-file traversal rejected", r.status_code == 400, r.text)

    return failures


# ── Live control ──────────────────────────────────────────────────────────────

def _run_control():
    failures = 0

    def check(name, cond, detail=""):
        nonlocal failures
        if cond:
            print(f"  PASS  {name}")
        else:
            failures += 1
            print(f"  FAIL  {name}: {detail}")

    with tempfile.TemporaryDirectory() as root:
        build_project(root)
        client = _make_client()

        # Start a run so the control routes have a RunState to act on.
        # (Build the manifest first — units are populated from it, mirroring how
        # editorial_lock seeds the chapter list during a real run.)
        client.post("/api/pipeline/build-manifest", json={
            "project_path": root, "project_name": "Market Morning",
            "project_type": "novel", "word_floor": 200,
        })
        r = client.post("/api/pipeline/start-run", json={
            "project_path": root, "project_name": "Market Morning",
            "instructions": "original brief",
        })
        check("start-run 200", r.status_code == 200, r.text)
        check("units detected from outline", r.json().get("units") == [1], r.json().get("units"))

        # update-instructions
        r = client.post("/api/pipeline/update-instructions", json={
            "project_path": root, "instructions": "make it darker and sparer"})
        check("update-instructions 200", r.status_code == 200, r.text)
        check("brief updated", r.json().get("instructions") == "make it darker and sparer", r.text)

        # set-status -> paused (stop)
        r = client.post("/api/pipeline/set-status", json={
            "project_path": root, "status": "paused"})
        check("set-status paused 200", r.status_code == 200 and r.json().get("status") == "paused", r.text)

        # invalid status rejected
        r = client.post("/api/pipeline/set-status", json={
            "project_path": root, "status": "bogus"})
        check("set-status invalid rejected", r.status_code == 400, r.text)

        # rerun-phase -> writer for chapter 1
        r = client.post("/api/pipeline/rerun-phase", json={
            "project_path": root, "phase": "writer", "chapter": 1})
        check("rerun-phase 200", r.status_code == 200, r.text)
        body = r.json()
        check("rerun targets writer", body.get("current_phase") == "writer", body)
        check("rerun status running", body.get("status") == "running", body)

        # unknown phase rejected
        r = client.post("/api/pipeline/rerun-phase", json={
            "project_path": root, "phase": "nope"})
        check("rerun unknown phase rejected", r.status_code == 400, r.text)

        # run-state reflects the re-targeted cursor.
        r = client.get("/api/pipeline/run-state", params={"project_path": root})
        check("run-state current_phase writer",
              r.json().get("current_phase") == "writer", r.json().get("current_phase"))
        check("run-state instructions persisted",
              r.json().get("instructions") == "make it darker and sparer", r.json().get("instructions"))

    return failures


# ── Chat helper ───────────────────────────────────────────────────────────────

def _run_chat_helper():
    failures = 0

    def check(name, cond, detail=""):
        nonlocal failures
        if cond:
            print(f"  PASS  {name}")
        else:
            failures += 1
            print(f"  FAIL  {name}: {detail}")

    extract = pipeline._extract_suggested_brief

    clean, suggested = extract("Sure.\n\nSUGGESTED_BRIEF:\nWrite darker prose.\n:END\nDone.")
    check("extracts brief block", suggested == "Write darker prose.", suggested)
    check("strips block from reply", "SUGGESTED_BRIEF" not in clean and "Done." in clean, clean)

    clean, suggested = extract("No change needed here.")
    check("no block -> None", suggested is None, suggested)
    check("no block -> reply untouched", clean == "No change needed here.", clean)

    return failures


# ── Entry points ──────────────────────────────────────────────────────────────

def test_pipeline_outputs_catalog():
    assert _run_outputs() == 0


def test_pipeline_live_control():
    assert _run_control() == 0


def test_pipeline_chat_helper():
    assert _run_chat_helper() == 0


if __name__ == "__main__":
    total = 0
    print("== outputs ==")
    total += _run_outputs()
    print("== control ==")
    total += _run_control()
    print("== chat helper ==")
    total += _run_chat_helper()
    print(f"\n{'ALL PASS' if total == 0 else f'{total} FAILURE(S)'}")
    sys.exit(1 if total else 0)
