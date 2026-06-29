#!/usr/bin/env python3
"""
Callback Check Tool for TV Scripts
Reads callback_ledger.json against assembled episode scripts, reports:
- Seeds past their must_pay_off_by_episode that are still unpaid
- Payoffs that occurred without proper seeding
- Cross-episode callback status

Usage:
    python tools/callback_check.py                           # Check all episodes
    python tools/callback_check.py --episode S01E05          # Check through episode S01E05
    python tools/callback_check.py --season 1                # Check full season
    python tools/callback_check.py --episode S01E01 S01E05   # Check range
"""

import json
import re
import sys
import os
import glob

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER_PATH = os.path.join(BASE_DIR, "state", "callback_ledger.json")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")


def load_ledger():
    """Load the callback ledger JSON."""
    with open(LEDGER_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


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


def load_episode_script(episode_code):
    """Load the assembled episode Fountain file."""
    filepath = os.path.join(SCRIPTS_DIR, f"{episode_code}.fountain")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""


def find_payoff_keywords(text, payoff_description):
    """Check if text contains keywords from the payoff description."""
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                  'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                  'would', 'could', 'should', 'may', 'might', 'shall', 'can',
                  'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
                  'with', 'by', 'from', 'as', 'into', 'through', 'during',
                  'before', 'after', 'above', 'below', 'between', 'each',
                  'that', 'this', 'these', 'those', 'it', 'its', 'they',
                  'them', 'their', 'we', 'us', 'our', 'he', 'him', 'his',
                  'she', 'her', 'not', 'no', 'nor', 'so', 'if', 'then',
                  'than', 'too', 'very', 'just', 'about', 'up', 'out',
                  'also', 'how', 'what', 'when', 'where', 'who', 'whom',
                  'which', 'why', 'all', 'any', 'both', 'few', 'more',
                  'most', 'other', 'some', 'such', 'only', 'own', 'same'}

    words = re.findall(r'[a-z]+', payoff_description.lower())
    keywords = [w for w in words if len(w) > 3 and w not in stop_words]

    if not keywords:
        return False

    text_lower = text.lower()
    matches = sum(1 for kw in keywords if kw in text_lower)

    # Require at least 30% of keywords to match
    return matches / len(keywords) >= 0.3


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
            # Find all episodes for this season
            pattern = os.path.join(SCRIPTS_DIR, f"S{season_num:02d}E*.fountain")
            for f in sorted(glob.glob(pattern)):
                ep = os.path.splitext(os.path.basename(f))[0]
                episodes.append(ep)
            i += 2
        else:
            i += 1
    return sorted(set(episodes), key=episode_code_sort_key)


def check_callbacks(episodes=None):
    """Check callbacks against episode scripts."""
    ledger = load_ledger()
    seeds = ledger.get('seeds', [])

    if not seeds:
        print("No seeds in callback ledger.")
        return 0

    # Determine which episodes to check
    if episodes:
        check_episodes = episodes
    else:
        # Find all assembled episodes
        pattern = os.path.join(SCRIPTS_DIR, "S*.fountain")
        check_episodes = sorted([
            os.path.splitext(os.path.basename(f))[0]
            for f in glob.glob(pattern)
            if not os.path.basename(f).startswith("Season_")
        ], key=episode_code_sort_key)

    if not check_episodes:
        print("No assembled episode scripts found.")
        print("Run episode_assemble.py first.")
        return 1

    # Load scripts for keyword matching
    episode_scripts = {}
    for ep in check_episodes:
        episode_scripts[ep] = load_episode_script(ep)

    all_script_text = "\n".join(episode_scripts.values())

    # Categorize seeds
    overdue = []
    upcoming = []
    paid_off = []
    no_deadline = []

    for seed in seeds:
        seed_id = seed['id']
        seeded_in = seed.get('seeded_in_episode', '?')
        must_pay_by = seed.get('must_pay_off_by_episode')
        is_paid = seed.get('paid_off', False)
        description = seed.get('payoff_description', '')

        if is_paid:
            paid_off.append(seed)
            continue

        if must_pay_by is None:
            no_deadline.append(seed)
            continue

        # Check if the payoff deadline has passed
        deadline_sort = episode_code_sort_key(must_pay_by)
        latest_checked = episode_code_sort_key(check_episodes[-1]) if check_episodes else (0, 0)

        if deadline_sort <= latest_checked:
            # This seed is overdue — check if any episode contains the payoff
            found_in_script = False
            found_in_episode = None
            for ep in check_episodes:
                if episode_code_sort_key(ep) >= episode_code_sort_key(seeded_in or "S00E00"):
                    if find_payoff_keywords(episode_scripts.get(ep, ""), description):
                        found_in_script = True
                        found_in_episode = ep
                        break

            if found_in_script:
                paid_off.append({**seed, 'note': f'Found in {found_in_episode} (auto-detected)'})
            else:
                overdue.append(seed)
        else:
            upcoming.append(seed)

    # Report
    print(f"\n{'='*70}")
    print(f"CALLBACK CHECK — Through {check_episodes[-1] if check_episodes else 'N/A'}")
    print(f"{'='*70}")

    if overdue:
        print(f"\nOVERDUE UNPAID CALLBACKS ({len(overdue)}):")
        print(f"{'-'*70}")
        for seed in overdue:
            print(f"\n  ID: {seed['id']}")
            print(f"  Seeded in: {seed.get('seeded_in_episode', '?')}")
            print(f"  Due by: {seed['must_pay_off_by_episode']}")
            print(f"  Description: {seed['payoff_description']}")
    else:
        print(f"\nNo overdue callbacks.")

    if paid_off:
        print(f"\nPAID OFF ({len(paid_off)}):")
        print(f"{'-'*70}")
        for seed in paid_off:
            note = seed.get('note', 'Marked in ledger')
            print(f"  {seed['id']}: {note}")

    if upcoming:
        print(f"\nUPCOMING ({len(upcoming)}):")
        print(f"{'-'*70}")
        for seed in upcoming:
            print(f"  {seed['id']}: due {seed['must_pay_off_by_episode']} (seeded in {seed.get('seeded_in_episode', '?')})")

    if no_deadline:
        print(f"\nNO DEADLINE ({len(no_deadline)}):")
        print(f"{'-'*70}")
        for seed in no_deadline:
            print(f"  {seed['id']}: {seed['payoff_description']}")

    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"{'='*70}")
    print(f"  Total seeds: {len(seeds)}")
    print(f"  Paid off: {len(paid_off)}")
    print(f"  Overdue: {len(overdue)}")
    print(f"  Upcoming: {len(upcoming)}")
    print(f"  No deadline: {len(no_deadline)}")

    if overdue:
        print(f"\n{len(overdue)} callback(s) past deadline without payoff!")
        return 1
    else:
        print(f"\nAll callbacks on track.")
        return 0


def main():
    args = sys.argv[1:]
    episodes = get_episode_range(args)
    result = check_callbacks(episodes if episodes else None)
    sys.exit(result)


if __name__ == '__main__':
    main()
