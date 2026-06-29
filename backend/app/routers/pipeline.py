# routers/pipeline.py -- Open-Write completion-gate endpoints
# =================================================================
# Exposes the deterministic Open-Write toolchain (ported into app.pipeline)
# as HTTP routes so the frontend can drive the same gate that the agentic
# IDE pipeline uses. The pipeline package is the SOLE authority on whether
# an Open-Write project is complete; these routes only call it.
#
# Endpoints
#   POST /api/pipeline/word-count     count words in a file or whole project
#   POST /api/pipeline/build-manifest generate completion_manifest.json from the locked outline
#   GET  /api/pipeline/manifest       read the existing manifest
#   POST /api/pipeline/verify         verify the manifest against disk (PASS/FAIL)
#   POST /api/pipeline/lints          run the 6 finalize blocking/advisory lints
#   POST /api/pipeline/lint-suite     run the deterministic per-chapter lint suite
#   POST /api/pipeline/finalize       run the full gate; writes the bound COMPLETION_PASS certificate
#
# Path safety: project_path must resolve to an existing directory. The
# pipeline tools additionally bounds-check every internal path against the
# project base (see verify_completion._resolve), so a manifest cannot reach
# outside the project folder.

from __future__ import annotations

import json
import os

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.pipeline import word_count, build_manifest, verify_completion, finalize, lints, lint_suite, critics
from app.pipeline import orchestrator
from app.settings_store import get_default_model


router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _require_project(project_path: str) -> str:
    """Resolve and validate that project_path is an existing directory."""
    resolved = os.path.realpath(project_path)
    if not resolved or not os.path.isdir(resolved):
        raise HTTPException(status_code=404, detail=f"Project folder not found: {project_path}")
    return resolved


def _locate_manifest(project: str) -> str | None:
    """Find completion_manifest.json in the conventional locations."""
    for candidate in (
        os.path.join(project, "state", "completion_manifest.json"),
        os.path.join(project, "completion_manifest.json"),
    ):
        if os.path.isfile(candidate):
            return candidate
    return None


# ── Request models ────────────────────────────────────────────────────────────

class WordCountRequest(BaseModel):
    project_path: str
    file: str | None = None      # relative path within the project (optional)
    floor: int | None = None     # flag items below this floor


class BuildManifestRequest(BaseModel):
    project_path: str
    outline: str | None = None          # relative path to outline (auto-detected if omitted)
    project_name: str = "Untitled"
    project_type: str = "novel"
    word_floor: int = 800


class VerifyRequest(BaseModel):
    project_path: str
    expected_chapters: int | None = None
    skip_lint: bool = False


class LintSuiteRequest(BaseModel):
    project_path: str
    chapter: str | None = None          # relative path to a single chapter file
    assembly: str | None = None         # relative path to the assembly file
    full: bool = True                   # run the whole-project suite (default)


class ProjectPathRequest(BaseModel):
    project_path: str


class RunCriticRequest(BaseModel):
    project_path: str
    chapter: str                    # relative path to the chapter file (e.g. manuscript/chapters/001_market.md)
    critic_type: str                # show | voice | palette | continuity | naturalism | editorial
    model_id: str | None = None     # falls back to the global default model
    context: str = ""               # optional attached context (summaries, ledger, profiles)


class RunAllCriticsRequest(BaseModel):
    project_path: str
    chapter: str
    model_id: str | None = None
    context: str = ""


# ── Orchestrator (Phase P) request models ─────────────────────────────────────

class StartRunRequest(BaseModel):
    project_path: str
    project_name: str = ""
    word_floor: int = 800
    instructions: str = ""    # Custom creative brief for the pipeline


class AdvancePhaseRequest(BaseModel):
    project_path: str
    model_id: str | None = None     # falls back to the global default model
    instructions: str = ""          # Custom instructions appended to each phase's prompt


# ── Word count ────────────────────────────────────────────────────────────────

