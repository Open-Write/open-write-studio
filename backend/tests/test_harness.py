"""
test_harness.py — the orchestration layer (The Architect protocols).

Validates: task-plan validation (unique ids, acyclic deps, topological order),
router resolution, verifier kinds (files + manifest via the gate), the planner
parser (injectable model call), and the runner's dependency-ordered execution +
verification. No network — model calls are injected.
"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from app.harness import models, router, verifier, planner, runner
from pipeline_fixtures import build_project


# ── Models ───────────────────────────────────────────────────────────────────

def _task(tid, depends_on=None, priority=3):
    return {
        "task_id": tid, "domain": "writing", "role": "writer", "priority": priority,
        "prompt": f"do {tid}", "depends_on": depends_on or [],
        "acceptance_criteria": ["x done"], "verifier": {"kind": "files", "files_expected": [tid]},
    }


def test_plan_rejects_duplicate_ids():
    try:
        models.TaskPlan(plan_id="p", goal="g",
                        tasks=[models.Task(**_task("t1")), models.Task(**_task("t1"))])
        assert False, "expected duplicate-id error"
    except Exception:
        pass


def test_plan_rejects_cycle():
    try:
        models.TaskPlan(plan_id="p", goal="g", tasks=[
            models.Task(**_task("a", depends_on=["b"])),
            models.Task(**_task("b", depends_on=["a"])),
        ])
        assert False, "expected cycle error"
    except Exception as e:
        assert "cycle" in str(e).lower()


def test_plan_rejects_unknown_dependency():
    try:
        models.TaskPlan(plan_id="p", goal="g",
                        tasks=[models.Task(**_task("a", depends_on=["zzz"]))])
        assert False, "expected unknown-dep error"
    except Exception:
        pass


def test_topological_order_respects_deps_and_priority():
    tasks = [
        models.Task(**_task("a", priority=2)),
        models.Task(**_task("b", depends_on=["a"], priority=1)),
        models.Task(**_task("c", depends_on=["a"])),
    ]
    order = models.topological_order(tasks)
    assert order.index("a") < order.index("b")
    assert order.index("a") < order.index("c")


# ── Router ───────────────────────────────────────────────────────────────────

def test_router_resolves_known_role():
    t = router.resolve("writing", "architect")
    assert t.role == "architect"
    assert t.domain == "writing"
    assert t.model  # resolves to some qualified/default model
    assert isinstance(t.skills, tuple)


def test_router_rejects_unknown():
    try:
        router.resolve("nope", "coder"); assert False
    except router.RoutingError:
        pass
    try:
        router.resolve("writing", "nope"); assert False
    except router.RoutingError:
        pass


# ── Verifier ─────────────────────────────────────────────────────────────────

def test_verifier_files_pass_and_fail():
    v = verifier.Verifier()
    with tempfile.TemporaryDirectory() as root:
        open(os.path.join(root, "a.txt"), "w").write("x")
        ok = v.verify(models.VerifierSpec(kind="files", files_expected=["a.txt"]), root)
        assert ok.passed is True
        bad = v.verify(models.VerifierSpec(kind="files", files_expected=["missing.txt"]), root)
        assert bad.passed is False


def test_verifier_manifest_uses_gate():
    v = verifier.Verifier()
    with tempfile.TemporaryDirectory() as root:
        build_project(root)  # gate-PASSING artifacts
        # build_project creates artifacts but not the manifest; build it now.
        from app.pipeline import build_manifest
        manifest = build_manifest.build_manifest(1, "Test", "novel", 300)
        os.makedirs(os.path.join(root, "state"), exist_ok=True)
        with open(os.path.join(root, "state", "completion_manifest.json"), "w") as f:
            json.dump(manifest, f)
        ok = v.verify(models.VerifierSpec(kind="manifest"), root)
        assert ok.passed is True, ok.detail
        assert ok.kind == "manifest"


# ── Planner ──────────────────────────────────────────────────────────────────

_PLAN_REPLY = json.dumps({
    "plan_id": "test-1",
    "goal": "Write chapter 1",
    "tasks": [
        {"task_id": "t1", "domain": "writing", "role": "architect", "priority": 2,
         "prompt": "Plan chapter 1", "depends_on": [], "acceptance_criteria": ["plan exists"],
         "verifier": {"kind": "files", "files_expected": ["plan.md"]}},
        {"task_id": "t2", "domain": "writing", "role": "writer", "priority": 3,
         "prompt": "Write chapter 1", "depends_on": ["t1"], "acceptance_criteria": ["draft exists"],
         "verifier": {"kind": "files", "files_expected": ["draft.md"]}},
    ],
    "notes": "plan then write",
})


def test_planner_parses_valid_plan():
    p = planner.parse_plan(_PLAN_REPLY, "Write chapter 1")
    assert p.plan_id == "test-1"
    assert len(p.tasks) == 2
    assert p.tasks[1].depends_on == ["t1"]


def test_planner_plan_call_uses_injected_model():
    async def mc(system, user):
        assert "GOAL" in user
        return _PLAN_REPLY
    import asyncio
    p = asyncio.new_event_loop().run_until_complete(planner.plan("Write chapter 1", mc))
    assert len(p.tasks) == 2


# ── Runner ───────────────────────────────────────────────────────────────────

def test_runner_executes_in_dependency_order_and_verifies():
    with tempfile.TemporaryDirectory() as root:
        plan = models.TaskPlan(plan_id="r1", goal="g", tasks=[
            # t1 has no deps; executor writes plan.md -> files verifier passes.
            models.Task(task_id="t1", domain="writing", role="architect", priority=2,
                        prompt="plan", depends_on=[], acceptance_criteria=[],
                        verifier=models.VerifierSpec(kind="files", files_expected=["plan.md"])),
            # t2 depends on t1; executor writes draft.md.
            models.Task(task_id="t2", domain="writing", role="writer", priority=3,
                        prompt="write", depends_on=["t1"], acceptance_criteria=[],
                        verifier=models.VerifierSpec(kind="files", files_expected=["draft.md"])),
        ])
        runner.start_run(root, plan)

        async def writer(system, user):
            # The runner injects the task prompt; emulate by creating the file.
            if "plan" in user.lower():
                open(os.path.join(root, "plan.md"), "w").write("plan")
            else:
                open(os.path.join(root, "draft.md"), "w").write("draft")
            return "done"

        def mcr(qualified):
            return writer

        # First advance: t1 (deps satisfied), then t2.
        r1 = _await(runner.advance_task(root, mcr))
        assert r1["task_id"] == "t1"
        assert r1["status"] == "completed"
        r2 = _await(runner.advance_task(root, mcr))
        assert r2["task_id"] == "t2"
        assert r2["status"] == "completed"
        # Third advance: nothing left -> complete.
        r3 = _await(runner.advance_task(root, mcr))
        assert r3["status"] == "complete"


def test_runner_blocks_downstream_on_failed_verify():
    with tempfile.TemporaryDirectory() as root:
        plan = models.TaskPlan(plan_id="r2", goal="g", tasks=[
            models.Task(task_id="t1", domain="writing", role="writer", priority=2,
                        prompt="x", depends_on=[], acceptance_criteria=[],
                        verifier=models.VerifierSpec(kind="files", files_expected=["never.md"])),
        ])
        runner.start_run(root, plan)

        async def noop(system, user):
            return "did nothing"  # never.md not created -> verify fails

        r = _await(runner.advance_task(root, lambda qualified: noop))
        assert r["task_id"] == "t1"
        assert r["status"] == "failed"
        assert r["verification"]["passed"] is False


def test_verifier_tool_rejects_path_traversal():
    v = verifier.Verifier()
    with tempfile.TemporaryDirectory() as root:
        # A traversal tool path must be refused, not executed.
        bad = v.verify(
            models.VerifierSpec(kind="tool", tool="../../escape.py", gate="pass"),
            root,
        )
        assert bad.passed is False
        assert "escapes project" in bad.detail or "missing" in bad.detail


def _await(coro):
    import asyncio
    return asyncio.new_event_loop().run_until_complete(coro)


def _run_all():
    tests = [
        test_plan_rejects_duplicate_ids,
        test_plan_rejects_cycle,
        test_plan_rejects_unknown_dependency,
        test_topological_order_respects_deps_and_priority,
        test_router_resolves_known_role,
        test_router_rejects_unknown,
        test_verifier_files_pass_and_fail,
        test_verifier_manifest_uses_gate,
        test_planner_parses_valid_plan,
        test_planner_plan_call_uses_injected_model,
        test_runner_executes_in_dependency_order_and_verifies,
        test_runner_blocks_downstream_on_failed_verify,
        test_verifier_tool_rejects_path_traversal,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {t.__name__}: {e}")
        except Exception as e:
            failed += 1
            print(f"  ERROR {t.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return failed


if __name__ == "__main__":
    sys.exit(1 if _run_all() else 0)
