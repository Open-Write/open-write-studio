#!/usr/bin/env python3
"""
Convention Ledger Scanner for TV Scripts
Scans individual scene Fountain files and produces convention_ledger.json with per-scene
frequency counts for body-anchor markers, sentence structures, and forbidden-after-N flags.
Tracks patterns across all episodes.

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
SCENES_BASE = os.path.join(BASE, "scripts", "scenes")
SCRIPTS_DIR = os.path.join(BASE, "scripts")
OUTPUT_PATH = os.path.join(BASE, "state", "convention_ledger.json")


# ---------------------------------------------------------------------------
# Scene loading
# ---------------------------------------------------------------------------

def load_all_scenes() -> list[dict]:
    """Load all .fountain scene files from all episode directories."""
    scenes = []
    episode_dirs = sorted(glob.glob(os.path.join(SCENES_BASE, "S*")))
    for ep_dir in episode_dirs:
        episode = os.path.basename(ep_dir)
        pattern = os.path.join(ep_dir, "*.fountain")
        files = sorted(glob.glob(pattern))
        for filepath in files:
            label = os.path.splitext(os.path.basename(filepath))[0]
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            scenes.append({
                "episode": episode,
                "label": f"{episode}/{label}",
                "text": text,
                "path": filepath
            })
    return scenes


def load_assembled_episodes() -> list[dict]:
    """Load assembled episode files if no scene directories exist."""
    scenes = []
    pattern = os.path.join(SCRIPTS_DIR, "S*.fountain")
    files = sorted(glob.glob(pattern))
    files = [f for f in files if not os.path.basename(f).startswith("Season_")]
    for filepath in files:
        label = os.path.splitext(os.path.basename(filepath))[0]
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        scenes.append({
            "episode": label,
            "label": label,
            "text": text,
            "path": filepath
        })
    return scenes


# ---------------------------------------------------------------------------
# Text cleaning & sentence extraction
# ---------------------------------------------------------------------------

def clean_fountain(text: str) -> str:
    """Remove Fountain markup while preserving dialogue and action."""
    lines = text.split('\n')
    in_title_page = True
    body_lines = []
    for line in lines:
        if in_title_page:
            if re.match(r'^(INT\.|EXT\.|#|COLD OPEN|ACT)', line.strip(), re.IGNORECASE):
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
    # Remove act break markers
    text = re.sub(r'^(END OF ACT|ACT \w+|COLD OPEN|TITLE SEQUENCE).*$', '', text, flags=re.MULTILINE)
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


# ---------------------------------------------------------------------------
# Dialogue attribution patterns
# ---------------------------------------------------------------------------

DIALOGUE_TAGS = {
    "said": re.compile(r'\bsaid\b', re.IGNORECASE),
    "asked": re.compile(r'\basked\b', re.IGNORECASE),
    "whispered": re.compile(r'\bwhispered\b', re.IGNORECASE),
    "muttered": re.compile(r'\bmuttered\b', re.IGNORECASE),
    "shouted": re.compile(r'\bshouted\b', re.IGNORECASE),
    "replied": re.compile(r'\breplied\b', re.IGNORECASE),
}


def count_dialogue_tags(text: str) -> dict:
    """Count dialogue attribution tags."""
    counts = {}
    for tag, pattern in DIALOGUE_TAGS.items():
        counts[tag] = len(pattern.findall(text))
    return counts


# ---------------------------------------------------------------------------
# Main scanning function
# ---------------------------------------------------------------------------

def scan_scenes():
    """Main entry point: scan scenes and produce convention ledger."""
    print(f"Looking for scenes in {SCENES_BASE}...")
    scenes = load_all_scenes()

    if not scenes:
        print("No scene directories found. Trying assembled episodes...")
        scenes = load_assembled_episodes()

    if not scenes:
        print("No scene files found.")
        return

    print(f"Scenes/episodes found: {len(scenes)}")

    # Initialize global accumulators
    global_anchors = Counter()
    global_dialogue_tags = Counter()
    per_scene_anchors = {}
    per_episode_anchors = defaultdict(lambda: Counter())
    tic_flags = []

    for scene in scenes:
        label = scene["label"]
        episode = scene["episode"]
        scene_text = scene["text"]

        # Body anchors
        anchors = count_body_anchors(scene_text)
        per_scene_anchors[label] = anchors
        for k, v in anchors.items():
            global_anchors[k] += v
            per_episode_anchors[episode][k] += v

        # Dialogue tags
        tags = count_dialogue_tags(clean_fountain(scene_text))
        for k, v in tags.items():
            global_dialogue_tags[k] += v

        # Check for tic overuse
        overuse = find_physical_tic_overuse(anchors)
        if overuse:
            tic_flags.append({"scene": label, "episode": episode, "flags": overuse})

    # Build the ledger
    ledger = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scene_count": len(scenes),
        "episodes_scanned": sorted(set(s["episode"] for s in scenes)),

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
            "per_episode": {k: dict(v) for k, v in per_episode_anchors.items()},
            "flags": tic_flags
        },

        "dialogue_attribution": {
            "global_counts": dict(global_dialogue_tags)
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
    print(f"Scenes/episodes: {len(scenes)}")
    print(f"\n--- Body Anchors (global) ---")
    for k, v in sorted(global_anchors.items()):
        print(f"  {k}: {v}")
    print(f"\n--- Dialogue Tags (global) ---")
    for k, v in sorted(global_dialogue_tags.items()):
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
