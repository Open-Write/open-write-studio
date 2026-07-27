#!/usr/bin/env python3
"""
ow_cli.py — Open-Write Pipeline CLI

Drive the Open-Write pipeline from the command line for debugging and testing.
Calls the running backend API on localhost:8000 (the Tauri sidecar must be
running), or imports the orchestrator directly for standalone testing.

Usage:
    python tools/ow_cli.py status <project_path>
    python tools/ow_cli.py start  <project_path> [--instructions "..."]
    python tools/ow_cli.py advance <project_path>
    python tools/ow_cli.py advance-all <project_path>  (auto-run all phases)
    python tools/ow_cli.py reset  <project_path>
    python tools/ow_cli.py outputs <project_path>
    python tools/ow_cli.py read   <project_path> <relpath>
    python tools/ow_cli.py critic-test <project_path>  (test one critic call)
"""


def _direct_api(method: str, path: str, body: dict | None = None, params: dict | None = None) -> dict:
    """Call the orchestrator directly (bypasses the sidecar). Used for debugging."""
    import asyncio
    from app.pipeline import orchestrator, outputs
    from app.routers.pipeline import _resolve_call_model, _make_model_call
    from app.settings_store import get_writer_model, get_critic_model

    if path == "/api/pipeline/run-state":
        project = params["project_path"]
        state = orchestrator.load_run_state(project)
        if state is None:
            return {"active": False}
        current = orchestrator.PHASE_SPECS.get(state.current_phase)
        return {
            "active": True, "status": state.status,
            "current_phase": state.current_phase,
            "current_phase_label": current.label if current else state.current_phase,
            "current_unit_index": state.current_unit_index,
            "units": state.units, "instructions": state.instructions,
            "last_error": state.last_error,
            "unit_results": {str(k): v for k, v in state.unit_results.items()},
        }

    if path == "/api/pipeline/start-run":
        project = body["project_path"]
        state = orchestrator.start_run(project, body.get("project_name", ""),
                                       instructions=body.get("instructions", ""))
        current = orchestrator.PHASE_SPECS.get(state.current_phase)
        return {"status": state.status, "current_phase": state.current_phase,
                "current_phase_label": current.label if current else state.current_phase,
                "units": state.units}

    if path == "/api/pipeline/advance-phase":
        project = body["project_path"]
        # Clear stale locks from previous event loops (each asyncio.run creates
        # a new loop; locks cached from a prior loop can deadlock).
        from app.pipeline.orchestrator import _RUN_LOCKS
        _RUN_LOCKS.pop(os.path.abspath(project), None)
        # Use per-phase model routing with fallback for critic phases.
        from app.settings_store import get_model_for_phase, get_writer_model
        _model_cache = {}
        def _get_info(mid):
            if mid not in _model_cache:
                _model_cache[mid] = _resolve_call_model(mid)
            return _model_cache[mid]

        def _resolve_for_phase(phase):
            mid = get_model_for_phase(phase)
            k, n, b = _get_info(mid)
            call = _make_model_call(k, n, b)
            if phase in ("critics", "editorial"):
                aid = get_writer_model()
                if mid != aid:
                    ak, an, ab = _get_info(aid)
                    ac = _make_model_call(ak, an, ab)
                    async def _fb(s, u):
                        try: return await call(s, u)
                        except Exception: return await ac(s, u)
                    return _fb
            return call

        try:
            result = asyncio.run(orchestrator.advance_phase(project, _resolve_for_phase))
        except RuntimeError as exc:
            return {"error": str(exc)}
        except Exception as exc:
            import traceback
            traceback.print_exc()
            return {"error": f"{type(exc).__name__}: {exc}"}
        return result

    if path == "/api/pipeline/reset-run":
        orchestrator.reset_run(body["project_path"])
        return {"status": "reset"}

    if path == "/api/pipeline/outputs":
        return outputs.build_output_catalog(params["project_path"])

    if path == "/api/pipeline/output-file":
        return outputs.read_artifact(params["project_path"], params["path"])

    return {"error": f"Direct mode does not support {path}"}



