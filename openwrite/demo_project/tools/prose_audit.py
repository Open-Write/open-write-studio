#!/usr/bin/env python3
"""
Prose audit tool for novel manuscript.
Detects AI tics and prose discipline violations per Section VII-N.
"""

import os
import sys
import re
import glob

MANUSCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "manuscript", "chapters")
CRITIC_DIR = os.path.join(os.path.dirname(__file__), "..", "critic_outputs")

# Tier 1 — Scrub on sight
TIER1_PATTERNS = [
    (r'\bnot just\b.*\bbut\b', "Not just X but Y construction"),
    (r'\bin a way that\b', "In a way that Z construction"),
    (r'\b(?:somewhat|perhaps|in some sense|almost as if)\b', "Hedge word"),
    (r'\b(?:she|he|they) (?:felt|thought|realized) that\b', "Interiority through telling"),
    (r'\bThere (?:was|is|were|are)\b', "Existential expletive"),
]

# Tier 2 — Flag and evaluate
TIER2_PATTERNS = [
    (r'\b—\s*\w+', "Em-dash followed by elaboration"),
    (r'\b\w+ly\b(?=\s+(?:said|asked|replied|whispered|shouted|muttered|exclaimed))', "Adverb in dialogue tag"),
    (r'\bsomething between\b.*\band\b', "Something between X and Y"),
]

# Literary clichés
CLICHE_PATTERNS = [
    (r'\bthe weight of grief\b', "Banned cliché"),
    (r'\bthe architecture of memory\b', "Banned cliché"),
    (r'\bthe geography of longing\b', "Banned cliché"),
    (r'\bthe texture of silence\b', "Banned cliché"),
    (r'\ba symphony of light\b', "Banned cliché (unless in Velai track where literally accurate)"),
    (r'\bthe space between heartbeats\b', "Banned cliché"),
    (r'\bthe quiet hum of\b', "Banned cliché"),
    (r'\bthe slow unfurling of\b', "Banned cliché"),
    (r'\btangled in\b', "Banned cliché"),
    (r'\bwoven through\b', "Banned cliché"),
    (r'\betched into\b', "Banned cliché"),
    (r'\bburned into\b', "Banned cliché"),
    (r'\bseared by\b', "Banned cliché"),
]

# Named emotion patterns (interiority failures)
INTERIORITY_PATTERNS = [
    (r'\b(?:she|he|they) felt (?:grief|sad|angry|afraid|happy|joy|sorrow|fear|pain|loss|love|hope|despair|rage|shame|guilt)\b', "Named emotion without rendering"),
    (r'\b(?:she|he|they) felt a (?:familiar|deep|sharp|vague|strange|sudden|quiet|heavy) (?:grief|sadness|anger|fear|joy|sorrow|pain|loss|love|hope|despair|rage|shame|guilt)\b', "Named emotion with qualifier"),
]


def audit_file(filepath):
    """Audit a single file for prose issues."""
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    findings = []
    is_velai_track = "_track_b_" in filepath.lower()

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("```") or stripped.startswith("---"):
            continue

        # Tier 1
        for pattern, desc in TIER1_PATTERNS:
            matches = re.finditer(pattern, stripped, re.IGNORECASE)
            for match in matches:
                # Skip "a symphony of light" in Velai track
                if "symphony of light" in match.group().lower() and is_velai_track:
                    continue
                findings.append({
                    "line": line_num,
                    "tier": 1,
                    "type": desc,
                    "text": match.group(),
                    "context": stripped[:100]
                })

        # Tier 2
        for pattern, desc in TIER2_PATTERNS:
            matches = re.finditer(pattern, stripped, re.IGNORECASE)
            for match in matches:
                findings.append({
                    "line": line_num,
                    "tier": 2,
                    "type": desc,
                    "text": match.group(),
                    "context": stripped[:100]
                })

        # Clichés
        for pattern, desc in CLICHE_PATTERNS:
            matches = re.finditer(pattern, stripped, re.IGNORECASE)
            for match in matches:
                # Skip "a symphony of light" in Velai track
                if "symphony of light" in match.group().lower() and is_velai_track:
                    continue
                findings.append({
                    "line": line_num,
                    "tier": "cliché",
                    "type": desc,
                    "text": match.group(),
                    "context": stripped[:100]
                })

        # Interiority
        for pattern, desc in INTERIORITY_PATTERNS:
            matches = re.finditer(pattern, stripped, re.IGNORECASE)
            for match in matches:
                findings.append({
                    "line": line_num,
                    "tier": "interiority",
                    "type": desc,
                    "text": match.group(),
                    "context": stripped[:100]
                })

    return findings


