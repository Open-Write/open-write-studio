"""
test_pipeline_routes.py — HTTP-level smoke test for the pipeline router.

Mounts the pipeline router on a minimal FastAPI app and drives the full
gate over HTTP: build-manifest -> verify -> finalize. Uses the shared
pipeline_fixtures builder so the fixture stays in sync with the logic test.

Requires fastapi + httpx (TestClient). Runs directly with Python or via pytest.
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


def _run_all():
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

        # 1. build-manifest
        r = client.post("/api/pipeline/build-manifest", json={
            "project_path": root, "project_name": "Market Morning",
            "project_type": "novel", "word_floor": 200,
        })
        check("build-manifest status 200", r.status_code == 200, r.text)
        bm = r.json()
        check("build-manifest detected 1 chapter", bm.get("chapters_detected") == 1, bm)

        # 2. read manifest back
        r = client.get("/api/pipeline/manifest", params={"project_path": root})
        check("manifest GET 200", r.status_code == 200, r.text)
        check("manifest has sections", isinstance(r.json().get("sections"), list))

        # 3. verify -> PASS
        r = client.post("/api/pipeline/verify", json={"project_path": root})
        check("verify status 200", r.status_code == 200, r.text)
        v = r.json()
        check("verify verdict PASS", v.get("verdict") == "PASS", v)

        # 4. finalize -> COMPLETE, writes COMPLETION_PASS.json
        r = client.post("/api/pipeline/finalize", json={"project_path": root})
        check("finalize status 200", r.status_code == 200, r.text)
        f = r.json()
        check("finalize verdict COMPLETE", f.get("finalize_verdict") == "COMPLETE", f)
        check("COMPLETION_PASS.json written",
              os.path.isfile(os.path.join(root, "state", "COMPLETION_PASS.json")))
        check("COMPLETION_INCOMPLETE.json absent",
              not os.path.isfile(os.path.join(root, "state", "COMPLETION_INCOMPLETE.json")))

        # 5. word-count whole project
        r = client.post("/api/pipeline/word-count", json={"project_path": root})
        check("word-count status 200", r.status_code == 200, r.text)
        check("word-count total > 0", r.json().get("total_words", 0) > 0, r.text)

    print(f"\n{1 - failures}/{1} group(s) ok" if False else "")
    return failures


# pytest entrypoints ----------------------------------------------------------
def test_pipeline_routes_end_to_end():
    with tempfile.TemporaryDirectory() as root:
        build_project(root)
        client = _make_client()

        r = client.post("/api/pipeline/build-manifest", json={
            "project_path": root, "project_name": "Market Morning",
            "project_type": "novel", "word_floor": 200,
        })
        assert r.status_code == 200, r.text
        assert r.json()["chapters_detected"] == 1

        r = client.post("/api/pipeline/verify", json={"project_path": root})
        assert r.status_code == 200, r.text
        assert r.json()["verdict"] == "PASS", r.text

        r = client.post("/api/pipeline/finalize", json={"project_path": root})
        assert r.status_code == 200, r.text
        assert r.json()["finalize_verdict"] == "COMPLETE", r.text
        assert os.path.isfile(os.path.join(root, "state", "COMPLETION_PASS.json"))


if __name__ == "__main__":
    sys.exit(1 if _run_all() else 0)