import argparse
import json
import os
import sys
import textwrap

# Ensure the backend package is importable.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_CONFIG = {"api_base": "http://localhost:8000", "direct": False}


def _api(method: str, path: str, body: dict | None = None, params: dict | None = None) -> dict:
    """Call the backend API (or the orchestrator directly in direct mode)."""
    if _CONFIG["direct"]:
        return _direct_api(method, path, body, params)
    import httpx
    url = f"{_CONFIG['api_base']}{path}"
    try:
        if method == "GET":
            r = httpx.get(url, params=params, timeout=600)
        else:
            r = httpx.post(url, json=body, timeout=600)
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError:
        print(f"[ERROR] Cannot reach backend at {_CONFIG['api_base']}. Is the Tauri app running?")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        print(f"[HTTP {e.response.status_code}] {e.response.text[:500]}")
        sys.exit(1)


def cmd_status(args):
    """Show the current pipeline run state."""
    data = _api("GET", "/api/pipeline/run-state", params={"project_path": args.project})
    if not data.get("active"):
        print("No active pipeline run.")
        return
    print(f"Status:   {data['status']}")
    print(f"Phase:    {data.get('current_phase_label', data.get('current_phase', '?'))}")
    print(f"Unit idx: {data.get('current_unit_index', '?')}")
    print(f"Units:    {data.get('units', [])}")
    print(f"Error:    {data.get('last_error') or '(none)'}")
    print(f"Brief:    {(data.get('instructions') or '')[:120]}...")
    # Show unit_results summary
    ur = data.get("unit_results", {})
    for ch, phases in sorted(ur.items(), key=lambda x: int(x[0])):
        print(f"\n  Chapter {ch}:")
        for p, r in phases.items():
            verdict = r.get("gate", {}).get("verdict", "") if isinstance(r.get("gate"), dict) else ""
            wc = r.get("word_count", "")
            err = r.get("error", "")
            info = f"verdict={verdict}" if verdict else f"wc={wc}" if wc else ""
            if err:
                info += f" ERROR={err}"
            print(f"    {p}: {info}")


def cmd_start(args):
    """Start a new pipeline run."""
    data = _api("POST", "/api/pipeline/start-run", body={
        "project_path": args.project,
        "project_name": os.path.basename(args.project),
        "instructions": args.instructions or "",
    })
    print(f"Run started. Status: {data.get('status')}")
    print(f"Phase: {data.get('current_phase_label', data.get('current_phase'))}")
    print(f"Units: {data.get('units', [])}")


def cmd_advance(args):
    """Advance one phase."""
    print(f"Advancing phase...")
    data = _api("POST", "/api/pipeline/advance-phase", body={
        "project_path": args.project,
    })
    if "error" in data:
        print(f"\nERROR: {data['error']}")
        return
    phase = data.get("phase", "?")
    label = data.get("phase_label", phase)
    nxt = data.get("next_phase", "?")
    gate = data.get("result", {}).get("gate", {})
    retrying = data.get("retrying", False)

    print(f"\nPhase:  {label}")
    if retrying:
        print(f"RETRY:  {data.get('state', {}).get('last_error', 'Retrying...')}")
    if gate:
        print(f"Gate:   {gate.get('verdict', '?')}")
        for f in gate.get("chapter_failures", gate.get("failures", [])):
            print(f"  - {f}")
    print(f"Next:   {nxt}")

    # Show artifacts
    result = data.get("result", {})
    if "artifacts" in result:
        print(f"Artifacts: {result['artifacts']}")
    if "artifact" in result:
        print(f"Artifact:  {result['artifact']}")
    if "word_count" in result:
        print(f"Words:     {result['word_count']}")
    if "critics" in result:
        for c in result["critics"]:
            err = c.get("error", "")
            print(f"  {c.get('critic_type', '?')}: verdict={c.get('verdict', '?')} findings={c.get('located_findings', 0)} {'ERR: ' + err if err else 'OK'}")
    if "failures" in result:
        for f in result["failures"]:
            print(f"  FAILURE: {f}")

    # Show state status
    state = data.get("state", {})
    print(f"\nState:  {state.get('status', '?')}")
    if state.get("last_error"):
        print(f"Error:  {state['last_error']}")


