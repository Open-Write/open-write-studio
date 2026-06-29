"""
harness/planner.py — the orchestration Planner.

Decomposes a goal into a dependency-ordered ``TaskPlan`` and routes each task to
a (domain, role). Adapted from ``C:\\The_Architect\\core\\planner_prompt.md``:
the system prompt is rendered from the domains/roles registry so adding a domain
never edits code. The planner model is selected through the multi-provider
system (``planner_model``); the model call is injectable so the parsing/routing
logic is testable without a network key.

The planner NEVER executes — it only decides WHAT and WHERE, never HOW.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Awaitable, Callable

from . import router
from .models import Task, TaskPlan

ModelCall = Callable[[str, str], Awaitable[str]]


_SYSTEM_PROMPT = """\
You are THE ORCHESTRATOR for Open-Write-Studio, an AI writing app that also \
hosts its own code. A human gives you a GOAL; you decompose it into an ordered, \
dependency-aware batch of tasks and route each to the correct DOMAIN and agent \
ROLE. You are a PROJECT MANAGER and ROUTER, never an executor: you decide WHAT \
and WHERE, not HOW.

## Routing Model
Every task MUST specify:
- domain: one of the domains below.
- role: an agent role from the roles list (NOT a model name).
Pick the domain whose skills/state match the task. Writing/novel work uses the \
"writing" domain; app/backend/frontend/harness work uses "core".

## Cardinal Rules
1. Read before act: every task lists the skill files its executor must read first.
2. No self-reported completion: each task declares a verifier; a task is done \
only when its verifier returns PASS.
3. Verifier is law.
4. >=2 distinct models per critical (critic/adversarial/editorial) pass where \
applicable — take the UNION of flagged issues.

## Priority
1=CRITICAL (blocking), 2=HIGH, 3=NORMAL, 4=LOW.

## Dependency Rules
- Foundation tasks finish before dependent ones.
- A writing writer task depends_on its architect (plan) task.

## Output Format
Respond with ONLY a JSON object matching the schema. No preamble, no markdown \
fences. Raw JSON only.

{
  "plan_id": "<date>-<seq>",
  "goal": "<the goal>",
  "tasks": [
    {
      "task_id": "t-001",
      "domain": "<domain>",
      "role": "<role>",
      "priority": 3,
      "prompt": "<specific, self-contained instruction; WHAT not HOW>",
      "context_files": ["<path/relative/to/project>"],
      "depends_on": [],
      "timeout_minutes": 60,
      "acceptance_criteria": ["<testable condition>"],
      "skills": ["<skill files the executor must read first>"],
      "verifier": {
        "kind": "manifest|tool|files|tests",
        "tool": "<optional tool path>",
        "files_expected": ["<paths that must exist>"],
        "manifest_key": "<optional manifest entry>",
        "gate": "pass"
      }
    }
  ],
  "notes": "<why these tasks and this ordering>"
}

## Task Planning Rules
- 1-6 tasks per cycle.
- ALWAYS include acceptance_criteria and a verifier. "It works" is not a criterion.
- Make prompts specific and self-contained; reference concrete files when known.

## === Domain & Role Registry ===
__REGISTRY__
"""


def build_planner_prompt() -> str:
    """Render the system prompt with the live registry injected."""
    summary = router.registry_summary()
    lines = ["DOMAINS:"]
    for name, d in summary["domains"].items():
        lines.append(f"- {name}: {d['description']} (default role: {d['default_role']})")
    lines.append("ROLES:")
    for name, job in summary["roles"].items():
        lines.append(f"- {name}: {job}")
    return _SYSTEM_PROMPT.replace("__REGISTRY__", "\n".join(lines))


def _extract_json(reply: str) -> dict:
    """Pull the first JSON object out of a model reply (tolerates fences/preamble)."""
    text = reply.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    if start < 0:
        raise ValueError("Planner reply contained no JSON object.")
    # Track brace depth to find the matching close (naive but robust for our schema).
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i + 1])
    return json.loads(text[start:])


def parse_plan(reply: str, goal: str) -> TaskPlan:
    """Parse a planner reply into a validated TaskPlan."""
    data = _extract_json(reply)
    if "tasks" not in data:
        raise ValueError("Planner reply missing 'tasks'.")
    plan_id = data.get("plan_id") or f"plan-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    tasks = [Task(**t) for t in data["tasks"]]
    return TaskPlan(
        plan_id=plan_id,
        goal=data.get("goal", goal),
        generated_at=datetime.now(),
        tasks=tasks,
        notes=data.get("notes"),
    )


async def plan(goal: str, model_call: ModelCall, context: str = "") -> TaskPlan:
    """Plan a goal via an injectable model call. Returns a validated TaskPlan."""
    system = build_planner_prompt()
    user = f"GOAL:\n{goal}\n"
    if context:
        user += f"\nCONTEXT:\n{context}\n"
    user += "\nProduce the TaskPlan JSON now."
    reply = await model_call(system, user)
    return parse_plan(reply, goal)
