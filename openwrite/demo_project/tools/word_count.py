#!/usr/bin/env python3
"""
Verified Word Count Tool
Counts words in manuscript files. Used by the pipeline for verified word counts.
Every word count in the pipeline comes from this tool — never from memory.

Supports:
  - Novel: counts words in manuscript/chapters/*.md
  - Screenplay: counts words in script/scenes/*.fountain
  - Single file: counts words in one specified file

Usage:
    python tools/word_count.py                              # Auto-detect project type
    python tools/word_count.py --file manuscript/chapters/01_chapter.md
    python tools/word_count.py --floor 800                  # Flag stub chapters
    python tools/word_count.py --json                       # Machine-readable output
"""

import os
import sys
import json
import glob
import re
import argparse


def count_prose_words(filepath):
    with open(filepath, "r", encoding="utf-8-sig") as f:
        text = f.read()
    return _count_prose_text(text)


def _count_prose_text(text):
    lines = text.split("\n")
    word_count = 0
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("```"):
            continue
        if stripped.startswith("---"):
            continue
        word_count += len(stripped.split())
    return word_count


def count_fountain_words(filepath):
    with open(filepath, "r", encoding="utf-8-sig") as f:
        text = f.read()
    text = re.sub(r'^(INT\.|EXT\.).*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^(FADE|CUT|DISSOLVE).*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[A-Z][A-Z\s\.]+(\s*\(.*\))?$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\([^)]+\)\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^===\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^(END OF ACT|ACT \w+|COLD OPEN|TITLE SEQUENCE).*$', '', text, flags=re.MULTILINE)
    if text.startswith("Title:"):
        lines = text.split('\n')
        body_start = 0
        for j, line in enumerate(lines):
            if line.strip() == '' and j > 0:
                body_start = j + 1
                break
        text = '\n'.join(lines[body_start:])
    words = text.split()
    return len(words)


def count_words(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".fountain":
        return count_fountain_words(filepath)
    return count_prose_words(filepath)


def count_prose_words_from_text(text):
    return _count_prose_text(text)


ARTIFACT_PATTERNS = [
    (r'^\[Word count:?\s*\d+\s*words?\]\s*$', re.MULTILINE),
    (r'^\(Expanded\)\s*$', re.MULTILINE),
    (r'^\(Revised\)\s*$', re.MULTILINE),
    (r'^\(Cut\s*\d+%\)\s*$', re.MULTILINE),
    (r'^---\s*BEGIN\s+(?:CRITIC|EDITORIAL|RESUME|NOTES?|PROCESS)\s*---.*?^---\s*END\s+(?:CRITIC|EDITORIAL|RESUME|NOTES?|PROCESS)\s*---', re.MULTILINE | re.DOTALL),
    (r'^---\s*RESUME\s*---.*?^---\s*END\s*RESUME\s*---', re.MULTILINE | re.DOTALL),
    (r'^<!--\s*(?:critic|editorial|process|resume|notes?|word.?count).*?-->', re.MULTILINE | re.DOTALL),
    (r'^\*\*(?:Critic|Editorial|Process|Resume|Notes?)\*\*:.*$', re.MULTILINE),
    (r'^Stage \d+.*?completed.*$', re.MULTILINE),
    (r'^Pipeline status:.*$', re.MULTILINE),
    (r'^Verified:.*$', re.MULTILINE),
    (r'^ADVANCE\s*$', re.MULTILINE),
    (r'^COMPLETE\s*$', re.MULTILINE),
]


def strip_artifacts(content):
    for pattern, flags in ARTIFACT_PATTERNS:
        content = re.sub(pattern, '', content, flags=flags)
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip()


def count_stripped_prose_words(filepath):
    with open(filepath, "r", encoding="utf-8-sig") as f:
        text = f.read()
    clean = strip_artifacts(text)
    return _count_prose_text(clean)


def detect_project_type(base_dir):
    if os.path.exists(os.path.join(base_dir, "manuscript", "chapters")):
        return "novel"
    if os.path.exists(os.path.join(base_dir, "script", "scenes")):
        return "screenplay"
    if os.path.exists(os.path.join(base_dir, "scripts", "scenes")):
        return "tv"
    return None


def find_novel_chapters(base_dir):
    chapters_dir = os.path.join(base_dir, "manuscript", "chapters")
    if not os.path.exists(chapters_dir):
        return []
    files = glob.glob(os.path.join(chapters_dir, "*.md"))

    def sort_key(filepath):
        match = re.match(r"(\d+)", os.path.basename(filepath))
        return int(match.group(1)) if match else 0

    return sorted(files, key=sort_key)


def find_screenplay_scenes(base_dir):
    scenes_dir = os.path.join(base_dir, "script", "scenes")
    if not os.path.exists(scenes_dir):
        return []
    return sorted(glob.glob(os.path.join(scenes_dir, "*.fountain")))


def find_tv_episodes(base_dir):
    scripts_dir = os.path.join(base_dir, "scripts")
    if not os.path.exists(scripts_dir):
        return []
    pattern = os.path.join(scripts_dir, "S*.fountain")
    files = sorted(glob.glob(pattern))
    return [f for f in files if not os.path.basename(f).startswith("Season_")]


def main():
    parser = argparse.ArgumentParser(description="Verified word count for manuscripts")
    parser.add_argument("--file", default=None, help="Count a single file")
    parser.add_argument("--floor", type=int, default=0, help="Flag items below this word floor")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--base-dir", default=None, help="Project base directory")
    args = parser.parse_args()

    if args.file:
        filepath = args.file
        if not os.path.exists(filepath):
            print(f"Error: File not found: {filepath}")
            sys.exit(1)
        wc = count_words(filepath)
        print(f"{filepath}: {wc} words")
        if args.floor and wc < args.floor:
            print(f"  BELOW FLOOR ({args.floor} words)")
            sys.exit(1)
        sys.exit(0)

    base_dir = args.base_dir or os.getcwd()
    project_type = detect_project_type(base_dir)

    if not project_type:
        print("Error: Could not detect project type. Use --file to count a specific file.")
        sys.exit(1)

    results = []

    if project_type == "novel":
        files = find_novel_chapters(base_dir)
    elif project_type == "screenplay":
        files = find_screenplay_scenes(base_dir)
    elif project_type == "tv":
        files = find_tv_episodes(base_dir)

    for filepath in files:
        wc = count_words(filepath)
        results.append({"file": os.path.basename(filepath), "words": wc})

    if not results:
        print("No files found.")
        sys.exit(1)

    total = sum(r["words"] for r in results)
    below_floor = [r for r in results if args.floor and r["words"] < args.floor]

    if args.json:
        output = {
            "total_words": total,
            "file_count": len(results),
            "floor": args.floor,
            "below_floor_count": len(below_floor),
            "items": results
        }
        print(json.dumps(output, indent=2))
    else:
        label = "chapter" if project_type == "novel" else "scene" if project_type == "screenplay" else "episode"
        print(f"{'File':<50} {'Words':>8}")
        print("-" * 60)
        for r in results:
            flag = " BELOW FLOOR" if args.floor and r["words"] < args.floor else ""
            print(f"  {r['file']:<48} {r['words']:>8}{flag}")
        print("-" * 60)
        print(f"  {'TOTAL':<48} {total:>8}")
        print(f"\n  {label.title()}s: {len(results)}")
        if project_type == "novel":
            print(f"  Estimated pages: {total / 250:.1f}")

    if below_floor:
        print(f"\n  WARNING: {len(below_floor)} {label}(s) below {args.floor} word floor")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
