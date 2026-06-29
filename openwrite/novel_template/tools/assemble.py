#!/usr/bin/env python3
"""
Assemble tool for novel manuscript.
Concatenates chapter files into a single manuscript file.
Strips process artifacts, prevents duplicates, verifies word counts.

Usage:
    python tools/assemble.py --title "Title" --author "Author"
    python tools/assemble.py --verify
    python tools/assemble.py --title "Title" --author "Author" --output manuscript/novel.md
"""

import os
import sys
import re
import glob
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "tools"))
try:
    from word_count import count_prose_words_from_text, strip_artifacts
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "tools"))
    from word_count import count_prose_words_from_text, strip_artifacts

CHAPTERS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "manuscript", "chapters")
DEFAULT_OUTPUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "manuscript", "novel.md")

MIN_WORD_FLOOR = 800


def extract_chapter_number(filename):
    match = re.match(r"(\d+)", os.path.basename(filename))
    return int(match.group(1)) if match else 0


def find_canonical_chapters(chapters_dir):
    files = glob.glob(os.path.join(chapters_dir, "*.md"))
    by_chapter = {}
    for filepath in files:
        ch_num = extract_chapter_number(os.path.basename(filepath))
        if ch_num not in by_chapter:
            by_chapter[ch_num] = []
        by_chapter[ch_num].append(filepath)

    canonical = []
    has_duplicates = False
    for ch_num in sorted(by_chapter.keys()):
        candidates = by_chapter[ch_num]
        if len(candidates) == 1:
            canonical.append(candidates[0])
        else:
            has_duplicates = True
            print(f"  ERROR: Duplicate files for chapter {ch_num}:")
            for c in candidates:
                print(f"    {os.path.basename(c)}")
            print(f"  Resolve by deleting the old file. The pipeline must overwrite, not create duplicates.")

    if has_duplicates:
        print(f"\n  FATAL: Duplicate chapter files found. Assembly aborted.")
        print(f"  The pipeline must overwrite chapters on revision, never create a second file.")
        return []

    return canonical


def assemble(chapters_dir, output_path, title="Untitled", author="Author"):
    if not os.path.exists(chapters_dir):
        print(f"Error: Chapters directory not found: {chapters_dir}")
        return False

    canonical = find_canonical_chapters(chapters_dir)
    if not canonical:
        print("No chapter files found.")
        return False

    chapter_word_counts = []
    total_words = 0
    parts = []

    parts.append(f"# {title}\n\n")
    parts.append(f"*by {author}*\n\n")
    parts.append("---\n\n")

    for filepath in canonical:
        filename = os.path.basename(filepath)
        ch_num = extract_chapter_number(filename)

        with open(filepath, "r", encoding="utf-8-sig") as f:
            raw_content = f.read()

        clean_content = strip_artifacts(raw_content)
        wc = count_prose_words_from_text(clean_content)
        chapter_word_counts.append((ch_num, filename, wc))
        total_words += wc

        if wc < MIN_WORD_FLOOR:
            print(f"  WARNING: Chapter {ch_num} ({filename}) has {wc} words — below {MIN_WORD_FLOOR} word floor")

        parts.append(clean_content)
        parts.append("\n\n---\n\n")

    assembled = ''.join(parts)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(assembled)

    assembled_wc = count_prose_words_from_text(assembled)

    print(f"{'='*60}")
    print(f"ASSEMBLY COMPLETE")
    print(f"{'='*60}")
    print(f"  Output: {output_path}")
    print(f"  Chapters: {len(canonical)}")
    print(f"  Sum of chapter words: {total_words}")
    print(f"  Assembled word count: {assembled_wc}")
    print(f"  Estimated pages: {total_words / 250:.1f}")
    print()

    for ch_num, filename, wc in chapter_word_counts:
        floor_mark = " BELOW FLOOR" if wc < MIN_WORD_FLOOR else ""
        print(f"  Ch {ch_num:>3}: {wc:>6} words — {filename}{floor_mark}")

    under_floor = [(n, f, w) for n, f, w in chapter_word_counts if w < MIN_WORD_FLOOR]
    if under_floor:
        print(f"\n  WARNING: {len(under_floor)} chapter(s) below {MIN_WORD_FLOOR} word floor")

    return True


def verify(chapters_dir):
    if not os.path.exists(chapters_dir):
        print(f"Error: Chapters directory not found: {chapters_dir}")
        return False

    canonical = find_canonical_chapters(chapters_dir)
    if not canonical:
        print("No chapter files found.")
        return False

    all_pass = True
    print(f"Verifying {len(canonical)} chapter files...\n")

    for filepath in canonical:
        filename = os.path.basename(filepath)
        ch_num = extract_chapter_number(filename)

        with open(filepath, "r", encoding="utf-8-sig") as f:
            content = f.read()

        clean = strip_artifacts(content)
        wc = count_prose_words_from_text(clean)

        status = "PASS" if wc >= MIN_WORD_FLOOR else "FAIL"
        if wc < MIN_WORD_FLOOR:
            all_pass = False
        print(f"  Ch {ch_num:>3}: {wc:>6} words — {status} — {filename}")

    return all_pass


def main():
    parser = argparse.ArgumentParser(description="Assemble chapter files into the novel manuscript")
    parser.add_argument("--title", default="Untitled", help="Novel title")
    parser.add_argument("--author", default="Author", help="Author name")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Output file path")
    parser.add_argument("--verify", action="store_true", help="Verify all chapters meet word floor without assembling")
    args = parser.parse_args()

    if args.verify:
        success = verify(CHAPTERS_DIR)
        sys.exit(0 if success else 1)
    else:
        success = assemble(CHAPTERS_DIR, args.output, args.title, args.author)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