def check_sentence_length_monotony(filepath):
    """Check for 5+ consecutive sentences with similar lengths."""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # Split into sentences (rough approximation)
    sentences = re.split(r'[.!?]+\s+', text)
    sentences = [s.strip() for s in sentences if s.strip() and not s.strip().startswith('#')]

    findings = []
    window = 5
    for i in range(len(sentences) - window + 1):
        lengths = [len(s.split()) for s in sentences[i:i+window]]
        if all(abs(l - lengths[0]) <= 3 for l in lengths):
            findings.append({
                "line": "N/A",
                "tier": "rhythm",
                "type": "Metric monotony (5+ similar-length sentences)",
                "text": f"Sentences {i+1}-{i+window}: lengths {lengths}",
                "context": sentences[i][:80]
            })

    return findings


def main():
    if not os.path.exists(MANUSCRIPT_DIR):
        print(f"Error: Manuscript directory not found: {MANUSCRIPT_DIR}")
        sys.exit(1)

    chapters = glob.glob(os.path.join(MANUSCRIPT_DIR, "*.md"))
    if not chapters:
        print("No chapter files found.")
        return

    os.makedirs(CRITIC_DIR, exist_ok=True)

    for filepath in sorted(chapters):
        filename = os.path.basename(filepath)
        chapter_name = os.path.splitext(filename)[0]
        print(f"\nAuditing: {filename}")

        findings = audit_file(filepath)
        rhythm_findings = check_sentence_length_monotony(filepath)
        all_findings = findings + rhythm_findings

        tier1 = [f for f in all_findings if f["tier"] == 1]
        tier2 = [f for f in all_findings if f["tier"] == 2]
        cliches = [f for f in all_findings if f["tier"] == "cliché"]
        interiority = [f for f in all_findings if f["tier"] == "interiority"]
        rhythm = [f for f in all_findings if f["tier"] == "rhythm"]

        print(f"  Tier 1 (scrub): {len(tier1)}")
        print(f"  Tier 2 (flag): {len(tier2)}")
        print(f"  Clichés: {len(cliches)}")
        print(f"  Interiority: {len(interiority)}")
        print(f"  Rhythm: {len(rhythm)}")
        print(f"  Total: {len(all_findings)}")

        # Write report
        report_path = os.path.join(CRITIC_DIR, f"{chapter_name}_prose_audit.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Prose Audit: {filename}\n\n")
            f.write(f"## Summary\n")
            f.write(f"- Total violations: {len(all_findings)}\n")
            f.write(f"- Tier 1 (scrub on sight): {len(tier1)}\n")
            f.write(f"- Tier 2 (flag and evaluate): {len(tier2)}\n")
            f.write(f"- Cliché violations: {len(cliches)}\n")
            f.write(f"- Interiority failures: {len(interiority)}\n")
            f.write(f"- Rhythm violations: {len(rhythm)}\n\n")

            if all_findings:
                f.write(f"## Violations\n\n")
                for i, finding in enumerate(all_findings, 1):
                    f.write(f"{i}. **[Line {finding['line']}]** [{finding['type']}]\n")
                    f.write(f"   > {finding['context']}\n\n")
            else:
                f.write("## No violations found.\n")

        print(f"  Report: {report_path}")


if __name__ == "__main__":
    main()
