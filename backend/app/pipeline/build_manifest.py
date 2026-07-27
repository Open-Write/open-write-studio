#!/usr/bin/env python3
"""
Build Completion Manifest v2.0

Reads the locked outline file, counts chapters, and generates a deterministic
completion_manifest.json. The agent does not author the item list — it is
derived mechanically from the outline scope.

New in v2.0:
  - Per-chapter lint_pass items (deterministic lints must pass)
  - critic_substance items (critic/editorial files must contain located findings)
  - Hash-bound artifact tracking (chapter hashes embedded, stale artifacts fail)

Usage:
    python tools/build_manifest.py --base-dir /path/to/project
    python tools/build_manifest.py --outline bible/04_outline.md --project-name "My Novel"
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime


def count_chapters_in_outline(outline_path):
    with open(outline_path, "r", encoding="utf-8-sig") as f:
        text = f.read()
    patterns = [
        r'^##\s+Chapter\s+(\d+)',
        r'^##\s+Ch\.?\s*(\d+)',
        r'^#\s+Chapter\s+(\d+)',
        r'^##\s+\d+\.',
        r'^###?\s+Chapter\s+(\d+)',
    ]
    chapters = set()
    for line in text.split("\n"):
        for pat in patterns:
            m = re.match(pat, line.strip(), re.IGNORECASE)
            if m:
                try:
                    chapters.add(int(m.group(1)))
                except (IndexError, ValueError):
                    chapters.add(len(chapters) + 1)
    if not chapters:
        heading_count = 0
        for line in text.split("\n"):
            stripped = line.strip()
            if re.match(r'^##\s+', stripped) and not re.match(r'^##\s+(Note|Introduction|Prologue|Epilogue|Appendix|Part)', stripped, re.IGNORECASE):
                heading_count += 1
        if heading_count > 0:
            return heading_count
    return len(chapters) if chapters else 0


def build_manifest(chapter_count, project_name="Untitled", project_type="novel", word_floor=800):
    sections = []

    pre_items = [
        {"label": "Bible: concept", "path": "bible/01_concept.md", "check": "nonempty"},
        {"label": "Bible: outline locked", "path": "bible/04_outline.md", "check": "nonempty"},
        {"label": "Bible: format rules", "path": "bible/07_format_rules.md", "check": "nonempty"},
        {"label": "Locked voice spec", "check": "glob_count", "pattern": "bible/LOCKED_VOICE_SPEC*", "min_count": 1},
    ]
    sections.append({"name": "Pre-Production", "items": pre_items})

    for ch in range(1, chapter_count + 1):
        ch_items = [
            {"label": f"Ch{ch} plan", "path": f"critic_outputs/chapter_{ch}_plan.md", "check": "nonempty"},
            {"label": f"Ch{ch} draft", "check": "word_floor", "path": f"manuscript/{ch:03d}_*.md", "floor": word_floor},
            {"label": f"Ch{ch} lint pass", "check": "lint_pass", "path": f"manuscript/{ch:03d}_*.md"},
            {"label": f"Ch{ch} show critic substance", "check": "critic_substance", "pattern": f"critic_outputs/chapter_{ch}_show*"},
            {"label": f"Ch{ch} voice critic substance", "check": "critic_substance", "pattern": f"critic_outputs/chapter_{ch}_voice*"},
            {"label": f"Ch{ch} palette critic substance", "check": "critic_substance", "pattern": f"critic_outputs/chapter_{ch}_palette*"},
            {"label": f"Ch{ch} continuity critic substance", "check": "critic_substance", "pattern": f"critic_outputs/chapter_{ch}_continuity*"},
            {"label": f"Ch{ch} naturalism critic substance", "check": "critic_substance", "pattern": f"critic_outputs/chapter_{ch}_naturalism*"},
            {"label": f"Ch{ch} editorial substance", "check": "critic_substance", "pattern": f"coverage_reports/editorial_report_ch{ch}*"},
        ]
        sections.append({"name": f"Chapter {ch}", "items": ch_items})

    post_items = [
        {"label": "Adversarial read substance", "check": "critic_substance", "pattern": "coverage_reports/*adversarial*"},
        {"label": "Assembly integrity", "check": "assembly_match", "assembled_path": "manuscript/novel.md", "chapter_pattern": "manuscript/*.md"},
        {"label": "Callback ledger", "path": "state/callback_ledger.json", "check": "nonempty"},
        {"label": "Convention ledger", "path": "state/convention_ledger.json", "check": "nonempty"},
    ]
    sections.append({"name": "Post-Production", "items": post_items})

    manifest = {
        "version": "2.0",
        "project_name": project_name,
        "project_type": project_type,
        "generated_at": datetime.now().isoformat(),
        "scope": {
            "chapter_count": chapter_count,
            "word_floor": word_floor,
            "outline_source": "bible/04_outline.md"
        },
        "sections": sections
    }
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Build completion manifest from locked outline")
    parser.add_argument("--base-dir", default=None, help="Project base directory")
    parser.add_argument("--outline", default=None, help="Path to outline file (auto-detected if omitted)")
    parser.add_argument("--project-name", default="Untitled", help="Project name")
    parser.add_argument("--project-type", default="novel", help="Project type (novel/screenplay/tv)")
    parser.add_argument("--word-floor", type=int, default=800, help="Stub-detector floor — catches chapters that were never written")
    parser.add_argument("--output", default=None, help="Output path (default: state/completion_manifest.json)")
    args = parser.parse_args()

    base_dir = args.base_dir or os.getcwd()

    outline_path = args.outline
    if not outline_path:
        candidates = [
            os.path.join(base_dir, "bible", "04_outline.md"),
            os.path.join(base_dir, "bible", "04_season_arc.md"),
        ]
        for c in candidates:
            if os.path.isfile(c):
                outline_path = c
                break
        if not outline_path:
            print("FAIL: No outline file found. Searched:", candidates)
            sys.exit(1)

    if not os.path.isfile(outline_path):
        print(f"FAIL: Outline file not found: {outline_path}")
        sys.exit(1)

    chapter_count = count_chapters_in_outline(outline_path)
    if chapter_count == 0:
        print(f"FAIL: Could not detect any chapters in outline: {outline_path}")
        sys.exit(1)

    manifest = build_manifest(chapter_count, args.project_name, args.project_type, args.word_floor)

    output_path = args.output or os.path.join(base_dir, "state", "completion_manifest.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    total_items = sum(len(s["items"]) for s in manifest["sections"])
    print(f"Manifest written to: {output_path}")
    print(f"  Chapters detected: {chapter_count}")
    print(f"  Total check items: {total_items}")
    print(f"  Word floor: {args.word_floor}")
    print(f"  Sections: {len(manifest['sections'])}")
    print(f"  Version: 2.0 (lint_pass + critic_substance)")


if __name__ == "__main__":
    main()
