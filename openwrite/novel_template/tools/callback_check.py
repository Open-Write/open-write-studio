#!/usr/bin/env python3
"""
Callback check tool for novel manuscript.
Reads callback_ledger_novel.json against assembled manuscript and reports status.
"""

import os
import sys
import json

LEDGER_FILE = os.path.join(os.path.dirname(__file__), "..", "state", "callback_ledger.json")
CHAPTER_OUTLINE = os.path.join(os.path.dirname(__file__), "..", "state", "chapter_outline.json")


def main():
    if not os.path.exists(LEDGER_FILE):
        print(f"Error: Callback ledger not found: {LEDGER_FILE}")
        sys.exit(1)

    with open(LEDGER_FILE, "r", encoding="utf-8") as f:
        ledger = json.load(f)

    seeds = ledger.get("seeds", [])
    if not seeds:
        print("No callback seeds in the ledger.")
        return

    # Get current chapter from outline if available
    current_chapter = 0
    if os.path.exists(CHAPTER_OUTLINE):
        with open(CHAPTER_OUTLINE, "r", encoding="utf-8") as f:
            outline = json.load(f)
        chapters = outline.get("chapters", [])
        if chapters:
            current_chapter = max(c.get("chapter_number", 0) for c in chapters)

    paid_off = [s for s in seeds if s.get("paid_off")]
    active = [s for s in seeds if not s.get("paid_off")]
    overdue = [s for s in active if s.get("must_pay_off_by_chapter", 999) <= current_chapter]

    print(f"Callback Ledger Summary")
    print(f"{'='*50}")
    print(f"Total seeds: {len(seeds)}")
    print(f"Paid off: {len(paid_off)}")
    print(f"Active: {len(active)}")
    print(f"Overdue: {len(overdue)}")
    print()

    if overdue:
        print("⚠️  OVERDUE CALLBACKS:")
        for s in overdue:
            print(f"  - {s['id']}: seeded in chapter {s.get('seeded_in_chapter', '?')}, "
                  f"deadline chapter {s.get('must_pay_off_by_chapter', '?')}")
            print(f"    {s.get('payoff_description', 'No description')}")
        print()

    if active:
        print("Active callbacks:")
        for s in active:
            deadline = s.get("must_pay_off_by_chapter", "?")
            print(f"  - {s['id']}: deadline chapter {deadline}")
            print(f"    {s.get('payoff_description', 'No description')}")
        print()

    if paid_off:
        print("Paid off:")
        for s in paid_off:
            paid_ch = s.get("paid_off_in_chapter", "?")
            print(f"  - {s['id']}: paid off in chapter {paid_ch}")


if __name__ == "__main__":
    main()
