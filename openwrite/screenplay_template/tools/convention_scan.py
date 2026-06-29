#!/usr/bin/env python3
"""
Convention Ledger Scanner for Screenplay
Scans individual scene Fountain files and produces convention_ledger.json with per-scene
frequency counts for body-anchor markers, sentence structures, and forbidden-after-N flags.

Usage: python tools/convention_scan.py
Output: state/convention_ledger.json
"""

import re
import json
import os
import glob
from datetime import datetime, timezone
from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENES_PATH = os.path.join(BASE, "script", "scenes")
OUTPUT_PATH = os.path.join(BASE, "state", "convention_ledger.json")


# ---------------------------------------------------------------------------
# Scene splitting
# ---------------------------------------------------------------------------

def load_scenes() -> list[dict]:
    """Load all .fountain scene files."""
    pattern = os.path.join(SCENES_PATH, "*.fountain")
    files = sorted(glob.glob(pattern))
    scenes = []
    for filepath in files:
        label = os.path.splitext(os.path.basename(filepath))[0]
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        scenes.append({"label": label, "text": text, "path": filepath})
    return scenes


# ---------------------------------------------------------------------------
# Text cleaning & sentence extraction
# ---------------------------------------------------------------------------

def clean_fountain(text: str) -> str:
    """Remove Fountain markup while preserving dialogue and action."""
    # Remove title page (everything before first scene heading)
    lines = text.split('\n')
    in_title_page = True
    body_lines = []
    for line in lines:
        if in_title_page:
            if re.match(r'^(INT\.|EXT\.|#)', line.strip(), re.IGNORECASE):
                in_title_page = False
                body_lines.append(line)
            continue
        body_lines.append(line)
    text = '\n'.join(body_lines)

    # Remove scene headings
    text = re.sub(r'^(INT\.|EXT\.).*$', '', text, flags=re.MULTILINE)
    # Remove transitions
    text = re.sub(r'^(FADE|CUT|DISSOLVE).*$', '', text, flags=re.MULTILINE)
    # Remove character names (ALL CAPS lines)
    text = re.sub(r'^[A-Z][A-Z\s\.]+(\s*\(.*\))?$', '', text, flags=re.MULTILINE)
    # Remove parentheticals
    text = re.sub(r'^\s*\([^)]+\)\s*$', '', text, flags=re.MULTILINE)
    # Remove page breaks
    text = re.sub(r'^===\s*$', '', text, flags=re.MULTILINE)
    return text


def extract_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    clean = clean_fountain(text)

    # Protect abbreviations
    clean = re.sub(r'\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr|St|vs|etc|i\.e|e\.g)\.',
                   r'\1<PERIOD>', clean)
    clean = re.sub(r'(\d)\.(\d)', r'\1<PERIOD>\2', clean)

    # Split into paragraphs
    paragraphs = re.split(r'\n\s*\n', clean)

    sentences = []
    for para in paragraphs:
        para = para.strip()
        if not para or para == '---':
            continue
        parts = re.split(r'(?<=[.!?])\s+', para)
        for part in parts:
            part = part.replace('<PERIOD>', '.').strip()
            if len(part) > 5:
                sentences.append(part)

    return sentences


# ---------------------------------------------------------------------------
# Category: Body-Anchor Markers
# ---------------------------------------------------------------------------
BODY_ANCHOR_PATTERNS = {
    "hands_fingers": re.compile(
        r'\b(?:thumb|finger|fingers|palm|palms|hand|hands|fist|fists|grip|grasp|'
        r'knuckle|knuckles|fingertip|fingertips)\b',
        re.IGNORECASE
    ),
    "jaw_teeth": re.compile(
        r'\b(?:jaw|teeth|bite|clench|clenched|grind|ground|molars)\b',
        re.IGNORECASE
    ),
    "throat_tongue": re.compile(
        r'\b(?:throat|swallow|swallowed|tongue|dry mouth|voice caught)\b',
        re.IGNORECASE
    ),
    "feet_legs": re.compile(
        r'\b(?:foot|feet|knee|knees|ankle|ankles|heel|heels|weight shift)\b',
        re.IGNORECASE
    ),
    "shoulders_neck": re.compile(
        r'\b(?:shoulder|shoulders|neck|collar|collarbone)\b',
        re.IGNORECASE
    ),
    "eyes": re.compile(
        r'\b(?:eye|eyes|eyelid|eyelids|blink|blinked|gaze|stare|stared|pupil|pupils)\b',
        re.IGNORECASE
    ),
    "breathing": re.compile(
        r'\b(?:breath|breathes|exhale|exhaled|inhale|inhaled|breathing|held.*breath)\b',
        re.IGNORECASE
    ),
    "temperature": re.compile(
        r'\b(?:cold|warm|warmth|heat|chill|chilled|fever)\b',
        re.IGNORECASE
    ),
}


