#!/usr/bin/env python3
"""
Track balance tool for novel manuscript.
Calculates Track A vs Track B vs interlude page ratios.
"""

import os
import sys
import json
import glob
import re

MANUSCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "manuscript", "chapters")
CHAPTER_OUTLINE = os.path.join(os.path.dirname(__file__), "..", "state", "chapter_outline.json")
TARGETS = {
    "a": {"min_pct": 55, "max_pct": 65, "label": "Track A"},
    "b": {"min_pct": 25, "max_pct": 35, "label": "Track B"},
    "interlude": {"min_pct": 5, "max_pct": 15, "label": "Interludes"},
}


def identify_track(filename):
    """Identify track from filename."""
    lower = filename.lower()
    if "_track_b_" in lower:
        return "b"
    if "_interlude" in lower or "_track_interlude_" in lower:
        return "interlude"
    return "a"


def count_words(filepath):
    """Count words in a file."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    words = 0
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("```") and not stripped.startswith("---"):
            words += len(stripped.split())
    return words


def check_alternation(chapters):
    """Check for alternation pattern violations."""
    issues = []
    consecutive = {"a": 0, "b": 0, "interlude": 0}
    for ch in chapters:
        track = ch["track"]
        for t in consecutive:
            if t == track:
                consecutive[t] += 1
            else:
                consecutive[t] = 0
        if consecutive[track] > 3:
            issues.append(f"Chapter {ch.get('number', '?')}: {consecutive[track]} consecutive Track {track.upper()} chapters")
    return issues


def main():
    if not os.path.exists(MANUSCRIPT_DIR):
        print(f"Error: Manuscript directory not found: {MANUSCRIPT_DIR}")
        sys.exit(1)

    chapters = glob.glob(os.path.join(MANUSCRIPT_DIR, "*.md"))
    if not chapters:
        print("No chapter files found.")
        return

    track_data = {"a": [], "b": [], "interlude": []}

    for filepath in sorted(chapters):
        filename = os.path.basename(filepath)
        track = identify_track(filename)
        wc = count_words(filepath)
        match = re.match(r"(\d+)", filename)
        ch_num = int(match.group(1)) if match else 0

        track_data[track].append({
            "file": filename,
            "number": ch_num,
            "track": track,
            "words": wc
        })

    total_words = sum(
        sum(ch["words"] for ch in tracks)
        for tracks in track_data.values()
    )

    print(f"Track Balance Report")
    print(f"{'='*50}")
    print(f"Total words: {total_words}")
    print(f"Estimated pages: {total_words / 250:.1f}")
    print()

    flags = []
    for track in ["a", "b", "interlude"]:
        words = sum(ch["words"] for ch in track_data[track])
        count = len(track_data[track])
        pct = (words / total_words * 100) if total_words > 0 else 0
        target = TARGETS[track]

        status = "✓"
        if pct < target["min_pct"]:
            status = f"⚠️ BELOW TARGET ({target['min_pct']}-{target['max_pct']}%)"
            flags.append(f"Track {track.upper()} at {pct:.1f}%, target {target['min_pct']}-{target['max_pct']}%")
        elif pct > target["max_pct"]:
            status = f"⚠️ ABOVE TARGET ({target['min_pct']}-{target['max_pct']}%)"
            flags.append(f"Track {track.upper()} at {pct:.1f}%, target {target['min_pct']}-{target['max_pct']}%")

        print(f"  {target['label']}: {words} words ({pct:.1f}%), {count} chapters {status}")

    # Check alternation
    all_chapters = []
    for track in track_data:
        all_chapters.extend(track_data[track])
    all_chapters.sort(key=lambda c: c["number"])

    alt_issues = check_alternation(all_chapters)
    if alt_issues:
        print(f"\nAlternation issues:")
        for issue in alt_issues:
            print(f"  ⚠️ {issue}")

    if flags or alt_issues:
        print(f"\n⚠️ {len(flags) + len(alt_issues)} flag(s) raised.")
    else:
        print(f"\n✓ All ratios within target range.")


if __name__ == "__main__":
    main()
