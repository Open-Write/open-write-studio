#!/usr/bin/env python3
"""
Parenthetical Audit Tool for Screenplay
Counts and lists all parentheticals in a Fountain file.
The bible says total under 20 for the entire screenplay.

Usage:
    python tools/parenthetical_audit.py                        # Audit assembled screenplay
    python tools/parenthetical_audit.py script/scenes/01_cold_open.fountain  # Audit single scene
    python tools/parenthetical_audit.py --all                  # Audit all scenes individually
"""

import re
import sys
import os
import glob


# Parenthetical pattern: line that starts with ( and ends with )
# Must be on its own line, typically after a character name
PARENTHETICAL_RE = re.compile(r'^\s*\(([^)]+)\)\s*$')

# Character name pattern (line that is all caps, possibly with spaces/dots)
CHARACTER_RE = re.compile(r'^[A-Z][A-Z\s\.\-]+(\s*\^)?$')


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
            if re.match(r'^(INT\.|EXT\.|#)', stripped, re.IGNORECASE):
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


def print_report(filepath, parentheticals, total_limit=20):
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
    
    if len(parentheticals) > total_limit:
        print(f"\nWARNING: Over limit! {len(parentheticals)} parentheticals (limit: {total_limit})")
    else:
        print(f"\nWithin limit ({len(parentheticals)}/{total_limit})")
    
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
    if len(sys.argv) < 2:
        # Default: audit assembled script
        assembled = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'script', 'screenplay.fountain')
        if os.path.exists(assembled):
            parens, err = audit_fountain(assembled)
            if err:
                print(f"Error: {err}")
                sys.exit(1)
            print_report(assembled, parens)
        else:
            # Try scenes directory
            scene_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'script', 'scenes')
            if os.path.exists(scene_dir):
                all_parens = []
                pattern = os.path.join(scene_dir, '*.fountain')
                for filepath in sorted(glob.glob(pattern)):
                    parens, err = audit_fountain(filepath)
                    if parens:
                        for p in parens:
                            p['scene_file'] = os.path.basename(filepath)
                        all_parens.extend(parens)
                if all_parens:
                    print_report("All scenes combined", all_parens)
                else:
                    print("No parentheticals found in any scene.")
            else:
                print("No script found.")
                sys.exit(1)
    elif sys.argv[1] == '--all':
        scene_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'script', 'scenes')
        all_parens = []
        pattern = os.path.join(scene_dir, '*.fountain')
        for filepath in sorted(glob.glob(pattern)):
            parens, err = audit_fountain(filepath)
            if parens:
                for p in parens:
                    p['scene_file'] = os.path.basename(filepath)
                all_parens.extend(parens)
                print_report(filepath, parens)
        if all_parens:
            print(f"\n{'='*60}")
            print(f"GRAND TOTAL: {len(all_parens)} parentheticals across all scenes")
            print(f"{'='*60}")
    else:
        filepath = sys.argv[1]
        parens, err = audit_fountain(filepath)
        if err:
            print(f"Error: {err}")
            sys.exit(1)
        print_report(filepath, parens)


if __name__ == '__main__':
    main()