@router.post("/word-count")
async def word_count_route(req: WordCountRequest):
    """Count words in a single file (relative path) or the whole project."""
    project = _require_project(req.project_path)

    if req.file:
        target = os.path.realpath(os.path.join(project, req.file))
        if not target.startswith(project + os.sep):
            raise HTTPException(status_code=400, detail="File path escapes the project folder.")
        if not os.path.isfile(target):
            raise HTTPException(status_code=404, detail=f"File not found: {req.file}")
        wc = word_count.count_words(target)
        result = {"file": req.file, "words": wc}
        if req.floor is not None and wc < req.floor:
            result["below_floor"] = True
        return result

    # Whole-project: detect type and sum.
    ptype = word_count.detect_project_type(project)
    if not ptype:
        raise HTTPException(status_code=400, detail="Could not detect project type (no manuscript/chapters or script/scenes).")
    if ptype == "novel":
        files = word_count.find_novel_chapters(project)
    elif ptype == "screenplay":
        files = word_count.find_screenplay_scenes(project)
    else:
        files = word_count.find_tv_episodes(project)

    items = [{"file": os.path.basename(f), "words": word_count.count_words(f)} for f in files]
    total = sum(i["words"] for i in items)
    return {
        "project_type": ptype,
        "total_words": total,
        "file_count": len(items),
        "floor": req.floor,
        "below_floor_count": sum(1 for i in items if req.floor and i["words"] < req.floor),
        "items": items,
    }


# ── Build manifest ────────────────────────────────────────────────────────────

