"""
app.harness — the orchestration layer (The Architect protocols, ported).

Goal -> Planner -> Router -> Runner -> Verifier -> Reporter, sitting ABOVE the
existing Open-Write pipeline. The pipeline's deterministic completion gate is
reused as the writing-domain verifier.
"""
