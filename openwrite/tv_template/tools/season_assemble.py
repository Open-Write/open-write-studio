#!/usr/bin/env python3
"""
Season Assembly Tool for TV Scripts
Assembles individual episode Fountain files into a single season script.
Strips process artifacts, verifies episode counts.

Usage:
    python tools/season_assemble.py --season 1
    python tools/season_assemble.py --season 1 --title "Threshold" --author "Written by Creator Name"
"""

import os
import sys
import glob
import re
from word_count import strip_artifacts

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

DEFAULT_AUTHOR = "Written by [Creator Name]"


def parse_args():
    season = None
    title = None
    author = DEFAULT_AUTHOR

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--season' and i + 1 < len(args):
            season = int(args[i + 1])
            i += 2
        elif args[i] == '--title' and i + 1 < len(args):
            title = args[i + 1]
            i += 2
        elif args[i] == '--author' and i + 1 < len(args):
            author = args[i + 1]
            i += 2
        else:
            i += 1

    if season is None:
        print("Error: --season is required (e.g., --season 1)")
        sys.exit(1)

    if not title:
        title = f"Season {season}"

    return season, title, author


def get_episode_files(season):
    pattern = os.path.join(SCRIPTS_DIR, f"S{season:02d}E*.fountain")
    files = sorted(glob.glob(pattern))
    return files


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
    season, title, author = parse_args()

    files = get_episode_files(season)

    if not files:
        print(f"Error: No episode files found for Season {season}")
        print(f"Expected: {SCRIPTS_DIR}/S{season:02d}E*.fountain")
        print(f"Run episode_assemble.py for each episode first.")
        sys.exit(1)

    title_page = f"""Title: {title}
Subtitle: Season {season}
Credit: {author}
"""

    parts = [title_page.strip()]
    episode_stats = []
    total_lines = 0
    total_scenes = 0

    for filepath in files:
        basename = os.path.basename(filepath)
        episode_code = os.path.splitext(basename)[0]

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()

        content = strip_title_page(content)
        content = strip_artifacts(content)

        if content:
            divider = f"\n{'='*60}\n{episode_code}\n{'='*60}\n"
            parts.append(divider)
            parts.append(content)

            line_count = content.count('\n')
            scene_count = len(re.findall(r'^(INT\.|EXT\.)', content, re.MULTILINE))
            estimated_pages = round(line_count / 55.0, 1)

            episode_stats.append({
                'episode': episode_code,
                'lines': line_count,
                'scenes': scene_count,
                'pages': estimated_pages
            })

            total_lines += line_count
            total_scenes += scene_count

    assembled = "\n\n".join(parts) + "\n"

    output_file = os.path.join(SCRIPTS_DIR, f"Season_{season}.fountain")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(assembled)

    total_pages = round(total_lines / 55.0, 1)

    print(f"{'='*60}")
    print(f"SEASON {season} ASSEMBLY")
    print(f"{'='*60}")
    print(f"  Episodes: {len(files)}")
    print(f"  Total scenes: {total_scenes}")
    print(f"  Total lines: {total_lines}")
    print(f"  Estimated pages: {total_pages}")
    print(f"  Output: {output_file}")
    print(f"\n  Per-episode breakdown:")
    print(f"  {'Episode':<12} {'Scenes':>7} {'Lines':>7} {'Pages':>7}")
    print(f"  {'-'*35}")
    for stat in episode_stats:
        print(f"  {stat['episode']:<12} {stat['scenes']:>7} {stat['lines']:>7} {stat['pages']:>7.1f}")
    print(f"  {'-'*35}")
    print(f"  {'TOTAL':<12} {total_scenes:>7} {total_lines:>7} {total_pages:>7.1f}")


if __name__ == "__main__":
    main()
