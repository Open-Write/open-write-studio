#!/usr/bin/env python3
"""
Page Count Tool for Screenplay
Estimates page count from Fountain files.

Usage:
    python tools/page_count.py                          # Count assembled screenplay
    python tools/page_count.py script/scenes/01_cold_open.fountain  # Count single scene
    python tools/page_count.py --all                    # Count all scenes individually + total
"""

import re
import sys
import os
import glob
import json

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(BASE_DIR, "state")


def count_fountain_pages(filepath):
    """Estimate page count from a Fountain file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return None, f"File not found: {filepath}"

    lines = content.split('\n')

    # Remove title page (everything before first scene heading)
    in_title_page = True
    scene_lines = []
    for line in lines:
        if in_title_page:
            if re.match(r'^(INT\.|EXT\.|#)', line.strip(), re.IGNORECASE):
                in_title_page = False
                scene_lines.append(line)
            continue
        scene_lines.append(line)

    if not scene_lines:
        return 0, "No scene content found"

    # Count effective "page lines"
    total_lines = 0
    page_breaks = 0

    for line in scene_lines:
        stripped = line.strip()

        # Page break
        if stripped == '===':
            page_breaks += 1
            continue

        # Empty line (minor spacing)
        if not stripped:
            total_lines += 0.3
            continue

        # Scene heading
        if re.match(r'^(INT\.|EXT\.)', stripped, re.IGNORECASE):
            total_lines += 2
            continue

        # Transition (FADE IN:, CUT TO:, FADE OUT.)
        if re.match(r'^(FADE|CUT|DISSOLVE)', stripped, re.IGNORECASE):
            total_lines += 1.5
            continue

        # Character name (centered, takes space)
        if re.match(r'^[A-Z][A-Z\s\.]+$', stripped) and len(stripped) < 40:
            total_lines += 1.5
            continue

        # Parenthetical
        if stripped.startswith('(') and stripped.endswith(')'):
            total_lines += 1
            continue

        # All other lines (dialogue, action)
        total_lines += 1

    # Standard screenplay: ~55 lines per page
    estimated_pages = (total_lines / 55.0) + page_breaks

    return round(estimated_pages, 1), None


def count_scene_dir(scene_dir):
    """Count all scenes in a directory."""
    pattern = os.path.join(scene_dir, '*.fountain')
    files = sorted(glob.glob(pattern))

    if not files:
        print(f"No .fountain files found in {scene_dir}")
        return None

    total = 0
    print(f"{'Scene':<50} {'Pages':>6}")
    print("-" * 58)

    for filepath in files:
        pages, err = count_fountain_pages(filepath)
        if err:
            print(f"{os.path.basename(filepath):<50} {'ERROR':>6}  ({err})")
        elif pages is not None:
            print(f"{os.path.basename(filepath):<50} {pages:>6.1f}")
            total += pages

    print("-" * 58)
    print(f"{'TOTAL':<50} {total:>6.1f}")

    return total


def update_project_state(total_pages):
    """Update current_page in project_state.json."""
    state_path = os.path.join(STATE_DIR, 'project_state.json')
    try:
        with open(state_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        state['current_page'] = total_pages
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
        print(f"\nUpdated project_state.json: current_page = {total_pages}")
    except Exception as e:
        print(f"\nCould not update project_state.json: {e}")


def main():
    args = sys.argv[1:]
    filepath = None

    i = 0
    while i < len(args):
        if args[i] == '--all':
            scene_dir = os.path.join(BASE_DIR, 'script', 'scenes')
            total = count_scene_dir(scene_dir)
            if total:
                update_project_state(total)
            return
        elif args[i].endswith('.fountain'):
            filepath = args[i]
        i += 1

    if filepath:
        pages, err = count_fountain_pages(filepath)
        if err:
            print(f"Error: {err}")
            sys.exit(1)
        print(f"{os.path.basename(filepath)}: {pages:.1f} pages")
    else:
        # Default: count assembled screenplay
        assembled = os.path.join(BASE_DIR, 'script', 'screenplay.fountain')
        if os.path.exists(assembled):
            pages, err = count_fountain_pages(assembled)
            if err:
                print(f"Error: {err}")
                sys.exit(1)
            print(f"screenplay.fountain: {pages:.1f} pages")
            update_project_state(pages)
        else:
            scene_dir = os.path.join(BASE_DIR, 'script', 'scenes')
            if os.path.exists(scene_dir):
                total = count_scene_dir(scene_dir)
                if total:
                    update_project_state(total)
            else:
                print("No script found. Run assemble_screenplay.py first or pass a file path.")
                sys.exit(1)


if __name__ == '__main__':
    main()
