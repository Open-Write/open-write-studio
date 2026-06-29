"""
harness/reporter.py — human-facing run summary (progress / accomplishments / blockers).

Reads a persisted RunState and produces a concise report. Adapted from The
Architect's reporter role: progress, what got done, what's stuck.
"""

from __future__ import annotations

from .models import TaskStatus
from .runner import RunState, _task_by_id, _deps_complete, _failed_dep


def summarize(state: RunState) -> dict:
    by_id = _task_by_id(state)
    records = state.records
    total = len(state.tasks)

    counts = {s.value: 0 for s in TaskStatus}
    completed, failed, blocked, pending = [], [], [], []
    for tid, rec in records.items():
        st = rec.get("status", TaskStatus.PENDING.value)
        counts[st] = counts.get(st, 0) + 1
        if st == TaskStatus.COMPLETED.value:
            completed.append(tid)
        elif st == TaskStatus.FAILED.value:
            failed.append(tid)
        elif st in (TaskStatus.PENDING.value, TaskStatus.READY.value, TaskStatus.RUNNING.value):
            # A pending task with a failed dependency is effectively blocked.
            if _failed_dep(state, tid, by_id):
                blocked.append(tid)
            elif not _deps_complete(state, tid, by_id):
                pending.append(tid)
            else:
                pending.append(tid)

    accomplishments = [
        {"task_id": tid, "detail": (records[tid].get("verification") or {}).get("detail", "")}
        for tid in completed
    ]
    blockers = []
    for tid in failed + blocked:
        rec = records.get(tid, {})
        blockers.append({
            "task_id": tid,
            "status": rec.get("status"),
            "reason": rec.get("error") or (rec.get("verification") or {}).get("detail", "")
                      or "dependency failed",
        })

    done = counts.get(TaskStatus.COMPLETED.value, 0)
    return {
        "goal": state.goal,
        "plan_id": state.plan_id,
        "status": state.status,
        "progress": f"{done}/{total}",
        "counts": counts,
        "accomplishments": accomplishments,
        "blockers": blockers,
        "remaining": pending,
    }
