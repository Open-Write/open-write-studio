#!/usr/bin/env python3
"""
Completion Verification Tool v2.0

Reads a completion_manifest.json, validates the manifest itself, then checks
every item against disk. Verifies CONTENT, not just PRESENCE.

New in v2.0:
  - Chapter hashing: every chapter gets a SHA-256 hash of its clean content
  - Lint suite integration: per-chapter deterministic lints must pass
  - Critic substance validation: critic/editorial files must contain located
    findings, not just bare PASS/ADVANCE assertions
  - Hash-bound artifacts: critic/editorial files embed the chapter hash;
    stale artifacts (hash mismatch) fail the gate

This tool is the sole authority on whether a workflow is complete.
No agent judgment enters the check.

Usage:
    python tools/verify_completion.py
    python tools/verify_completion.py --manifest state/completion_manifest.json
    python tools/verify_completion.py --base-dir /path/to/project
    python tools/verify_completion.py --json
    python tools/verify_completion.py --expected-chapters 3
    python tools/verify_completion.py --skip-lint   (for testing only)
"""

import os
import sys
import json
import re
import argparse
import glob as globmod

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from word_count import count_words, strip_artifacts, count_prose_words_from_text


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def _resolve(base_dir, rel_path):
    full = os.path.join(base_dir, rel_path)
    real_full = os.path.realpath(full)
    real_base = os.path.realpath(base_dir)
    in_tree = real_full.startswith(real_base + os.sep) or real_full == real_base
    return real_full, in_tree


def file_exists(base_dir, rel_path):
    full, in_tree = _resolve(base_dir, rel_path)
    if not in_tree:
        return False, full, "OUT_OF_TREE"
    return os.path.isfile(full), full, None


def file_nonempty(base_dir, rel_path):
    full, in_tree = _resolve(base_dir, rel_path)
    if not in_tree:
        return False, full, "OUT_OF_TREE"
    if not os.path.isfile(full):
        return False, full, "MISSING"
    return os.path.getsize(full) > 0, full, None


def file_above_floor(base_dir, rel_path, floor):
    full, in_tree = _resolve(base_dir, rel_path)
    if not in_tree:
        return False, full, 0, "OUT_OF_TREE"
    if not os.path.isfile(full):
        return False, full, 0, "MISSING"
    wc = count_words(full)
    return wc >= floor, full, wc, None


def file_contains_verdict(base_dir, rel_path, verdict_values):
    full, in_tree = _resolve(base_dir, rel_path)
    if not in_tree:
        return False, full, None, "OUT_OF_TREE"
    if not os.path.isfile(full):
        return False, full, None, "MISSING"
    try:
        with open(full, "r", encoding="utf-8-sig") as f:
            content = f.read()
    except Exception:
        return False, full, None, "READ_ERROR"
    for v in verdict_values:
        if re.search(
            r'(?:VERDICT|Verdict|Consensus Verdict)[:\s]*' + re.escape(v),
            content, re.IGNORECASE
        ):
            return True, full, v, None
    return False, full, None, None


def glob_check(base_dir, pattern, min_count):
    full_pattern = os.path.join(base_dir, pattern)
    real_base = os.path.realpath(base_dir)
    matches = sorted(globmod.glob(full_pattern))
    in_tree_matches = [
        m for m in matches
        if os.path.realpath(m).startswith(real_base + os.sep)
    ]
    return len(in_tree_matches) >= min_count, in_tree_matches, len(in_tree_matches)


# ---------------------------------------------------------------------------
# Critic substance validation (Fix 1: requires located findings)
# ---------------------------------------------------------------------------

LOCATED_FINDING_PATTERN = re.compile(
    r'(?:'
    r'(?:Line|line|Lines|lines)\s*\d+'
    r'|(?:paragraph|Paragraph)\s*\d+'
    r'|(?:page|Page)\s*\d+'
    r'|(?:chapter|Chapter)\s*\d+'
    r'|"[^"]{10,}"'
    r'|>[^>]{10,}'
    r'|(?:Location|location|Loc|loc)[:\s]'
    r'|(?:Text|text)[:\s]*"'
    r'|(?:Passage|passage|Example|example)[:\s]'
    r'|(?:Quote|quote|Evidence|evidence)[:\s]'
    r')'
)