@router.post("/build-manifest")
async def build_manifest_route(req: BuildManifestRequest):
    """Generate completion_manifest.json from the locked outline."""
    project = _require_project(req.project_path)

    # Resolve the outline file.
    outline_path = req.outline
    if outline_path:
        outline_path = os.path.realpath(os.path.join(project, outline_path))
        if not outline_path.startswith(project + os.sep) or not os.path.isfile(outline_path):
            raise HTTPException(status_code=404, detail=f"Outline not found: {req.outline}")
    else:
        for candidate in (
            os.path.join(project, "bible", "04_outline.md"),
            os.path.join(project, "bible", "04_season_arc.md"),
        ):
            if os.path.isfile(candidate):
                outline_path = candidate
                break
        if not outline_path:
            raise HTTPException(status_code=404, detail="No outline found (looked for bible/04_outline.md).")

    chapter_count = build_manifest.count_chapters_in_outline(outline_path)
    if chapter_count == 0:
        raise HTTPException(status_code=400, detail=f"No chapters detected in outline: {os.path.basename(outline_path)}")

    manifest = build_manifest.build_manifest(
        chapter_count, req.project_name, req.project_type, req.word_floor
    )

    output_path = os.path.join(project, "state", "completion_manifest.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    total_items = sum(len(s["items"]) for s in manifest["sections"])
    return {
        "manifest_path": os.path.relpath(output_path, project),
        "chapters_detected": chapter_count,
        "total_check_items": total_items,
        "word_floor": req.word_floor,
        "sections": len(manifest["sections"]),
        "outline_source": os.path.relpath(outline_path, project),
    }


# ── Read manifest ─────────────────────────────────────────────────────────────

@router.get("/manifest")
async def get_manifest_route(project_path: str = Query(...)):
    """Return the existing completion_manifest.json, or 404 if absent."""
    project = _require_project(project_path)
    path = _locate_manifest(project)
    if not path:
        raise HTTPException(status_code=404, detail="No completion_manifest.json found. Run build-manifest first.")
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


# ── Verify ────────────────────────────────────────────────────────────────────

@router.post("/verify")
async def verify_route(req: VerifyRequest):
    """Run the manifest verifier against disk. Sole PASS/FAIL authority."""
    project = _require_project(req.project_path)
    path = _locate_manifest(project)
    if not path:
        raise HTTPException(status_code=404, detail="No completion_manifest.json found. Run build-manifest first.")

    with open(path, "r", encoding="utf-8-sig") as f:
        manifest = json.load(f)

    expected = req.expected_chapters
    if expected is None:
        expected = verify_completion._auto_detect_chapters(project)

    all_pass, total, passed, failed, failures, chapter_hashes = verify_completion.verify_manifest(
        project, manifest, expected, skip_lint=req.skip_lint
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


# ── Finalize lints (the 6 finalize blocking/advisory lints) ───────────────────

@router.post("/lints")
async def lints_route(req: ProjectPathRequest):
    """Run lints.run_all — the finalize-gate lints (hollow critics, padding, refrains, etc.)."""
    project = _require_project(req.project_path)
    return {
        "lints": lints.run_all(project),
        "blocking_failures": [l["name"] for l in lints.run_all(project) if l["blocking"] and l["status"] == "FAIL"],
    }


# ── Deterministic lint suite (per-chapter) ────────────────────────────────────

@router.post("/lint-suite")
async def lint_suite_route(req: LintSuiteRequest):
    """Run the deterministic per-chapter / assembly / full-project lint suite."""
    project = _require_project(req.project_path)

    if req.chapter:
        target = os.path.realpath(os.path.join(project, req.chapter))
        if not target.startswith(project + os.sep) or not os.path.isfile(target):
            raise HTTPException(status_code=404, detail=f"Chapter not found: {req.chapter}")
        return {"mode": "chapter", "file": req.chapter, "findings": lint_suite.run_lints_on_chapter(target)}

    if req.assembly:
        target = os.path.realpath(os.path.join(project, req.assembly))
        if not target.startswith(project + os.sep) or not os.path.isfile(target):
            raise HTTPException(status_code=404, detail=f"Assembly not found: {req.assembly}")
        return {"mode": "assembly", "file": req.assembly, "findings": lint_suite.run_lints_on_assembly(target)}

    if req.full:
        return {"mode": "full", "result": lint_suite.run_full_lint_suite(project, json_output=False)}

    raise HTTPException(status_code=400, detail="Specify chapter, assembly, or full=true.")


# ── Finalize (the gate) ───────────────────────────────────────────────────────

@router.post("/finalize")
async def finalize_route(req: ProjectPathRequest):
    """
    Run the full completion gate. Writes state/COMPLETION_PASS.json (bound to a
    SHA-256 of the normalized manuscript) ONLY when the manifest verifies PASS
    AND every blocking lint passes. Otherwise writes COMPLETION_INCOMPLETE.json.
    No caller may write the certificate directly — only this route (via
    finalize.finalize) does.
    """
    project = _require_project(req.project_path)
    try:
        return finalize.finalize(project)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ── Critic runner (Phase C) ───────────────────────────────────────────────────

def _resolve_chapter(project: str, chapter_rel: str) -> str:
    target = os.path.realpath(os.path.join(project, chapter_rel))
    if not target.startswith(project + os.sep) or not os.path.isfile(target):
        raise HTTPException(status_code=404, detail=f"Chapter not found: {chapter_rel}")
    return target


def _resolve_call_model(qualified: str | None):
    """Resolve a qualified model id to a configured provider.

    Returns (api_key, model_name, base_url). Raises HTTPException 400 if the
    provider isn't configured. Falls back to the default model when ``qualified``
    is None, and to the writer/critic models when the caller is the pipeline.
    """
    from app.ai.providers import resolve
    target = qualified or get_default_model()
    try:
        resolved = resolve(target)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not resolved.is_configured:
        raise HTTPException(
            status_code=400,
            detail=(f"The '{resolved.label}' provider isn't configured. "
                    f"Add its base URL and API key in Settings."),
        )
    return resolved.api_key, resolved.model_name, resolved.base_url


@router.post("/run-critic")
async def run_critic_route(req: RunCriticRequest):
    """Run one critic over one chapter and write its gate-valid artifact."""
    project = _require_project(req.project_path)
    chapter = _resolve_chapter(project, req.chapter)
    if req.critic_type not in critics.CRITIC_TYPES and req.critic_type != critics.EDITORIAL_TYPE:
        raise HTTPException(status_code=400, detail=f"Unknown critic type: {req.critic_type}")
    api_key, model_name, base_url = _resolve_call_model(req.model_id)
    return await critics.run_critic(
        req.critic_type, chapter, project, api_key, model_name,
        context=req.context, base_url=base_url,
    )


@router.post("/run-all-critics")
async def run_all_critics_route(req: RunAllCriticsRequest):
    """Run all five critics + the editorial critic over one chapter, sequentially."""
    project = _require_project(req.project_path)
    chapter = _resolve_chapter(project, req.chapter)
    api_key, model_name, base_url = _resolve_call_model(req.model_id)

    results = []
    for ctype in (*critics.CRITIC_TYPES, critics.EDITORIAL_TYPE):
        result = await critics.run_critic(
            ctype, chapter, project, api_key, model_name,
            context=req.context, base_url=base_url,
        )
        results.append(result)
    return {"critics": results, "model_used": model_name}


# ── Orchestrator (Phase P) ────────────────────────────────────────────────────

def _make_model_call(api_key: str, model_name: str, base_url: str):
    """Build an injectable async model call bound to one provider+model."""
    from app.ai.openrouter import run_chat

    async def model_call(system_prompt: str, user_prompt: str) -> str:
        return await run_chat(
            api_key, model_name, system_prompt,
            [{"role": "user", "content": user_prompt}],
            temperature=0.4,
            base_url=base_url,
        )
    return model_call


@router.post("/start-run")
async def start_run_route(req: StartRunRequest):
    """Initialize (or reset) a pipeline run for a project."""
    project = _require_project(req.project_path)
    state = orchestrator.start_run(project, req.project_name, req.word_floor,
                                   instructions=req.instructions)
    return {
        "status": state.status,
        "current_phase": state.current_phase,
        "current_phase_label": orchestrator.PHASE_SPECS[state.current_phase].label,
        "units": state.units,
        "instructions": state.instructions,
        "run_state": state.to_dict(),
    }


@router.get("/run-state")
async def get_run_state_route(project_path: str = Query(...)):
    """Return the current pipeline run state, or null if none exists."""
    project = _require_project(project_path)
    state = orchestrator.load_run_state(project)
    if state is None:
        return {"active": False}
    current = orchestrator.PHASE_SPECS.get(state.current_phase)
    return {
        "active": True,
        "status": state.status,
        "current_phase": state.current_phase,
        "current_phase_label": current.label if current else state.current_phase,
        "current_unit_index": state.current_unit_index,
        "units": state.units,
        "instructions": state.instructions,
        "last_error": state.last_error,
        "phase_results": state.phase_results,
        "unit_results": {str(k): v for k, v in state.unit_results.items()},
    }


@router.post("/advance-phase")
async def advance_phase_route(req: AdvancePhaseRequest):
    """Run exactly ONE phase and return its artifact + gate verdict.

    Never auto-advances past a FAIL — the frontend surfaces the result for
    human approval before calling this endpoint again.
    """
    project = _require_project(req.project_path)
    # Build the role-based resolver: author phases -> writer_model, critic
    # phases -> critic_model (Open-Write A/B). Each resolves to its provider.
    from app.settings_store import get_writer_model, get_critic_model
    try:
        a_key, a_model, a_base = _resolve_call_model(get_writer_model())
        c_key, c_model, c_base = _resolve_call_model(get_critic_model())
    except HTTPException:
        raise
    author_call = _make_model_call(a_key, a_model, a_base)
    critic_call = _make_model_call(c_key, c_model, a_base)

    # Instructions are now persisted in the run state and applied by each
    # phase executor via _with_instructions(). No wrapping needed here.
    resolve_call = lambda role: critic_call if role == "critic" else author_call
    try:
        result = await orchestrator.advance_phase(project, resolve_call)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    result["writer_model"] = a_model
    result["critic_model"] = c_model
    return result


@router.get("/phase-output")
async def get_phase_output_route(
    project_path: str = Query(...),
    phase: str = Query(...),
    chapter: int | None = Query(None),
):
    """Return the recorded result for a phase (optionally for one chapter)."""
    project = _require_project(project_path)
    return orchestrator.get_phase_output(project, phase, chapter)
