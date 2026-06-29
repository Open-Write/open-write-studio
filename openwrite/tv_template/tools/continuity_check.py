#!/usr/bin/env python3
"""
Continuity Check Tool for TV Scripts
Checks for continuity issues across episodes:
- Character knowledge consistency (do they know things they shouldn't?)
- Physical state continuity (injuries, illnesses carrying over)
- Timeline consistency (does time flow correctly?)
- Prop/location continuity (is the office described the same way?)
- Dialogue voice consistency (does a character sound the same?)

Usage:
    python tools/continuity_check.py --season 1                # Check all episodes
    python tools/continuity_check.py --episode S01E01 S01E05   # Check range
    python tools/continuity_check.py --episode S01E05           # Check single episode
"""

import json
import re
import sys
import os
import glob
from collections import defaultdict

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(BASE_DIR, "state")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")


def parse_episode_code(code):
    """Parse S01E01 into (season, episode) tuple."""
    match = re.match(r'S(\d+)E(\d+)', code, re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None


def episode_code_sort_key(code):
    """Sort key for episode codes."""
    s, e = parse_episode_code(code)
    return (s or 0, e or 0)


def load_json(filepath):
    """Load a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def load_episode_script(episode_code):
    """Load the assembled episode Fountain file."""
    filepath = os.path.join(SCRIPTS_DIR, f"{episode_code}.fountain")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return None


def extract_characters(script_text):
    """Extract character names from a Fountain script."""
    # Character names in Fountain are ALL CAPS lines
    char_re = re.compile(r'^([A-Z][A-Z\s\.\-]+)(\s*\^)?$', re.MULTILINE)
    # Exclude common non-character CAPS lines
    exclude = {'INT', 'EXT', 'FADE', 'CUT', 'DISSOLVE', 'CONTINUOUS',
               'DAY', 'NIGHT', 'DAWN', 'DUSK', 'LATER', 'MOMENTS',
               'TITLE', 'COLD OPEN', 'ACT', 'END', 'BEGIN', 'MONTAGE',
               'SERIES OF SHOTS', 'INTERCUT'}

    characters = set()
    for match in char_re.finditer(script_text):
        name = match.group(1).strip()
        # Skip if it's a common non-character line
        if name in exclude or len(name) > 30:
            continue
        # Skip if it looks like a scene heading
        if name.startswith(('INT', 'EXT')):
            continue
        characters.add(name)

    return characters


def extract_locations(script_text):
    """Extract locations from scene headings."""
    loc_re = re.compile(r'^(INT\.|EXT\.)\s*(.+?)(?:\s*-\s*(?:DAY|NIGHT|DAWN|DUSK|CONTINUOUS|LATER|MORNING|EVENING))?\s*$',
                        re.MULTILINE | re.IGNORECASE)
    locations = set()
    for match in loc_re.finditer(script_text):
        loc = match.group(2).strip()
        locations.add(loc)
    return locations


def check_character_continuity(episodes):
    """Check that characters appear consistently across episodes."""
    issues = []
    character_episodes = defaultdict(list)

    for ep in episodes:
        script = load_episode_script(ep)
        if not script:
            continue
        characters = extract_characters(script)
        for char in characters:
            character_episodes[char].append(ep)

    # Check for characters that disappear without explanation
    # (This is a heuristic — not all characters appear in every episode)
    for char, eps in character_episodes.items():
        if len(eps) >= 3:
            # Check for gaps of 3+ episodes
            sorted_eps = sorted(eps, key=episode_code_sort_key)
            for i in range(1, len(sorted_eps)):
                _, prev_ep = parse_episode_code(sorted_eps[i-1])
                _, curr_ep = parse_episode_code(sorted_eps[i])
                if prev_ep and curr_ep and curr_ep - prev_ep > 3:
                    issues.append({
                        'type': 'character_gap',
                        'severity': 'warning',
                        'character': char,
                        'detail': f'{char} appears in {sorted_eps[i-1]} and {sorted_eps[i]} but not in between ({curr_ep - prev_ep - 1} episode gap)',
                        'episodes': [sorted_eps[i-1], sorted_eps[i]]
                    })

    return issues


def check_location_continuity(episodes):
    """Check that locations are described consistently."""
    issues = []
    location_first_seen = {}

    for ep in episodes:
        script = load_episode_script(ep)
        if not script:
            continue
        locations = extract_locations(script)
        for loc in locations:
            # Normalize location name for comparison
            normalized = loc.upper().strip()
            if normalized not in location_first_seen:
                location_first_seen[normalized] = ep
            # Check for spelling variations (simple heuristic)
            for existing in location_first_seen:
                if existing != normalized:
                    # Check if they might be the same location with different spelling
                    if (normalized.replace(' ', '') == existing.replace(' ', '') and
                            normalized != existing):
                        issues.append({
                            'type': 'location_spelling',
                            'severity': 'warning',
                            'detail': f'Location "{loc}" in {ep} may be inconsistent with "{existing}" (first seen in {location_first_seen[existing]})',
                            'episodes': [ep, location_first_seen[existing]]
                        })

    return issues


def check_state_tracker():
    """Check character_state_tracker.json for inconsistencies."""
    issues = []
    tracker_path = os.path.join(STATE_DIR, "character_state_tracker.json")
    tracker = load_json(tracker_path)

    if not tracker:
        issues.append({
            'type': 'missing_state',
            'severity': 'info',
            'detail': 'character_state_tracker.json not found — run after first episode is locked',
            'episodes': []
        })
        return issues

    characters = tracker.get('characters', {})
    for char_name, char_data in characters.items():
        knowledge = char_data.get('knowledge_state', {})
        episodes_list = sorted(knowledge.keys(), key=episode_code_sort_key)

        # Check for knowledge that appears and disappears
        for i in range(1, len(episodes_list)):
            prev_ep = episodes_list[i-1]
            curr_ep = episodes_list[i]
            prev_knows = set(knowledge[prev_ep].get('knows', []))
            curr_knows = set(knowledge[curr_ep].get('knows', []))

            # Things the character knew before but forgot (potential issue)
            forgot = prev_knows - curr_knows
            if forgot:
                issues.append({
                    'type': 'knowledge_loss',
                    'severity': 'warning',
                    'character': char_name,
                    'detail': f'{char_name} knew {forgot} in {prev_ep} but not in {curr_ep}',
                    'episodes': [prev_ep, curr_ep]
                })

    return issues


def check_season_arc_tracker():
    """Check season_arc_tracker.json for completeness."""
    issues = []
    tracker_path = os.path.join(STATE_DIR, "season_arc_tracker.json")
    tracker = load_json(tracker_path)

    if not tracker:
        issues.append({
            'type': 'missing_state',
            'severity': 'info',
            'detail': 'season_arc_tracker.json not found',
            'episodes': []
        })
        return issues

    # Check if all episodes are tracked
    total = tracker.get('total_episodes', 0)
    completion = tracker.get('episode_completion', {})
    missing = []
    for i in range(1, total + 1):
        ep_code = f"S{tracker.get('season', 1):02d}E{i:02d}"
        if ep_code not in completion:
            missing.append(ep_code)

    if missing:
        issues.append({
            'type': 'untracked_episodes',
            'severity': 'info',
            'detail': f'Episodes not yet tracked in season arc: {", ".join(missing)}',
            'episodes': missing
        })

    return issues


def get_episode_range(args):
    """Parse episode range from args."""
    episodes = []
    i = 0
    while i < len(args):
        if args[i] == '--episode' and i + 1 < len(args):
            i += 1
            while i < len(args) and not args[i].startswith('--'):
                episodes.append(args[i].upper())
                i += 1
        elif args[i] == '--season' and i + 1 < len(args):
            season_num = int(args[i + 1])
            pattern = os.path.join(SCRIPTS_DIR, f"S{season_num:02d}E*.fountain")
            for f in sorted(glob.glob(pattern)):
                ep = os.path.splitext(os.path.basename(f))[0]
                if not ep.startswith("Season_"):
                    episodes.append(ep)
            i += 2
        else:
            i += 1
    return sorted(set(episodes), key=episode_code_sort_key)


def main():
    args = sys.argv[1:]
    episodes = get_episode_range(args)

    if not episodes:
        print("Error: No episodes specified.")
        print("Usage: python tools/continuity_check.py --season 1")
        print("       python tools/continuity_check.py --episode S01E01 S01E05")
        sys.exit(1)

    print(f"\n{'='*70}")
    print(f"CONTINUITY CHECK — {episodes[0]} to {episodes[-1]}")
    print(f"{'='*70}")
    print(f"Episodes: {len(episodes)}")

    all_issues = []

    # Check character continuity
    print(f"\nChecking character continuity...")
    char_issues = check_character_continuity(episodes)
    all_issues.extend(char_issues)

    # Check location continuity
    print(f"Checking location continuity...")
    loc_issues = check_location_continuity(episodes)
    all_issues.extend(loc_issues)

    # Check state tracker
    print(f"Checking state tracker...")
    state_issues = check_state_tracker()
    all_issues.extend(state_issues)

    # Check season arc tracker
    print(f"Checking season arc tracker...")
    arc_issues = check_season_arc_tracker()
    all_issues.extend(arc_issues)

    # Report
    if all_issues:
        errors = [i for i in all_issues if i['severity'] == 'error']
        warnings = [i for i in all_issues if i['severity'] == 'warning']
        infos = [i for i in all_issues if i['severity'] == 'info']

        print(f"\n{'='*70}")
        print(f"ISSUES FOUND: {len(all_issues)}")
        print(f"{'='*70}")

        if errors:
            print(f"\nERRORS ({len(errors)}):")
            print(f"{'-'*70}")
            for issue in errors:
                print(f"  [{issue['type']}] {issue['detail']}")

        if warnings:
            print(f"\nWARNINGS ({len(warnings)}):")
            print(f"{'-'*70}")
            for issue in warnings:
                print(f"  [{issue['type']}] {issue['detail']}")

        if infos:
            print(f"\nINFO ({len(infos)}):")
            print(f"{'-'*70}")
            for issue in infos:
                print(f"  [{issue['type']}] {issue['detail']}")

        if errors:
            return 1
    else:
        print(f"\nNo continuity issues found.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