def count_body_anchors(text: str) -> dict:
    """Count body-anchor markers in text."""
    counts = {}
    for category, pattern in BODY_ANCHOR_PATTERNS.items():
        counts[category] = len(pattern.findall(text))
    return counts


# ---------------------------------------------------------------------------
# Forbidden-After-N Flags
# ---------------------------------------------------------------------------

def find_physical_tic_overuse(scene_anchors: dict) -> list[str]:
    """Flag any body-anchor category used 3+ times in same scene."""
    flags = []
    for cat, count in scene_anchors.items():
        if count >= 3:
            flags.append(f"{cat}: {count} occurrences")
    return flags


def find_scene_ending_repetition(scene_endings: dict) -> list[dict]:
    """Flag any scene-ending pattern used 3+ times across manuscript."""
    pattern_counts = Counter()
    pattern_scenes = defaultdict(list)

    for scene_label, ending_type in scene_endings.items():
        if ending_type == "empty":
            continue
        pattern_counts[ending_type] += 1
        pattern_scenes[ending_type].append(scene_label)

    flags = []
    for pattern, count in pattern_counts.items():
        if count >= 3:
            flags.append({
                "pattern": pattern,
                "count": count,
                "scenes": sorted(pattern_scenes[pattern])
            })

    return flags


# ---------------------------------------------------------------------------
# Main scanning function
# ---------------------------------------------------------------------------
def scan_scenes():
    """Main entry point: scan scenes and produce convention ledger."""
    print(f"Reading scenes from {SCENES_PATH}...")
    scenes = load_scenes()

    if not scenes:
        print("No scene files found.")
        return

    print(f"Scenes found: {len(scenes)}")

    # Initialize global accumulators
    global_anchors = Counter()
    per_scene_anchors = {}
    tic_flags = []

    for scene in scenes:
        label = scene["label"]
        scene_text = scene["text"]

        # Body anchors
        anchors = count_body_anchors(scene_text)
        per_scene_anchors[label] = anchors
        for k, v in anchors.items():
            global_anchors[k] += v

        # Check for tic overuse
        overuse = find_physical_tic_overuse(anchors)
        if overuse:
            tic_flags.append({"scene": label, "flags": overuse})

    # Build the ledger
    ledger = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scene_count": len(scenes),

        "body_anchors": {
            "targets_per_scene": {
                "hands_fingers": "<=2",
                "jaw_teeth": "<=1",
                "throat_tongue": "<=1",
                "feet_legs": "<=1",
                "shoulders_neck": "<=1",
                "eyes": "<=2",
                "breathing": "<=1",
                "temperature": "<=2"
            },
            "global_counts": dict(global_anchors),
            "per_scene": per_scene_anchors,
            "flags": tic_flags
        },

        "flags": {
            "physical_tic_overuse": tic_flags
        }
    }

    # Write output
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)

    print(f"\nConvention ledger written to {OUTPUT_PATH}")
    print(f"\n{'='*60}")
    print(f"CONVENTION LEDGER SUMMARY")
    print(f"{'='*60}")
    print(f"Scenes: {len(scenes)}")
    print(f"\n--- Body Anchors (global) ---")
    for k, v in sorted(global_anchors.items()):
        print(f"  {k}: {v}")
    print(f"\n--- Flags ---")
    print(f"  Physical tic overuse: {len(tic_flags)} scenes flagged")

    if tic_flags:
        print(f"\n  Tic overuse details:")
        for tf in tic_flags[:10]:
            print(f"    {tf['scene']}: {', '.join(tf['flags'])}")

    return ledger


if __name__ == "__main__":
    scan_scenes()
