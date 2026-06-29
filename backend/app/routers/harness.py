# routers/harness.py — orchestration-layer endpoints (The Architect protocols)
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.ai import providers
from app.settings_store import get_planner_model

router = APIRouter(prefix="/api/harness", tags=["harness"])


# ── Helpers ──────────────────────────────────────────────────────────────────

def _require_project(project_path: str) -> str:
    import os
    resolved = os.path.realpath(project_path)
    if not resolved or not os.path.isdir(resolved):
        raise HTTPException(status_code=404, detail=f"Project folder not found: {project_path}")
    return resolved


def _make_model_call(qualified: str):
    """Resolve a qualified model to a provider and return an async model_call."""
    from app.ai.openrouter import run_chat
    try:
        resolved = providers.resolve(qualified)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not resolved.is_configured:
        raise HTTPException(
            status_code=400,
            detail=(f"The '{resolved.label}' provider isn't configured. "
                    f"Add its base URL and API key in Settings."),
        )

    async def model_call(system_prompt: str, user_prompt: str) -> str:
        return await run_chat(
            resolved.api_key, resolved.model_name, system_prompt,
            [{"role": "user", "content": user_prompt}],
            temperature=0.4, base_url=resolved.base_url,
        )
    return model_call


# ── Request models ───────────────────────────────────────────────────────────

class PlanRequest(BaseModel):
    project_path: str
    goal: str
    context: str = ""


class StartRunRequest(BaseModel):
    project_path: str
    plan: dict        # a TaskPlan dict (goal + tasks[])


class AdvanceRequest(BaseModel):
    project_path: str


# ── Routes ───────────────────────────────────────────────────────────────────

@router.get("/registry")
async def registry_route():
    """Return the domains/roles registry summary (for the UI/planner context)."""
    from app.harness import router as harness_router_mod
    return harness_router_mod.registry_summary()


@router.post("/plan")
async def plan_route(req: PlanRequest):
    """Goal -> TaskPlan via the planner model (multi-provider)."""
    project = _require_project(req.project_path)
    from app.harness import planner
    model_call = _make_model_call(get_planner_model())
    try:
        plan = await planner.plan(req.goal, model_call, context=req.context)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Planner produced an invalid plan: {exc}")
    return plan.model_dump(mode="json")


@router.post("/start-run")
async def start_run_route(req: StartRunRequest):
    """Validate a plan dict and initialize a run."""
    project = _require_project(req.project_path)
    from app.harness.models import TaskPlan
    from app.harness import runner
    try:
        plan = TaskPlan(**req.plan)
    except Exception as exc:  # pydantic ValidationError
        raise HTTPException(status_code=422, detail=f"Invalid plan: {exc}")
    state = runner.start_run(project, plan)
    return state.to_dict()


@router.get("/run-state")
async def run_state_route(project_path: str = Query(...)):
    project = _require_project(project_path)
    from app.harness import runner
    state = runner.load_run_state(project)
    return {"active": state is not None, "state": state.to_dict() if state else None}


@router.post("/advance-task")
async def advance_task_route(req: AdvanceRequest):
    """Run exactly ONE ready task and verify it."""
    project = _require_project(req.project_path)
    from app.harness import runner

    # The runner resolves the task's model itself (via resolve_task); we only
    # provide the provider-bound model call for whatever qualified id it picks.
    def model_call_for_model(qualified: str):
        return _make_model_call(qualified)

    try:
        return await runner.advance_task(project, model_call_for_model)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@router.get("/report")
async def report_route(project_path: str = Query(...)):
    project = _require_project(project_path)
    from app.harness import runner, reporter
    state = runner.load_run_state(project)
    if state is None:
        return {"active": False}
    return {"active": True, "report": reporter.summarize(state)}