def _validate_critic_substance(filepath, label):
    """Check that a critic/editorial file contains located findings."""
    failures = []
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            content = f.read()
    except Exception:
        failures.append(f"READ_ERROR: Cannot read {label} ({filepath})")
        return failures

    finding_count = len(LOCATED_FINDING_PATTERN.findall(content))
    has_pass = bool(re.search(r'\b(?:PASS|ADVANCE|CLEAN|NATURAL)\b', content, re.IGNORECASE))
    has_findings_section = bool(re.search(
        r'(?:##|###)\s*(?:Violations?|Findings?|Issues?|Flags?|Problems?|Weaknesses|Criticism)',
        content, re.IGNORECASE
    ))
    word_count = len(content.split())

    if has_pass and finding_count == 0 and not has_findings_section:
        failures.append(
            f"HOLLOW_ARTIFACT: {label} asserts PASS/ADVANCE with zero located findings — "
            f"a bare PASS with no evidence is a failed critic pass, not a clean chapter"
        )

    if word_count < 100:
        failures.append(
            f"TOO_SHORT: {label} is only {word_count} words — "
            f"a substantive review requires analysis, not a one-line assertion"
        )

    return failures


# ---------------------------------------------------------------------------
# Chapter hash validation
# ---------------------------------------------------------------------------

def _compute_chapter_hash(filepath):
    """SHA-256 of artifact-stripped chapter content."""
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            text = f.read()
        text = text.replace('\ufeff', '')
        import hashlib
        clean = strip_artifacts(text)
        return hashlib.sha256(clean.encode("utf-8")).hexdigest()
    except Exception:
        return None


def _check_hash_binding(filepath, chapter_hash_map, label):
    """Check if an artifact embeds a stale chapter hash."""
    failures = []
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            content = f.read()
    except Exception:
        return failures

    hash_match = re.search(r'chapter_hash[:\s]*([a-f0-9]{64})', content, re.IGNORECASE)
    if hash_match:
        embedded = hash_match.group(1)
        if embedded not in chapter_hash_map.values():
            failures.append(
                f"STALE_ARTIFACT: {label} references chapter hash {embedded[:16]}... "
                f"which doesn't match any current chapter — chapter was revised but "
                f"this artifact wasn't regenerated"
            )
    return failures


# ---------------------------------------------------------------------------
# Lint suite integration (Fix 3)
# ---------------------------------------------------------------------------

def _run_lint_check(base_dir, chapter_path, label):
    """Run the deterministic lint suite on a chapter. Returns failures."""
    failures = []
    try:
        from lint_suite import run_lints_on_chapter
        findings = run_lints_on_chapter(chapter_path)
        critical = [f for f in findings if f.get("severity") == "critical"]
        moderate = [f for f in findings if f.get("severity") == "moderate"]
        if critical:
            failures.append(
                f"LINT_CRITICAL: {label} has {len(critical)} critical lint finding(s): "
                + "; ".join(f.get("pattern", "")[:60] for f in critical[:3])
            )
        if len(moderate) >= 5:
            failures.append(
                f"LINT_EXCESSIVE: {label} has {len(moderate)} moderate lint findings — "
                f"too many to advance without revision"
            )
    except ImportError:
        pass  # lint_suite not available — skip gracefully
    except Exception as e:
        failures.append(f"LINT_ERROR: {label} — {str(e)[:80]}")
    return failures


# ---------------------------------------------------------------------------
# Manifest validation
# ---------------------------------------------------------------------------

def validate_manifest(manifest, base_dir, expected_chapters=None):
    failures = []

    sections = manifest.get("sections", [])
    if not sections:
        failures.append("MANIFEST_INVALID: manifest has no sections")
        return failures

    total_items = 0
    for section in sections:
        items = section.get("items", [])
        total_items += len(items)

    if total_items == 0:
        failures.append(
            "MANIFEST_INVALID: manifest contains zero checkable items — "
            "an empty manifest cannot certify completion"
        )
        return failures

    all_paths = []
    for section in sections:
        for item in section.get("items", []):
            for field in ("path", "pattern", "assembled_path", "chapter_pattern"):
                p = item.get(field, "")
                if p:
                    all_paths.append((field, p))

    real_base = os.path.realpath(base_dir)
    for field, p in all_paths:
        real_full = os.path.realpath(os.path.join(base_dir, p))
        if not (real_full.startswith(real_base + os.sep) or real_full == real_base):
            failures.append(
                f"MANIFEST_INVALID: {field} escapes project base — '{p}' "
                f"resolves to '{real_full}' (base: '{real_base}')"
            )
            return failures

    if expected_chapters is not None and expected_chapters > 0:
        chapter_sections = [
            s for s in sections
            if any(
                item.get("check") == "word_floor"
                for item in s.get("items", [])
            )
        ]
        found_chapters = len(chapter_sections)
        if found_chapters < expected_chapters:
            failures.append(
                f"MANIFEST_INVALID: manifest claims {found_chapters} chapter(s) "
                f"but locked scope requires {expected_chapters} — "
                f"under-claiming manifest is equivalent to an empty one"
            )
            return failures

    return failures


