"""
app.pipeline — the Open-Write deterministic completion-gate toolchain.

These modules are ported verbatim (logic-for-logic) from the canonical
C:\\Open-Write\\tools\\ toolchain. They are the SOLE authority on whether an
Open-Write pipeline project is complete. No agent judgment enters the checks.

Public surface (import from `app.pipeline`):

  Word counting / artifact stripping
    - count_words, count_prose_words, count_prose_words_from_text
    - strip_artifacts, ARTIFACT_PATTERNS

  Manifest
    - build_manifest.build_manifest        (build the manifest dict)
    - build_manifest.count_chapters_in_outline

  Verification (sole PASS/FAIL authority)
    - verify_completion.verify_manifest    (returns all_pass, counts, failures, hashes)
    - verify_completion.validate_manifest

  Finalize (the gate; writes the bound COMPLETION_PASS certificate)
    - finalize.finalize                    (run the full gate, returns verdict dict)

  Lints
    - lints.run_all                        (the 6 finalize lints)
    - lint_suite.run_lints_on_chapter      (per-chapter deterministic lints)
    - lint_suite.run_full_lint_suite       (whole-project lint suite)

Import note: the agent (or any caller) may NEVER write COMPLETION_PASS.json
directly — only finalize.finalize() produces it, and it is bound to a SHA-256
of the normalized assembled manuscript so it cannot be copied between projects.
"""

# Eager import is safe — these modules use only the Python standard library.
from . import word_count, lints, lint_suite, build_manifest, verify_completion, finalize, critics

__all__ = [
    "word_count",
    "lints",
    "lint_suite",
    "build_manifest",
    "verify_completion",
    "finalize",
    "critics",
]
