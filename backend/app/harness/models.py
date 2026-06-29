"""
harness/models.py — The Architect generalized task models, adapted for Open-Write.

This is the orchestration layer ABOVE the existing pipeline. A goal is
decomposed into a dependency-ordered ``TaskPlan``; each ``Task`` is routed by
(domain, role), executed against a project, and certified by a ``VerifierSpec``
on disk. "No self-reported completion" — the verifier is the sole authority.

Adapted from ``C:\\The_Architect\\runtime\\models.py`` for Open-Write-Studio:
  - model selection is NOT a Roo/AgentType enum; it flows through the multi-
    provider system (qualified "<provider>/<model>" ids, resolved in the router).
  - "project" is the open-write project being worked on; the runner operates on
    the run's ``project_path``.
  - validation (unique ids, acyclic dependencies) is enforced at construction.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


# ── Enums ────────────────────────────────────────────────────────────────────

class TaskPriority(int, Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class TaskStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"           # dependencies satisfied, awaiting execution
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class VerifierKind(str, Enum):
    FILES = "files"            # artifact files must exist on disk
    TOOL = "tool"              # run a tool; gate token must appear in output
    MANIFEST = "manifest"      # completion_manifest gate must pass
    TESTS = "tests"            # a test command must exit 0


class TaskMode(str, Enum):
    CODE = "code"
    ARCHITECT = "architect"
    ASK = "ask"
    DEBUG = "debug"


# ── Verifier spec ────────────────────────────────────────────────────────────

class VerifierSpec(BaseModel):
    """How the verifier certifies a task done. Never self-grades the maker."""
    kind: VerifierKind = VerifierKind.FILES
    tool: Optional[str] = Field(default=None, description="Tool to run, e.g. 'tools/verify_completion.py'")
    files_expected: list[str] = Field(default_factory=list, description="Artifact paths (relative to project) that must exist")
    manifest_key: Optional[str] = Field(default=None, description="completion_manifest entry that must pass")
    gate: str = Field(default="pass", description="Required verdict token")


# ── Task ─────────────────────────────────────────────────────────────────────

class Task(BaseModel):
    """A single unit of work, routable across domains."""

    task_id: str
    domain: str = "writing"
    project: str = "open-write"
    role: str                                  # agent ROLE (not a model)
    priority: TaskPriority = TaskPriority.NORMAL
    mode: TaskMode = TaskMode.CODE
    prompt: str
    context_files: list[str] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    timeout_minutes: int = Field(default=60, ge=5, le=480)
    acceptance_criteria: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list, description="Skill files the executor MUST read first")
    verifier: Optional[VerifierSpec] = None
    model: Optional[str] = Field(default=None, description="Qualified provider/model override; None = role default")


class TaskPlan(BaseModel):
    """A dependency-ordered batch of tasks from one planning cycle."""
    plan_id: str
    goal: str
    generated_at: datetime = Field(default_factory=datetime.now)
    tasks: list[Task]
    notes: Optional[str] = None

    @model_validator(mode="after")
    def _validate(self) -> "TaskPlan":
        ids = [t.task_id for t in self.tasks]
        if len(ids) != len(set(ids)):
            dupes = {i for i in ids if ids.count(i) > 1}
            raise ValueError(f"Duplicate task_ids: {sorted(dupes)}")
        known = set(ids)
        # Every dependency must reference a task in this plan.
        for t in self.tasks:
            for dep in t.depends_on:
                if dep not in known:
                    raise ValueError(f"Task {t.task_id} depends_on unknown task '{dep}'")
        # Acyclic (DFS).
        self._check_acyclic(self.tasks)
        return self

    @staticmethod
    def _check_acyclic(tasks: list[Task]) -> None:
        graph = {t.task_id: list(t.depends_on) for t in tasks}
        WHITE, GREY, BLACK = 0, 1, 2
        color = {tid: WHITE for tid in graph}

        def dfs(node: str, path: list[str]) -> None:
            color[node] = GREY
            for nxt in graph.get(node, []):
                if color[nxt] == GREY:
                    cycle = path[path.index(nxt):] + [nxt]
                    raise ValueError(f"Dependency cycle detected: {' -> '.join(cycle)}")
                if color[nxt] == WHITE:
                    dfs(nxt, path + [nxt])
            color[node] = BLACK

        for tid in graph:
            if color[tid] == WHITE:
                dfs(tid, [tid])


# ── Run state (persisted) ────────────────────────────────────────────────────

class TaskRecord(BaseModel):
    """Per-task execution + verification record, persisted in the run state."""
    status: TaskStatus = TaskStatus.PENDING
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    output_preview: str = ""
    verification: Optional[dict] = None        # {passed, kind, detail, evidence}
    blockers: list[str] = Field(default_factory=list)
    error: Optional[str] = None


def topological_order(tasks: list[Task]) -> list[str]:
    """Return task_ids in dependency order (Kahn's algorithm). Stable on input order."""
    indeg = {t.task_id: 0 for t in tasks}
    dependents: dict[str, list[str]] = {t.task_id: [] for t in tasks}
    by_id = {t.task_id: t for t in tasks}
    for t in tasks:
        for dep in t.depends_on:
            indeg[t.task_id] += 1
            dependents[dep].append(t.task_id)
    ready = [t.task_id for t in tasks if indeg[t.task_id] == 0]
    order: list[str] = []
    while ready:
        ready.sort(key=lambda tid: (by_id[tid].priority, by_id[tid].task_id))
        n = ready.pop(0)
        order.append(n)
        for d in dependents[n]:
            indeg[d] -= 1
            if indeg[d] == 0:
                ready.append(d)
    if len(order) != len(tasks):
        raise ValueError("Cannot order tasks: cycle or unsatisfiable dependency")
    return order
