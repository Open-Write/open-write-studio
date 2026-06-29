#!/usr/bin/env python3
"""
Page Count Tool for TV Scripts
Estimates page count from Fountain files.
TV standard: ~1 page per minute of screen time.

Usage:
    python tools/page_count.py                          # Count all assembled episodes
    python tools/page_count.py --episode S01E01         # Count single episode
    python tools/page_count.py --episode S01E01 --all   # Count all scenes in episode
    python tools/page_count.py scripts/scenes/S01E01/01_cold_open.fountain  # Count single file
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
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
STATE_DIR = os.path.join(BASE_DIR, "state")

# TV page targets by format
FORMAT_TARGETS = {
    "half_hour": {"min": 25, "max": 35, "target": 30, "runtime": "22-28 min"},
    "one_hour_network": {"min": 50, "max": 65, "target": 58, "runtime": "42-48 min"},
    "one_hour_streaming": {"min": 55, "max": 70, "target": 62, "runtime": "48-58 min"},
}


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
            if re.match(r'^(INT\.|EXT\.|#|COLD OPEN|ACT)', line.strip(), re.IGNORECASE):
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

        # Act break markers
        if re.match(r'^(END OF ACT|ACT \w+|COLD OPEN|TITLE SEQUENCE)', stripped, re.IGNORECASE):
            total_lines += 2
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


def check_page_target(pages, format_type="one_hour_streaming"):
    """Check if page count is within target range."""
    target = FORMAT_TARGETS.get(format_type, FORMAT_TARGETS["one_hour_streaming"])
    if pages < target["min"]:
        return "UNDER", target
    elif pages > target["max"]:
        return "OVER", target
    else:
        return "OK", target


def main():
    args = sys.argv[1:]
    episode = None
    scene_mode = False
    filepath = None
    format_type = "one_hour_streaming"

    i = 0
    while i < len(args):
        if args[i] == '--episode' and i + 1 < len(args):
            episode = args[i + 1].upper()
            i += 2
        elif args[i] == '--all':
            scene_mode = True
            i += 1
        elif args[i] == '--format' and i + 1 < len(args):
            format_type = args[i + 1]
            i += 2
        elif args[i].endswith('.fountain'):
            filepath = args[i]
            i += 1
        else:
            i += 1

    if filepath:
        # Count a single file
        pages, err = count_fountain_pages(filepath)
        if err:
            print(f"Error: {err}")
            sys.exit(1)
        print(f"{os.path.basename(filepath)}: {pages:.1f} pages")
    elif episode:
        if scene_mode:
            # Count all scenes in the episode
            scene_dir = os.path.join(SCRIPTS_DIR, "scenes", episode)
            if os.path.exists(scene_dir):
                total = count_scene_dir(scene_dir)
                if total:
                    status, target = check_page_target(total, format_type)
                    print(f"\nTarget: {target['min']}-{target['max']} pages ({target['runtime']})")
                    print(f"Status: {status}")
            else:
                print(f"No scenes directory found: {scene_dir}")
        else:
            # Count the assembled episode
            ep_file = os.path.join(SCRIPTS_DIR, f"{episode}.fountain")
            if os.path.exists(ep_file):
                pages, err = count_fountain_pages(ep_file)
                if err:
                    print(f"Error: {err}")
                    sys.exit(1)
                print(f"{episode}: {pages:.1f} pages")
                status, target = check_page_target(pages, format_type)
                print(f"Target: {target['min']}-{target['max']} pages ({target['runtime']})")
                print(f"Status: {status}")
            else:
                print(f"Episode not found: {ep_file}")
                print("Run episode_assemble.py first.")
                sys.exit(1)
    else:
        # Count all assembled episodes
        pattern = os.path.join(SCRIPTS_DIR, "S*.fountain")
        files = sorted(glob.glob(pattern))
        # Exclude season files
        files = [f for f in files if not os.path.basename(f).startswith("Season_")]

        if not files:
            print("No assembled episodes found.")
            print("Run episode_assemble.py first.")
            sys.exit(1)

        total = 0
        print(f"{'Episode':<20} {'Pages':>6} {'Status':>8}")
        print("-" * 36)

        for filepath in files:
            basename = os.path.splitext(os.path.basename(filepath))[0]
            pages, err = count_fountain_pages(filepath)
            if err:
                print(f"{basename:<20} {'ERROR':>6}")
            elif pages is not None:
                status, _ = check_page_target(pages, format_type)
                print(f"{basename:<20} {pages:>6.1f} {status:>8}")
                total += pages

        print("-" * 36)
        print(f"{'TOTAL':<20} {total:>6.1f}")
        print(f"\nAverage per episode: {total / len(files):.1f} pages")


if __name__ == '__main__':
    main()