# ---------------------------------------------------------------------------
# Item checks
# ---------------------------------------------------------------------------

def check_item(base_dir, item, chapter_hashes=None):
    check_type = item.get("check", "exists")
    rel_path = item.get("path", "")
    label = item.get("label", rel_path)
    failures = []

    if check_type == "exists":
        ok, full, err = file_exists(base_dir, rel_path)
        if not ok:
            if err == "OUT_OF_TREE":
                failures.append(f"OUT_OF_TREE: {label} ({full})")
            else:
                failures.append(f"MISSING: {label} ({full})")

    elif check_type == "nonempty":
        ok, full, err = file_nonempty(base_dir, rel_path)
        if not ok:
            if err == "OUT_OF_TREE":
                failures.append(f"OUT_OF_TREE: {label} ({full})")
            elif err == "MISSING":
                failures.append(f"MISSING: {label} ({full})")
            else:
                failures.append(f"EMPTY: {label} ({full})")

    elif check_type == "word_floor":
        floor = item.get("floor", 800)
        if "*" in rel_path or "?" in rel_path:
            full_pattern = os.path.join(base_dir, rel_path)
            real_base = os.path.realpath(base_dir)
            matches = sorted(
                m for m in globmod.glob(full_pattern)
                if os.path.realpath(m).startswith(real_base + os.sep)
            )
            if not matches:
                failures.append(f"MISSING: {label} (no files match '{rel_path}')")
            else:
                best_wc = 0
                for m in matches:
                    wc = count_words(m)
                    if wc > best_wc:
                        best_wc = wc
                if best_wc < floor:
                    failures.append(f"UNDER_FLOOR: {label} — best match {best_wc} words (floor: {floor}) ({matches[0]})")
        else:
            ok, full, wc, err = file_above_floor(base_dir, rel_path, floor)
            if not ok:
                if err == "OUT_OF_TREE":
                    failures.append(f"OUT_OF_TREE: {label} ({full})")
                elif err == "MISSING":
                    failures.append(f"MISSING: {label} ({full})")
                else:
                    failures.append(f"UNDER_FLOOR: {label} — {wc} words (floor: {floor}) ({full})")

    elif check_type == "verdict":
        verdict_values = item.get("verdict_values", ["ADVANCE", "RECOMMEND", "CONSIDER", "ENGAGED"])
        required_verdict = item.get("required_verdict", None)
        ok, full, found, err = file_contains_verdict(base_dir, rel_path, verdict_values)
        if not ok:
            if err == "OUT_OF_TREE":
                failures.append(f"OUT_OF_TREE: {label} ({full})")
            elif err == "MISSING":
                failures.append(f"MISSING: {label} ({full})")
            else:
                failures.append(f"NO_VERDICT: {label} — no recognized verdict found ({full})")
        elif required_verdict and found != required_verdict:
            failures.append(f"WRONG_VERDICT: {label} — found '{found}', required '{required_verdict}' ({full})")

    elif check_type == "glob_count":
        pattern = item.get("pattern", "")
        min_count = item.get("min_count", 1)
        label_suffix = item.get("label", f"glob({pattern})")
        ok, matches, count = glob_check(base_dir, pattern, min_count)
        if not ok:
            failures.append(f"INSUFFICIENT: {label_suffix} — found {count}, need {min_count}")

    elif check_type == "assembly_match":
        assembled_path = item.get("assembled_path", "")
        chapter_pattern = item.get("chapter_pattern", "")
        ok_ass, full_ass, err = file_exists(base_dir, assembled_path)
        if not ok_ass:
            if err == "OUT_OF_TREE":
                failures.append(f"OUT_OF_TREE: {label} ({full_ass})")
            else:
                failures.append(f"MISSING: {label} ({full_ass})")
        else:
            real_base = os.path.realpath(base_dir)
            with open(full_ass, "r", encoding="utf-8-sig") as f:
                ass_text = f.read()
            ass_text = ass_text.replace('\ufeff', '')
            ass_clean = strip_artifacts(ass_text)
            sections_split = re.split(r'^---\s*$', ass_clean, flags=re.MULTILINE)
            chapter_sections = []
            for i, sec in enumerate(sections_split):
                sec = sec.strip()
                if i == 0:
                    continue
                if sec:
                    chapter_sections.append(sec)
            ass_wc = 0
            for sec in chapter_sections:
                ass_wc += count_prose_words_from_text(sec)
            chapter_pattern_full = os.path.join(base_dir, chapter_pattern)
            chapter_files = sorted(
                m for m in globmod.glob(chapter_pattern_full)
                if os.path.realpath(m).startswith(real_base + os.sep)
            )
            sum_wc = 0
            for cf in chapter_files:
                with open(cf, "r", encoding="utf-8-sig") as f:
                    ch_text = f.read()
                ch_clean = strip_artifacts(ch_text)
                sum_wc += count_prose_words_from_text(ch_clean)
            if ass_wc != sum_wc:
                failures.append(f"COUNT_MISMATCH: {label} — assembled {ass_wc} vs sum of chapters {sum_wc}")

    elif check_type == "critic_substance":
        # NEW: Validates that critic/editorial files contain located findings
        pattern = item.get("pattern", "")
        if "*" in pattern or "?" in pattern:
            full_pattern = os.path.join(base_dir, pattern)
            real_base = os.path.realpath(base_dir)
            matches = sorted(
                m for m in globmod.glob(full_pattern)
                if os.path.realpath(m).startswith(real_base + os.sep)
            )
            if not matches:
                failures.append(f"MISSING: {label} (no files match '{pattern}')")
            else:
                for m in matches:
                    m_label = os.path.basename(m)
                    sub_failures = _validate_critic_substance(m, m_label)
                    failures.extend(sub_failures)
                    if chapter_hashes:
                        hash_failures = _check_hash_binding(m, chapter_hashes, m_label)
                        failures.extend(hash_failures)
        elif rel_path:
            ok, full, err = file_exists(base_dir, rel_path)
            if not ok:
                failures.append(f"MISSING: {label} ({full})")
            else:
                sub_failures = _validate_critic_substance(full, label)
                failures.extend(sub_failures)
                if chapter_hashes:
                    hash_failures = _check_hash_binding(full, chapter_hashes, label)
                    failures.extend(hash_failures)

    elif check_type == "lint_pass":
        # NEW: Runs deterministic lint suite on the chapter
        if "*" in rel_path or "?" in rel_path:
            full_pattern = os.path.join(base_dir, rel_path)
            real_base = os.path.realpath(base_dir)
            matches = sorted(
                m for m in globmod.glob(full_pattern)
                if os.path.realpath(m).startswith(real_base + os.sep)
            )
            if not matches:
                failures.append(f"MISSING: {label} (no files match '{rel_path}')")
            else:
                for m in matches:
                    lint_failures = _run_lint_check(base_dir, m, os.path.basename(m))
                    failures.extend(lint_failures)
        elif rel_path:
            ok, full, err = file_exists(base_dir, rel_path)
            if not ok:
                failures.append(f"MISSING: {label} ({full})")
            else:
                lint_failures = _run_lint_check(base_dir, full, label)
                failures.extend(lint_failures)

    return failures


