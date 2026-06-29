"""
harness/runner.py — the orchestration dispatch loop, step by step.

A run is a goal + a validated TaskPlan executed against a project. Run state is
persisted to ``<project>/state/harness_run.json`` so a run resumes across
sessions (Open-Write: state over memory; reduce context = resume, never abbreviate).

Each call to ``advance_task`` runs exactly ONE ready task:
  1. pick the next dependency-satisfied task (topological + priority order),
  2. resolve its (domain, role) -> model + skills via the router,
  3. execute: read skills + context files, call the role's resolved provider
     model with the task prompt, return the reply,
  4. verify the result via its VerifierSpec (or the domain default),
  5. record status + verification; block downstream tasks on FAIL.

The executor never self-grades; the verifier certifies. The model call is
injectable so the dispatch logic is testable without a network key.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Awaitable, Callable, Optional

from . import router, verifier
from .models import Task, TaskPlan, TaskStatus, TaskRecord, topological_order, VerifierSpec

ModelCall = Callable[[str, str], Awaitable[str]]

RUN_STATE_REL = os.path.join("state", "harness_run.json")


# ── Run state ────────────────────────────────────────────────────────────────

@dataclass
class RunState:
    project_path: str
    plan_id: str
    goal: str
    status: str = "running"          # running | complete | failed | blocked
    started_at: str = ""
    updated_at: str = ""
    tasks: list[dict] = field(default_factory=list)            # serialized Task list
    records: dict[str, dict] = field(default_factory=dict)     # task_id -> TaskRecord dict
    last_error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "RunState":
        return cls(
            project_path=d["project_path"],
            plan_id=d.get("plan_id", ""),
            goal=d.get("goal", ""),
            status=d.get("status", "running"),
            started_at=d.get("started_at", ""),
            updated_at=d.get("updated_at", ""),
            tasks=d.get("tasks", []),
            records=d.get("records", {}),
            last_error=d.get("last_error"),
        )


def _run_state_path(project: str) -> str:
    return os.path.join(project, RUN_STATE_REL)


def load_run_state(project: str) -> Optional[RunState]:
    path = _run_state_path(project)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return RunState.from_dict(json.load(f))


def save_run_state(state: RunState) -> None:
    state.updated_at = datetime.now().isoformat()
    path = _run_state_path(state.project_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)


def start_run(project: str, plan: TaskPlan) -> RunState:
    """Initialize a run from a validated plan. Returns the fresh RunState."""
    project = os.path.abspath(project)
    tasks = [t.model_dump(mode="json") for t in plan.tasks]
    records = {t.task_id: TaskRecord(status=TaskStatus.PENDING).model_dump(mode="json")
               for t in plan.tasks}
    state = RunState(
        project_path=project,
        plan_id=plan.plan_id,
        goal=plan.goal,
        started_at=datetime.now().isoformat(),
        tasks=tasks,
        records=records,
    )
    save_run_state(state)
    return state


# ── Execution ────────────────────────────────────────────────────────────────

def _task_by_id(state: RunState) -> dict[str, dict]:
    return {t["task_id"]: t for t in state.tasks}


def _deps_complete(state: RunState, task_id: str, by_id: dict[str, dict]) -> bool:
    for dep in by_id[task_id].get("depends_on", []):
        rec = state.records.get(dep, {})
        if rec.get("status") != TaskStatus.COMPLETED.value:
            return False
    return True


def _failed_dep(state: RunState, task_id: str, by_id: dict[str, dict]) -> Optional[str]:
    for dep in by_id[task_id].get("depends_on", []):
        rec = state.records.get(dep, {})
        if rec.get("status") in (TaskStatus.FAILED.value, TaskStatus.SKIPPED.value, TaskStatus.BLOCKED.value):
            return dep
    return None


def next_ready_task(state: RunState) -> Optional[dict]:
    """Return the next executable task (deps satisfied, not yet run), or None."""
    by_id = _task_by_id(state)
    # Use the plan's topological order, then priority, to stay deterministic.
    order = topological_order([Task(**t) for t in state.tasks])
    for tid in order:
        rec = state.records.get(tid, {})
        if rec.get("status") not in (TaskStatus.PENDING.value, TaskStatus.READY.value):
            continue
        if _failed_dep(state, tid, by_id):
            continue
        if _deps_complete(state, tid, by_id):
            return by_id[tid]
    return None


def _read_context(project: str, skills: list[str], context_files: list[str]) -> str:
    parts = []
    for rel in (skills or []) + (context_files or []):
        p = os.path.join(project, rel)
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8-sig") as f:
                parts.append(f"--- {rel} ---\n{f.read()}\n")
    return "\n".join(parts)


def _effective_verifier(task_dict: dict, default_verifier: Optional[dict]) -> Optional[VerifierSpec]:
    v = task_dict.get("verifier") or default_verifier
    if not v:
        return None
    return VerifierSpec(**v)


async def advance_task(project: str, model_call_for_model: Callable[[str], ModelCall]) -> dict:
    """Run exactly ONE ready task.

    ``model_call_for_model(qualified)`` returns the async model call bound to
    that qualified provider/model id. The runner resolves the task's model
    itself (via ``resolve_task``) so the executed model is always consistent
    with the reported one.
    """
    project = os.path.abspath(project)
    state = load_run_state(project)
    if state is None:
        raise RuntimeError("No harness run in progress. Call start_run first.")
    if state.status == "complete":
        return {"task_id": None, "message": "Run already complete.", "state": state.to_dict()}

    task_dict = next_ready_task(state)
    if task_dict is None:
        # Nothing ready: complete if all done, else blocked.
        remaining = [tid for tid, r in state.records.items()
                     if r.get("status") in (TaskStatus.PENDING.value, TaskStatus.READY.value)]
        if not remaining:
            state.status = "complete"
        else:
            state.status = "blocked"
            state.last_error = f"Blocked: {len(remaining)} task(s) cannot run (unmet/failed deps)."
        save_run_state(state)
        return {"task_id": None, "status": state.status, "state": state.to_dict()}

    task = Task(**task_dict)
    try:
        target = router.resolve_task(task)
    except router.RoutingError as exc:
        rec = TaskRecord(status=TaskStatus.FAILED, error=str(exc), finished_at=datetime.now())
        state.records[task.task_id] = rec.model_dump(mode="json")
        save_run_state(state)
        return {"task_id": task.task_id, "error": str(exc), "state": state.to_dict()}

    # Resolve the model call from the SAME target the runner reports, so the
    # executed and reported models can never diverge.
    model_call = model_call_for_model(target.model)
    state.records[task.task_id] = TaskRecord(
        status=TaskStatus.RUNNING, started_at=datetime.now(),
    ).model_dump(mode="json")
    save_run_state(state)

    system = (f"You are the {target.role.upper()} role. {target.role_job}\n"
              "Follow the cardinal rules: read skills before acting; do not self-report "
              "completion. Produce exactly what the task asks for.")
    user = f"{_read_context(project, list(target.skills), task.context_files)}\n" \
           f"TASK:\n{task.prompt}\n\nACCEPTANCE CRITERIA:\n- " + \
           "\n- ".join(task.acceptance_criteria or ["(none stated)"])

    try:
        reply = await model_call(system, user)
    except Exception as exc:  # noqa: BLE001 — record and surface, never crash the run
        rec = TaskRecord(status=TaskStatus.FAILED, error=f"{type(exc).__name__}: {exc}",
                         finished_at=datetime.now())
        state.records[task.task_id] = rec.model_dump(mode="json")
        state.last_error = rec.error
        save_run_state(state)
        raise RuntimeError(rec.error) from exc

    # Verify on disk.
    v = verifier.Verifier()
    spec = _effective_verifier(task_dict, target.default_verifier)
    result = v.verify(spec, project, task_metadata={"files_expected": spec.files_expected if spec else []})
    status = TaskStatus.COMPLETED if result.passed else TaskStatus.FAILED
    rec = TaskRecord(
        status=status,
        finished_at=datetime.now(),
        output_preview=(reply or "")[:400],
        verification={
            "passed": result.passed, "kind": result.kind,
            "detail": result.detail, "evidence": result.evidence[:8],
        },
        blockers=[] if result.passed else [result.detail],
    )
    state.records[task.task_id] = rec.model_dump(mode="json")
    save_run_state(state)

    return {
        "task_id": task.task_id,
        "role": task.role,
        "domain": task.domain,
        "model": target.model,
        "status": status.value,
        "verification": rec.verification,
        "output_preview": rec.output_preview,
        "state": state.to_dict(),
    }
