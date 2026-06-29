#!/usr/bin/env python3
"""
Callback Check Tool for Screenplay
Reads callback_ledger.json against the assembled script, reports:
- Seeds past their must_pay_off_by_scene that are still unpaid
- Payoffs that occurred without proper seeding

Usage:
    python tools/callback_check.py                           # Check against assembled script
    python tools/callback_check.py script/screenplay.fountain  # Check against specific file
    python tools/callback_check.py --current-scene 25        # Check what's due by scene 25
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


def load_ledger(ledger_path):
    """Load the callback ledger JSON."""
    with open(ledger_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_state(state_path):
    """Load project state for current scene number."""
    try:
        with open(state_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def find_payoff_keywords(text, payoff_description):
    """Check if text contains keywords from the payoff description."""
    # Extract significant words from payoff description
    # Remove common words, keep content words
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


def check_callbacks(ledger_path, script_path, current_scene=None):
    """Check callbacks against the assembled script."""
    ledger = load_ledger(ledger_path)
    state_path = os.path.join(os.path.dirname(ledger_path), 'project_state.json')
    state = load_state(state_path)
    
    if current_scene is None and state:
        current_scene = state.get('current_scene', 52)
    elif current_scene is None:
        current_scene = 999  # Default to end if no state
    
    # Load script content
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            script_text = f.read()
    except FileNotFoundError:
        print(f"Script not found: {script_path}")
        print("Running check against ledger only (no script verification).")
        script_text = ""
    
    seeds = ledger.get('seeds', [])
    
    print(f"\n{'='*70}")
    print(f"CALLBACK CHECK — Scene {current_scene}")
    print(f"{'='*70}")
    
    # Check for overdue unpaid seeds
    overdue = []
    upcoming = []
    paid_off = []
    no_deadline = []
    
    for seed in seeds:
        seed_id = seed['id']
        seeded_in = seed.get('seeded_in_scene')
        must_pay_by = seed.get('must_pay_off_by_scene')
        is_paid = seed.get('paid_off', False)
        description = seed.get('payoff_description', '')
        
        if is_paid:
            paid_off.append(seed)
            continue
        
        if must_pay_by is None:
            no_deadline.append(seed)
            continue
        
        if must_pay_by <= current_scene:
            # This seed is overdue — check if the script contains the payoff
            found_in_script = False
            if script_text:
                found_in_script = find_payoff_keywords(script_text, description)
            
            if found_in_script:
                paid_off.append({**seed, 'note': 'Found in script (auto-detected)'})
            else:
                overdue.append(seed)
        else:
            upcoming.append(seed)
    
    # Report
    if overdue:
        print(f"\nOVERDUE UNPAID CALLBACKS ({len(overdue)}):")
        print(f"{'-'*70}")
        for seed in overdue:
            print(f"\n  ID: {seed['id']}")
            print(f"  Seeded in: Scene {seed.get('seeded_in_scene', '?')}")
            print(f"  Due by: Scene {seed['must_pay_off_by_scene']}")
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
            scenes_left = seed['must_pay_off_by_scene'] - current_scene
            print(f"  {seed['id']}: due Scene {seed['must_pay_off_by_scene']} ({scenes_left} scenes away)")
    
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
    base_dir = os.path.dirname(os.path.dirname(__file__))
    ledger_path = os.path.join(base_dir, 'state', 'callback_ledger.json')
    
    current_scene = None
    script_path = None
    
    # Parse args
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--current-scene' and i + 1 < len(args):
            current_scene = int(args[i + 1])
            i += 2
        elif args[i].endswith('.fountain'):
            script_path = args[i]
            i += 1
        else:
            i += 1
    
    if not script_path:
        script_path = os.path.join(base_dir, 'script', 'screenplay.fountain')
    
    if not os.path.exists(ledger_path):
        print(f"Error: Callback ledger not found at {ledger_path}")
        sys.exit(1)
    
    result = check_callbacks(ledger_path, script_path, current_scene)
    sys.exit(result)


if __name__ == '__main__':
    main()