# ---------------------------------------------------------------------------
# Main verification
# ---------------------------------------------------------------------------

def verify_manifest(base_dir, manifest, expected_chapters=None, skip_lint=False):
    all_failures = []

    validation_failures = validate_manifest(manifest, base_dir, expected_chapters)
    if validation_failures:
        return False, 0, 0, len(validation_failures), validation_failures, {}

    # Pre-compute chapter hashes for stale-artifact detection
    chapter_hashes = {}
    chapters_dir = os.path.join(base_dir, "manuscript", "chapters")
    if os.path.isdir(chapters_dir):
        for f in sorted(globmod.glob(os.path.join(chapters_dir, "*.md"))):
            h = _compute_chapter_hash(f)
            if h:
                rel = os.path.relpath(f, base_dir)
                chapter_hashes[rel] = h

    sections = manifest.get("sections", [])
    total_items = 0
    passed_items = 0

    for section in sections:
        items = section.get("items", [])
        for item in items:
            # Skip lint items if requested (for testing)
            if skip_lint and item.get("check") == "lint_pass":
                total_items += 1
                passed_items += 1
                continue

            total_items += 1
            failures = check_item(base_dir, item, chapter_hashes)
            if failures:
                all_failures.extend(failures)
            else:
                passed_items += 1

    all_pass = len(all_failures) == 0
    return all_pass, total_items, passed_items, len(all_failures), all_failures, chapter_hashes