def cmd_advance_all(args):
    """Auto-run all phases until complete or failed."""
    max_phases = 50
    for i in range(max_phases):
        print(f"\n{'='*60}")
        print(f"Phase {i+1}")
        print(f"{'='*60}")
        data = _api("POST", "/api/pipeline/advance-phase", body={
            "project_path": args.project,
        })
        if "error" in data:
            print(f"\nERROR: {data['error']}")
            break
        phase = data.get("phase", "?")
        label = data.get("phase_label", phase)
        gate = data.get("result", {}).get("gate", {})
        state = data.get("state", {})
        retrying = data.get("retrying", False)

        print(f"Phase:  {label}")
        if retrying:
            print(f"RETRY:  {state.get('last_error', 'Retrying...')}")
        if gate:
            print(f"Gate:   {gate.get('verdict', '?')}")
            for f in gate.get("chapter_failures", gate.get("failures", [])):
                print(f"  - {f}")

        result = data.get("result", {})
        if "critics" in result:
            for c in result["critics"]:
                err = c.get("error", "")
                print(f"  {c.get('critic_type', '?')}: verdict={c.get('verdict', '?')} findings={c.get('located_findings', 0)} {'ERR: ' + err if err else ''}")
        if "failures" in result:
            for f in result["failures"]:
                print(f"  FAILURE: {f}")
        if "word_count" in result:
            print(f"Words:   {result['word_count']}")

        status = state.get("status", "?")
        print(f"Status:  {status}")

        if status in ("complete", "failed"):
            print(f"\n{'='*60}")
            print(f"Pipeline {status.upper()}")
            if state.get("last_error"):
                print(f"Error: {state['last_error']}")
            break

        nxt = data.get("next_phase", "?")
        print(f"Next:    {nxt}")
    else:
        print(f"\nWARNING: Hit {max_phases} phase limit without completing.")


def cmd_reset(args):
    """Delete the run state (keeps artifacts on disk)."""
    _api("POST", "/api/pipeline/reset-run", body={"project_path": args.project})
    print("Run state deleted. Artifacts preserved.")


def cmd_outputs(args):
    """Show the output catalog."""
    data = _api("GET", "/api/pipeline/outputs", params={"project_path": args.project})
    for cat in data.get("categories", []):
        print(f"\n{cat['label']} ({cat['exists_count']}/{cat['count']}):")
        for e in cat["entries"]:
            status = f"{e['words']}w" if e.get("exists") and e.get("words") else ("exists" if e.get("exists") else "—")
            print(f"  {e['path']:50} {status}")


def cmd_read(args):
    """Read an artifact file."""
    data = _api("GET", "/api/pipeline/output-file", params={
        "project_path": args.project,
        "path": args.path,
    })
    if not data.get("exists"):
        print(f"File not found: {args.path}")
        return
    print(f"Path: {data['path']}  Words: {data.get('words', '?')}  Kind: {data.get('kind', '?')}")
    print("---")
    print(data["content"][:5000])
    if len(data["content"]) > 5000:
        print(f"\n... ({len(data['content'])} chars total, truncated)")


