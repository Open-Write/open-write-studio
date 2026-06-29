#!/usr/bin/env python3
"""
Assemble Tool for Screenplay
Concatenates all scene files from script/scenes/ into script/screenplay.fountain
in correct numerical order. Strips process artifacts, prevents duplicates,
verifies scene counts.

Usage:
    python tools/assemble.py                                  # Assemble all scenes
    python tools/assemble.py --title "My Script" --author "Author Name"
    python tools/assemble.py --verify
"""

import os
import sys
import re
import glob
import argparse

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
    (r'^ADVANCE\s*$', re.MULTILINE),
    (r'^COMPLETE\s*$', re.MULTILINE),
]


def strip_artifacts(content):
    for pattern, flags in ARTIFACT_PATTERNS:
        content = re.sub(pattern, '', content, flags=flags)
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content.strip()


def find_scene_files(scene_dir):
    pattern = os.path.join(scene_dir, '*.fountain')
    files = glob.glob(pattern)

    by_number = {}
    for filepath in files:
        basename = os.path.basename(filepath)
        match = re.match(r'^(\d+)([a-z]*)', basename)
        if match:
            num = int(match.group(1))
            suffix = match.group(2) or ''
            key = (num, suffix)
            if key not in by_number:
                by_number[key] = []
            by_number[key].append(filepath)

    scene_files = []
    for key in sorted(by_number.keys()):
        candidates = by_number[key]
        if len(candidates) == 1:
            scene_files.append((key, candidates[0]))
        else:
            candidates.sort(key=lambda f: os.path.getmtime(f), reverse=True)
            winner = candidates[0]
            for loser in candidates[1:]:
                num, suffix = key
                label = f"{num}{suffix}"
                print(f"  NOTE: Skipping duplicate scene {label}: {os.path.basename(loser)} (keeping {os.path.basename(winner)})")
            scene_files.append((key, winner))

    return scene_files


def build_title_page(title, author, contact=""):
    lines = [f"Title: {title}"]
    if author:
        lines.append(f"Credit: {author}")
    if contact:
        lines.append(f"Contact: {contact}")
    lines.append("")
    lines.append("")
    return '\n'.join(lines)


def strip_title_page(content):
    lines = content.split('\n')
    in_title = True
    start = 0

    for i, line in enumerate(lines):
        stripped = line.strip()
        if in_title:
            if ':' in stripped and not stripped.startswith('#') and not stripped.startswith('//'):
                continue
            elif not stripped:
                in_title = False
                start = i + 1
                break
            else:
                in_title = False
                start = 0
                break

    return '\n'.join(lines[start:])


def count_words_fountain(text):
    text = re.sub(r'^(INT\.|EXT\.).*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^(FADE|CUT|DISSOLVE).*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[A-Z][A-Z\s\.]+(\s*\(.*\))?$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\([^)]+\)\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^===\s*$', '', text, flags=re.MULTILINE)
    words = text.split()
    return len(words)


def assemble(scene_dir, output_path, title="Screenplay", author="", contact=""):
    scene_files = find_scene_files(scene_dir)

    if not scene_files:
        print(f"No scene files found in {scene_dir}")
        return False

    print(f"Found {len(scene_files)} scene files:")

    parts = []
    title_page = build_title_page(title, author, contact)
    parts.append(title_page)

    scene_word_counts = []
    total_words = 0

    for sort_key, filepath in scene_files:
        basename = os.path.basename(filepath)
        num, suffix = sort_key
        label = f"{num}{suffix}"
        print(f"  {label:>4}. {basename}")

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        content = strip_title_page(content)
        content = strip_artifacts(content)

        if content and not content.startswith('\n'):
            content = '\n' + content

        wc = count_words_fountain(content)
        scene_word_counts.append((label, basename, wc))
        total_words += wc

        parts.append(content)

    assembled = '\n'.join(parts)
    assembled = re.sub(r'\n{4,}', '\n\n\n', assembled)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(assembled)

    assembled_wc = count_words_fountain(assembled)

    line_count = assembled.count('\n') + 1
    char_count = len(assembled)

    print(f"\n{'='*60}")
    print(f"ASSEMBLY COMPLETE")
    print(f"{'='*60}")
    print(f"  Output: {output_path}")
    print(f"  Scenes: {len(scene_files)}")
    print(f"  Sum of scene words: {total_words}")
    print(f"  Assembled word count: {assembled_wc}")
    print(f"  Lines:  {line_count}")
    print(f"  Chars:  {char_count}")

    return True


def main():
    parser = argparse.ArgumentParser(description='Assemble screenplay scenes into a single Fountain file')
    parser.add_argument('--title', default='Screenplay', help='Script title')
    parser.add_argument('--author', default='', help='Author credit line')
    parser.add_argument('--contact', default='', help='Contact information')
    parser.add_argument('--scene-dir', default=None, help='Scene directory path')
    parser.add_argument('--output', default=None, help='Output file path')
    parser.add_argument('--verify', action='store_true', help='Verify scenes exist without assembling')

    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scene_dir = args.scene_dir or os.path.join(base_dir, 'script', 'scenes')
    output_path = args.output or os.path.join(base_dir, 'script', 'screenplay.fountain')

    if not os.path.exists(scene_dir):
        print(f"Error: Scene directory not found: {scene_dir}")
        sys.exit(1)

    if args.verify:
        scene_files = find_scene_files(scene_dir)
        if not scene_files:
            print("No scene files found.")
            sys.exit(1)
        print(f"Found {len(scene_files)} scene files:")
        for sort_key, filepath in scene_files:
            num, suffix = sort_key
            print(f"  {num}{suffix:>4}. {os.path.basename(filepath)}")
        sys.exit(0)

    success = assemble(scene_dir, output_path, args.title, args.author, args.contact)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