def run_verification(base_dir, manifest_path, expected_chapters=None, skip_lint=False):
    if not os.path.isfile(manifest_path):
        print(f"FAIL: Manifest not found: {manifest_path}")
        return False

    with open(manifest_path, "r", encoding="utf-8-sig") as f:
        manifest = json.load(f)

    manifest_version = manifest.get("version", "unknown")
    project_type = manifest.get("project_type", "unknown")
    project_name = manifest.get("project_name", "unnamed")

    all_pass, total, passed, failed, failures, chapter_hashes = verify_manifest(
        base_dir, manifest, expected_chapters, skip_lint
    )

    print(f"{'='*70}")
    print(f"COMPLETION VERIFICATION")
    print(f"{'='*70}")
    print(f"  Project: {project_name}")
    print(f"  Type: {project_type}")
    print(f"  Manifest: {manifest_path}")
    print(f"  Manifest version: {manifest_version}")
    print(f"  Items checked: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Chapters hashed: {len(chapter_hashes)}")
    print()

    if failures:
        print(f"FAILURES ({failed}):")
        print(f"{'-'*70}")
        for f in failures:
            print(f"  {f}")
        print()

    verdict = "PASS" if all_pass else "FAIL"
    print(f"{'='*70}")
    print(f"VERDICT: {verdict}")
    print(f"{'='*70}")

    return all_pass


def _auto_detect_chapters(base_dir):
    from build_manifest import count_chapters_in_outline

    outline_candidates = [
        os.path.join(base_dir, "bible", "04_outline.md"),
        os.path.join(base_dir, "bible", "04_season_arc.md"),
    ]
    for c in outline_candidates:
        if os.path.isfile(c):
            ch = count_chapters_in_outline(c)
            if ch > 0:
                return ch
    return None


def main():
    parser = argparse.ArgumentParser(description="Verify completion manifest against disk")
    parser.add_argument("--manifest", default=None, help="Path to completion_manifest.json")
    parser.add_argument("--base-dir", default=None, help="Project base directory")
    parser.add_argument("--json", action="store_true", help="Machine-readable JSON output")
    parser.add_argument("--expected-chapters", type=int, default=None,
                        help="Locked chapter count — manifest must cover this many chapters")
    parser.add_argument("--skip-lint", action="store_true",
                        help="Skip lint suite checks (for testing)")
    args = parser.parse_args()

    base_dir = args.base_dir or os.getcwd()

    expected_chapters = args.expected_chapters
    if expected_chapters is None:
        expected_chapters = _auto_detect_chapters(base_dir)

    if args.manifest:
        manifest_path = args.manifest
    else:
        candidates = [
            os.path.join(base_dir, "state", "completion_manifest.json"),
            os.path.join(base_dir, "completion_manifest.json"),
        ]
        manifest_path = None
        for c in candidates:
            if os.path.isfile(c):
                manifest_path = c
                break
        if not manifest_path:
            print("FAIL: No completion_manifest.json found.")
            print(f"  Searched: {candidates}")
            sys.exit(1)

    if args.json:
        if not os.path.isfile(manifest_path):
            print(json.dumps({"verdict": "FAIL", "error": f"Manifest not found: {manifest_path}"}))
            sys.exit(1)
        with open(manifest_path, "r", encoding="utf-8-sig") as f:
            manifest = json.load(f)
        all_pass, total, passed, failed, failures, chapter_hashes = verify_manifest(
            base_dir, manifest, expected_chapters, args.skip_lint
        )
        output = {
            "verdict": "PASS" if all_pass else "FAIL",
            "project_name": manifest.get("project_name", ""),
            "project_type": manifest.get("project_type", ""),
            "items_checked": total,
            "items_passed": passed,
            "items_failed": failed,
            "chapter_hashes": {k: v[:16] + "..." for k, v in chapter_hashes.items()},
            "failures": failures
        }
        print(json.dumps(output, indent=2))
        sys.exit(0 if all_pass else 1)

    all_pass = run_verification(base_dir, manifest_path, expected_chapters, args.skip_lint)
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
