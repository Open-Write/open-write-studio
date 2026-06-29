#!/usr/bin/env python3
"""
Episode Assembly Tool for TV Scripts
Assembles individual scene Fountain files into a single episode script.
Strips process artifacts, prevents duplicates, verifies counts.

Usage:
    python tools/episode_assemble.py --episode S01E01
    python tools/episode_assemble.py --episode S01E01 --title "Pattern Recognition" --author "Written by Creator Name"
    python tools/episode_assemble.py --episode S01E01 --order scenes_order.txt
    python tools/episode_assemble.py --verify --episode S01E01
"""

import os
import sys
import glob
import re
from word_count import strip_artifacts

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENES_BASE = os.path.join(BASE_DIR, "scripts", "scenes")
OUTPUT_BASE = os.path.join(BASE_DIR, "scripts")

DEFAULT_AUTHOR = "Written by [Creator Name]"


def parse_args():
    episode = None
    title = None
    author = DEFAULT_AUTHOR
    date = ""
    order_file = None
    verify_only = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--episode' and i + 1 < len(args):
            episode = args[i + 1]
            i += 2
        elif args[i] == '--title' and i + 1 < len(args):
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

    if not episode:
        print("Error: --episode is required (e.g., --episode S01E01)")
        sys.exit(1)

    if not title:
        title = episode

    return episode, title, author, date, order_file, verify_only


def get_scene_files(scene_dir, order_file=None):
    if order_file and os.path.exists(order_file):
        with open(order_file, 'r', encoding='utf-8') as f:
            filenames = [line.strip() for line in f if line.strip()]
        files = []
        for fn in filenames:
            path = os.path.join(scene_dir, fn)
            if os.path.exists(path):
                files.append(path)
            else:
                print(f"WARNING: Scene file not found: {fn}")
        return files
    else:
        pattern = os.path.join(scene_dir, "*.fountain")
        return sorted(glob.glob(pattern))


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
    episode, title, author, date, order_file, verify_only = parse_args()

    scene_dir = os.path.join(SCENES_BASE, episode)
    output_file = os.path.join(OUTPUT_BASE, f"{episode}.fountain")

    if not os.path.exists(scene_dir):
        print(f"Error: Scenes directory not found: {scene_dir}")
        print(f"Expected structure: scripts/scenes/{episode}/01_cold_open.fountain")
        sys.exit(1)

    files = get_scene_files(scene_dir, order_file)

    if not files:
        print(f"Error: No .fountain files found in {scene_dir}")
        sys.exit(1)

    if verify_only:
        print(f"Found {len(files)} scene files for {episode}:")
        for filepath in files:
            print(f"  {os.path.basename(filepath)}")
        sys.exit(0)

    title_page = f"""Title: {title}
Credit: {author}
Draft date: {date}
"""

    parts = [title_page.strip()]
    missing = []
    total_lines = 0

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
            total_lines += content.count('\n')

    if missing:
        print(f"WARNING: Missing scene files: {missing}")

    assembled = "\n\n".join(parts) + "\n"

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(assembled)

    line_count = assembled.count("\n")
    scene_count = len(parts) - 1
    estimated_pages = round(line_count / 55.0, 1)

    print(f"{'='*60}")
    print(f"EPISODE ASSEMBLY: {episode}")
    print(f"{'='*60}")
    print(f"  Scenes assembled: {scene_count}")
    print(f"  Total lines: {line_count}")
    print(f"  Estimated pages: {estimated_pages}")
    print(f"  Output: {output_file}")
    print(f"  Title: {title}")
    print(f"  Author: {author}")

    if missing:
        print(f"  WARNING: {len(missing)} missing scene(s)")

    return output_file


if __name__ == "__main__":
    main()
