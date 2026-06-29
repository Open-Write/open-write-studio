#!/usr/bin/env python3
"""
Parenthetical Audit Tool for TV Scripts
Counts and lists all parentheticals in a Fountain file.
Target: under 3 parentheticals per episode. Over 5 is a red flag.

Usage:
    python tools/parenthetical_audit.py                        # Audit all assembled episodes
    python tools/parenthetical_audit.py --episode S01E01       # Audit single episode
    python tools/parenthetical_audit.py --all                  # Audit all scenes individually
    python tools/parenthetical_audit.py scripts/scenes/S01E01/01_cold_open.fountain  # Audit single file
"""

import re
import sys
import os
import glob


# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
SCENES_BASE = os.path.join(SCRIPTS_DIR, "scenes")

# Parenthetical pattern: line that starts with ( and ends with )
PARENTHETICAL_RE = re.compile(r'^\s*\(([^)]+)\)\s*$')

# Character name pattern (line that is all caps, possibly with spaces/dots)
CHARACTER_RE = re.compile(r'^[A-Z][A-Z\s\.\-]+(\s*\^)?$')

# Per-episode limit
EPISODE_LIMIT = 3
EPISODE_RED_FLAG = 5


def audit_fountain(filepath):
    """Find all parentheticals in a Fountain file with context."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return None, f"File not found: {filepath}"

    parentheticals = []
    current_character = None
    in_title_page = True

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Skip title page
        if in_title_page:
            if re.match(r'^(INT\.|EXT\.|#|COLD OPEN|ACT)', stripped, re.IGNORECASE):
                in_title_page = False
            continue

        # Track character names
        if CHARACTER_RE.match(stripped) and len(stripped) < 40:
            current_character = stripped
            continue

        # Check for parenthetical
        match = PARENTHETICAL_RE.match(stripped)
        if match:
            content = match.group(1)

            # Classify the parenthetical
            ptype = classify_parenthetical(content)

            parentheticals.append({
                'line': i,
                'character': current_character or 'UNKNOWN',
                'content': content,
                'type': ptype,
                'text': stripped
            })

    return parentheticals, None


def classify_parenthetical(content):
    """Classify a parenthetical as functional, emotional, or camera."""
    content_lower = content.lower().strip()

    # Emotional words that indicate emotion-directing
    emotional_words = [
        'angrily', 'sadly', 'quietly', 'nervously', 'softly', 'loudly',
        'whispering', 'shouting', 'crying', 'laughing', 'sobbing',
        'holding back tears', 'tearfully', 'furiously', 'gently',
        'coldly', 'warmly', 'sarcastically', 'bitterly', 'desperately',
        'hesitantly', 'reluctantly', 'firmly', 'shakily', 'trembling'
    ]

    # Camera directions
    camera_words = ['camera', 'angle', 'close-up', 'closeup', 'wide shot', 'pov']

    # Functional (address disambiguation, action during dialogue)
    functional_patterns = [
        r'to\s+\w+',           # (to Daniel)
        r'into\s+\w+',         # (into phone)
        r'on\s+\w+',           # (on phone)
        r'picking up',         # (picking up the photograph)
        r'putting down',
        r'turning to',
        r'not\s+\w+',          # (not Daniel) - disambiguation
        r'continuing',         # (continuing)
        r'beat',               # (beat)
    ]

    for word in emotional_words:
        if word in content_lower:
            return 'EMOTIONAL'

    for word in camera_words:
        if word in content_lower:
            return 'CAMERA'

    for pattern in functional_patterns:
        if re.search(pattern, content_lower):
            return 'FUNCTIONAL'

    # If it contains a verb describing an action, it's probably functional
    if re.search(r'\b(picks up|puts down|turns|stands|sits|walks|looks|takes|holds)\b', content_lower):
        return 'FUNCTIONAL'

    # Default: classify as emotional if it contains adverbs
    if re.search(r'\b\w+ly\b', content_lower):
        return 'EMOTIONAL'

    return 'OTHER'


def print_report(filepath, parentheticals, total_limit=EPISODE_LIMIT):
    """Print the audit report."""
    basename = os.path.basename(filepath)

    emotional = [p for p in parentheticals if p['type'] == 'EMOTIONAL']
    functional = [p for p in parentheticals if p['type'] == 'FUNCTIONAL']
    camera = [p for p in parentheticals if p['type'] == 'CAMERA']
    other = [p for p in parentheticals if p['type'] == 'OTHER']

    print(f"\n{'='*60}")
    print(f"PARENTHETICAL AUDIT: {basename}")
    print(f"{'='*60}")
    print(f"\nTotal parentheticals: {len(parentheticals)}")
    print(f"  Functional (OK):    {len(functional)}")
    print(f"  Emotional (FLAG):   {len(emotional)}")
    print(f"  Camera (FLAG):      {len(camera)}")
    print(f"  Other:              {len(other)}")

    if len(parentheticals) > EPISODE_RED_FLAG:
        print(f"\nRED FLAG: {len(parentheticals)} parentheticals (red flag: {EPISODE_RED_FLAG})")
    elif len(parentheticals) > total_limit:
        print(f"\nWARNING: Over target! {len(parentheticals)} parentheticals (target: {total_limit})")
    else:
        print(f"\nWithin target ({len(parentheticals)}/{total_limit})")

    if emotional:
        print(f"\n{'-'*60}")
        print("EMOTIONAL PARENTHETICALS (must be removed):")
        print(f"{'-'*60}")
        for p in emotional:
            print(f"  Line {p['line']:>4} | {p['character']:<20} | {p['text']}")

    if camera:
        print(f"\n{'-'*60}")
        print("CAMERA PARENTHETICALS (must be removed):")
        print(f"{'-'*60}")
        for p in camera:
            print(f"  Line {p['line']:>4} | {p['character']:<20} | {p['text']}")

    if functional:
        print(f"\n{'-'*60}")
        print("FUNCTIONAL PARENTHETICALS (acceptable):")
        print(f"{'-'*60}")
        for p in functional:
            print(f"  Line {p['line']:>4} | {p['character']:<20} | {p['text']}")

    if other:
        print(f"\n{'-'*60}")
        print("OTHER PARENTHETICALS (review manually):")
        print(f"{'-'*60}")
        for p in other:
            print(f"  Line {p['line']:>4} | {p['character']:<20} | {p['text']}")


def main():
    args = sys.argv[1:]
    episode = None
    all_mode = False
    filepath = None

    i = 0
    while i < len(args):
        if args[i] == '--episode' and i + 1 < len(args):
            episode = args[i + 1].upper()
            i += 2
        elif args[i] == '--all':
            all_mode = True
            i += 1
        elif args[i].endswith('.fountain'):
            filepath = args[i]
            i += 1
        else:
            i += 1

    if filepath:
        # Audit a single file
        parens, err = audit_fountain(filepath)
        if err:
            print(f"Error: {err}")
            sys.exit(1)
        print_report(filepath, parens)
    elif episode:
        if all_mode:
            # Audit all scenes in the episode
            scene_dir = os.path.join(SCENES_BASE, episode)
            if os.path.exists(scene_dir):
                all_parens = []
                pattern = os.path.join(scene_dir, '*.fountain')
                for fp in sorted(glob.glob(pattern)):
                    parens, err = audit_fountain(fp)
                    if parens:
                        for p in parens:
                            p['scene_file'] = os.path.basename(fp)
                        all_parens.extend(parens)
                if all_parens:
                    print_report(f"{episode} (all scenes)", all_parens)
                else:
                    print(f"No parentheticals found in {episode}.")
            else:
                print(f"No scenes directory found: {scene_dir}")
        else:
            # Audit the assembled episode
            ep_file = os.path.join(SCRIPTS_DIR, f"{episode}.fountain")
            if os.path.exists(ep_file):
                parens, err = audit_fountain(ep_file)
                if err:
                    print(f"Error: {err}")
                    sys.exit(1)
                print_report(ep_file, parens)
            else:
                print(f"Episode not found: {ep_file}")
                print("Run episode_assemble.py first.")
                sys.exit(1)
    else:
        # Audit all assembled episodes
        pattern = os.path.join(SCRIPTS_DIR, "S*.fountain")
        files = sorted(glob.glob(pattern))
        files = [f for f in files if not os.path.basename(f).startswith("Season_")]

        if not files:
            print("No assembled episodes found.")
            sys.exit(1)

        grand_total = 0
        episode_summary = []

        for fp in files:
            basename = os.path.splitext(os.path.basename(fp))[0]
            parens, err = audit_fountain(fp)
            if parens:
                count = len(parens)
                emotional = len([p for p in parens if p['type'] == 'EMOTIONAL'])
                grand_total += count
                episode_summary.append({
                    'episode': basename,
                    'total': count,
                    'emotional': emotional,
                    'status': 'RED FLAG' if count > EPISODE_RED_FLAG else ('WARNING' if count > EPISODE_LIMIT else 'OK')
                })

        print(f"\n{'='*60}")
        print(f"PARENTHETICAL AUDIT — ALL EPISODES")
        print(f"{'='*60}")
        print(f"\n{'Episode':<15} {'Total':>6} {'Emotional':>10} {'Status':>10}")
        print("-" * 45)
        for ep in episode_summary:
            print(f"  {ep['episode']:<13} {ep['total']:>6} {ep['emotional']:>10} {ep['status']:>10}")
        print("-" * 45)
        print(f"  {'TOTAL':<13} {grand_total:>6}")

        red_flags = [ep for ep in episode_summary if ep['status'] == 'RED FLAG']
        if red_flags:
            print(f"\n{len(red_flags)} episode(s) with RED FLAG parenthetical counts!")


if __name__ == '__main__':
    main()
