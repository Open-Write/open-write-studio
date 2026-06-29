#!/usr/bin/env python3
"""
Assemble screenplay from individual scene Fountain files.
Reads all .fountain files from script/scenes/ in sorted order,
prepends a title page, and writes the assembled screenplay.

Usage:
    python script/assemble_screenplay.py                           # Default assembly
    python script/assemble_screenplay.py --title "My Film" --author "Written by Author Name"
"""

import os
import sys
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
SCENES_DIR = os.path.join(SCRIPT_DIR, "scenes")
OUTPUT_FILE = os.path.join(SCRIPT_DIR, "screenplay.fountain")

DEFAULT_TITLE = "Screenplay"
DEFAULT_AUTHOR = "Original Screenplay by [Author Name]"
DEFAULT_DATE = "2025-01-01"


def parse_args():
    """Parse command line arguments."""
    title = DEFAULT_TITLE
    author = DEFAULT_AUTHOR
    date = DEFAULT_DATE
    order_file = None

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
        else:
            i += 1

    return title, author, date, order_file


def get_scene_files(order_file=None):
    """Get scene files in order. If order_file is provided, use it. Otherwise, sort by filename."""
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
        return sorted(glob.glob(pattern))


def main():
    title, author, date, order_file = parse_args()

    if not os.path.exists(SCENES_DIR):
        print(f"Error: Scenes directory not found: {SCENES_DIR}")
        sys.exit(1)

    files = get_scene_files(order_file)

    if not files:
        print(f"Error: No .fountain files found in {SCENES_DIR}")
        sys.exit(1)

    # Build title page
    title_page = f"""Title: {title}
Credit: {author}
Draft date: {date}
"""

    # Read all scene files
    parts = [title_page.strip()]
    missing = []
    for filepath in files:
        if not os.path.exists(filepath):
            missing.append(os.path.basename(filepath))
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
        # Strip any duplicate title pages from scene files
        if content.startswith("Title:"):
            lines = content.split('\n')
            body_start = 0
            for j, line in enumerate(lines):
                if line.strip() == '' and j > 0:
                    body_start = j + 1
                    break
            content = '\n'.join(lines[body_start:]).strip()
        if content:
            parts.append(content)

    if missing:
        print(f"WARNING: Missing scene files: {missing}")

    # Join with double newline (one blank line between scenes)
    assembled = "\n\n".join(parts) + "\n"

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(assembled)

    # Report stats
    line_count = assembled.count("\n")
    scene_count = len(parts) - 1  # -1 for title page
    print(f"Assembled screenplay written to: {OUTPUT_FILE}")
    print(f"Total lines: {line_count}")
    print(f"Scenes assembled: {scene_count}")
    print(f"Title: {title}")
    print(f"Author: {author}")


if __name__ == "__main__":
    main()