def cmd_critic_test(args):
    """Test one critic call directly (bypasses the pipeline)."""
    from app.pipeline.orchestrator import (
        load_run_state, _chapter_rel, _read_file, system_prompt_for,
        _with_instructions, _collect_critic_feedback,
    )
    from app.pipeline import critics as critics_mod, profile_context
    from app.pipeline.lint_suite import hash_chapter
    from app.pipeline.word_count import strip_artifacts
    from app.routers.pipeline import _resolve_call_model, _make_model_call
    from app.settings_store import get_writer_model, get_critic_model
    import asyncio

    project = args.project
    state = load_run_state(project)
    if not state:
        print("No run state. Start a run first.")
        return

    chapter = state.units[state.current_unit_index] if state.units else 1
    chapter_path = _chapter_rel(chapter, project)
    full_path = os.path.join(project, chapter_path)

    print(f"Chapter: {chapter}")
    print(f"Path:    {chapter_path}")
    print(f"Exists:  {os.path.isfile(full_path)}")

    if not os.path.isfile(full_path):
        print("Chapter file not found. Run the writer phase first.")
        return

    chash = hash_chapter(full_path)
    chapter_text = strip_artifacts(_read_file(chapter_path, project) or "")
    print(f"Hash:    {chash[:16]}...")
    print(f"Chars:   {len(chapter_text)}")

    # Test with the critic model
    c_key, c_model, c_base = _resolve_call_model(get_critic_model())
    print(f"\nCritic model: {c_model}")
    print(f"Critic base:  {c_base}")
    print(f"Key prefix:   {c_key[:8]}...")

    call = _make_model_call(c_key, c_model, c_base)

    ctype = args.critic_type or "show"
    system = critics_mod._SYSTEM_PROMPTS.get(ctype, critics_mod._SYSTEM_PROMPTS["show"])
    user = (
        f"chapter_hash: {chash}\n\n"
        f"--- CHAPTER ---\n{chapter_text}\n--- END CHAPTER ---\n\n"
        f"Review this chapter now. Begin your report with 'chapter_hash: {chash}', "
        f"include a ## Findings section with at least three located findings "
        f"(Line N + quoted span), then VERDICT."
    )

    total = len(system) + len(user)
    print(f"\nPrompt:  {total} chars ({ctype} critic)")
    print(f"Calling model...")

    async def _test():
        try:
            reply = await call(system, user)
            print(f"\nReply:   {len(reply)} chars")
            print("---")
            print(reply[:2000])
            if len(reply) > 2000:
                print(f"\n... ({len(reply)} chars total, truncated)")
        except Exception as e:
            print(f"\nERROR: {type(e).__name__}: {e}")

    asyncio.run(_test())


def main():
    parser = argparse.ArgumentParser(description="Open-Write Pipeline CLI")
    parser.add_argument("--api", default="http://localhost:8000", help="Backend API base URL")
    parser.add_argument("--direct", action="store_true", help="Call orchestrator directly (bypass sidecar)")
    sub = parser.add_subparsers(dest="command")

    # status
    p = sub.add_parser("status", help="Show run state")
    p.add_argument("project")

    # start
    p = sub.add_parser("start", help="Start a new run")
    p.add_argument("project")
    p.add_argument("--instructions", "-i", default="")

    # advance
    p = sub.add_parser("advance", help="Advance one phase")
    p.add_argument("project")

    # advance-all
    p = sub.add_parser("advance-all", help="Auto-run all phases")
    p.add_argument("project")

    # reset
    p = sub.add_parser("reset", help="Delete run state")
    p.add_argument("project")

    # outputs
    p = sub.add_parser("outputs", help="Show output catalog")
    p.add_argument("project")

    # read
    p = sub.add_parser("read", help="Read an artifact")
    p.add_argument("project")
    p.add_argument("path")

    # critic-test
    p = sub.add_parser("critic-test", help="Test one critic call")
    p.add_argument("project")
    p.add_argument("--critic-type", "-t", default="show")

    args = parser.parse_args()
    _CONFIG["api_base"] = args.api
    _CONFIG["direct"] = args.direct

    if not args.command:
        parser.print_help()
        return

    cmds = {
        "status": cmd_status,
        "start": cmd_start,
        "advance": cmd_advance,
        "advance-all": cmd_advance_all,
        "reset": cmd_reset,
        "outputs": cmd_outputs,
        "read": cmd_read,
        "critic-test": cmd_critic_test,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
