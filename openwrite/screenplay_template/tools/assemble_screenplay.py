#!/usr/bin/env python3
"""
Assemble screenplay from individual scene Fountain files.
Reads all .fountain files from script/scenes/ in sorted order,
strips process artifacts, prevents duplicates, verifies counts.

Usage:
    python tools/assemble_screenplay.py                           # Default assembly
    python tools/assemble_screenplay.py --title "My Film" --author "Written by Author Name"
    python tools/assemble_screenplay.py --verify
"""

import os
import sys
import glob
import re
from word_count import strip_artifacts

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENES_DIR = os.path.join(BASE_DIR, "script", "scenes")
OUTPUT_FILE = os.path.join(BASE_DIR, "script", "screenplay.fountain")

DEFAULT_TITLE = "Screenplay"
DEFAULT_AUTHOR = "Original Screenplay by [Author Name]"
DEFAULT_DATE = "2025-01-01"


def parse_args():
    title = DEFAULT_TITLE
    author = DEFAULT_AUTHOR
    date = DEFAULT_DATE
    order_file = None
    verify_only = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--title' and i + 1 < len(args):
            title = args[i + 1]
            i += 2
        elif args[i] == '--author' and i + 1 < len(args):
            author = args[i + 1]
            i += 2
        elif args[i] == '--date' and i + 1 < len(args):
            date = args[i + 1]
            i += 2
        elif args[i] == '--order' and i + 1 < len(args):
            order_file = args[i + 1]
            i += 2
        elif args[i] == '--verify':
            verify_only = True
            i += 1
        else:
            i += 1

    return title, author, date, order_file, verify_only


def get_scene_files(order_file=None):
    if order_file and os.path.exists(order_file):
        with open(order_file, 'r', encoding='utf-8') as f:
            filenames = [line.strip() for line in f if line.strip()]
        files = []
        for fn in filenames:
            path = os.path.join(SCENES_DIR, fn)
            if os.path.exists(path):
                files.append(path)
            else:
                print(f"WARNING: Scene file not found: {fn}")
        return files
    else:
        pattern = os.path.join(SCENES_DIR, "*.fountain")
        all_files = sorted(glob.glob(pattern))

        by_number = {}
        for filepath in all_files:
            basename = os.path.basename(filepath)
            match = re.match(r'^(\d+)([a-z]*)', basename)
            if match:
                num = int(match.group(1))
                suffix = match.group(2) or ''
                key = (num, suffix)
                if key not in by_number:
                    by_number[key] = []
                by_number[key].append(filepath)

        result = []
        for key in sorted(by_number.keys()):
            candidates = by_number[key]
            if len(candidates) == 1:
                result.append(candidates[0])
            else:
                candidates.sort(key=lambda f: os.path.getmtime(f), reverse=True)
                winner = candidates[0]
                for loser in candidates[1:]:
                    print(f"  NOTE: Skipping duplicate scene {key}: {os.path.basename(loser)} (keeping {os.path.basename(winner)})")
                result.append(winner)

        return result


def strip_title_page(content):
    if content.startswith("Title:"):
        lines = content.split('\n')
        body_start = 0
        for j, line in enumerate(lines):
            if line.strip() == '' and j > 0:
                body_start = j + 1
                break
        content = '\n'.join(lines[body_start:]).strip()
    return content


def main():
    title, author, date, order_file, verify_only = parse_args()

    if not os.path.exists(SCENES_DIR):
        print(f"Error: Scenes directory not found: {SCENES_DIR}")
        sys.exit(1)

    files = get_scene_files(order_file)

    if not files:
        print(f"Error: No .fountain files found in {SCENES_DIR}")
        sys.exit(1)

    if verify_only:
        print(f"Found {len(files)} scene files:")
        for filepath in files:
            print(f"  {os.path.basename(filepath)}")
        sys.exit(0)

    title_page = f"""Title: {title}
Credit: {author}
Draft date: {date}
"""

    parts = [title_page.strip()]
    missing = []
    for filepath in files:
        if not os.path.exists(filepath):
            missing.append(os.path.basename(filepath))
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
        content = strip_title_page(content)
        content = strip_artifacts(content)
        if content:
            parts.append(content)

    if missing:
        print(f"WARNING: Missing scene files: {missing}")

    assembled = "\n\n".join(parts) + "\n"

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(assembled)

    line_count = assembled.count("\n")
    scene_count = len(parts) - 1
    print(f"{'='*60}")
    print(f"ASSEMBLY COMPLETE")
    print(f"{'='*60}")
    print(f"  Output: {OUTPUT_FILE}")
    print(f"  Scenes assembled: {scene_count}")
    print(f"  Total lines: {line_count}")
    print(f"  Title: {title}")
    print(f"  Author: {author}")
    if missing:
        print(f"  WARNING: {len(missing)} missing scene(s)")


if __name__ == "__main__":
    main()
