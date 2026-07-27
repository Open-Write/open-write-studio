#!/usr/bin/env python3
"""
Deterministic Lint Suite — Model-independent content lints for the completion gate.

Runs per chapter and on assembly. Every lint is deterministic: same input → same output.
These lints are the model-independent substitute for cross-model validation.

Usage:
    python tools/lint_suite.py --base-dir /path/to/project
    python tools/lint_suite.py --base-dir /path/to/project --chapter manuscript/chapters/001_the_altar.md
    python tools/lint_suite.py --base-dir /path/to/project --json
    python tools/lint_suite.py --base-dir /path/to/project --assembly manuscript/novel.md

Exit codes:
    0 — all lints pass
    1 — one or more lints failed
"""

import os
import sys
import re
import json
import hashlib
import argparse
import glob as globmod
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from .word_count import strip_artifacts, count_prose_words_from_text, _count_prose_text


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_chapter(path):
    """Read a chapter file, strip artifacts, return clean text."""
    with open(path, "r", encoding="utf-8-sig") as f:
        text = f.read()
    text = text.replace('\ufeff', '')
    return strip_artifacts(text)


def _normalize_sentence(s):
    """Normalize a sentence for near-duplicate comparison."""
    s = s.strip().lower()
    s = re.sub(r'[^\w\s]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s


def _split_sentences(text):
    """Split text into sentences (rough heuristic)."""
    # Split on sentence-ending punctuation followed by whitespace or end
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in parts if s.strip()]


def _word_count(text):
    return len(text.split())


# ---------------------------------------------------------------------------
# Lint 1: Exact + near-duplicate paragraph/sentence detection
# ---------------------------------------------------------------------------

def lint_duplicates(text, filepath="<string>"):
    """Detect exact duplicate paragraphs and near-duplicate sentences."""
    findings = []
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    # Exact duplicate paragraphs
    seen_paras = {}
    for i, p in enumerate(paragraphs):
        norm = _normalize_sentence(p)
        if len(norm) < 20:  # skip very short paragraphs
            continue
        if norm in seen_paras:
            findings.append({
                "lint": "duplicate_paragraph",
                "severity": "critical",
                "location": f"paragraph {i + 1}",
                "pattern": f"Exact duplicate of paragraph {seen_paras[norm] + 1}",
                "example": p[:120] + ("..." if len(p) > 120 else ""),
            })
        else:
            seen_paras[norm] = i

    # Near-duplicate sentences (>80% word overlap, both >8 words)
    sentences = _split_sentences(text)
    normalized = [_normalize_sentence(s) for s in sentences]
    for i in range(len(sentences)):
        if len(sentences[i].split()) < 8:
            continue
        for j in range(i + 1, len(sentences)):
            if len(sentences[j].split()) < 8:
                continue
            words_i = set(normalized[i].split())
            words_j = set(normalized[j].split())
            if not words_i or not words_j:
                continue
            overlap = len(words_i & words_j) / max(len(words_i), len(words_j))
            if overlap > 0.8 and normalized[i] != normalized[j]:
                findings.append({
                    "lint": "near_duplicate_sentence",
                    "severity": "moderate",
                    "location": f"sentences {i + 1} and {j + 1}",
                    "pattern": f"{overlap:.0%} word overlap",
                    "example": sentences[i][:80] + "..." + " / " + sentences[j][:80],
                })

    return findings


# ---------------------------------------------------------------------------
# Lint 2: Cross-chapter repeated-sentence / refrain cap
# ---------------------------------------------------------------------------

def lint_cross_chapter_repetition(chapter_files, threshold=3):
    """Flag any normalized sentence repeated across >threshold chapters."""
    findings = []
    sentence_to_chapters = {}

    for filepath in chapter_files:
        text = _read_chapter(filepath)
        sentences = _split_sentences(text)
        ch_name = os.path.basename(filepath)
        for s in sentences:
            norm = _normalize_sentence(s)
            if len(norm.split()) < 5:
                continue
            if norm not in sentence_to_chapters:
                sentence_to_chapters[norm] = set()
            sentence_to_chapters[norm].add(ch_name)

    for norm, chapters in sentence_to_chapters.items():
        if len(chapters) > threshold:
            findings.append({
                "lint": "cross_chapter_refrain",
                "severity": "critical",
                "location": f"{len(chapters)} chapters",
                "pattern": f"Sentence repeated across {len(chapters)} chapters (threshold: {threshold})",
                "example": norm[:120],
                "chapters": sorted(chapters),
            })

    return findings


# ---------------------------------------------------------------------------
# Lint 3: Negative-construction density per 1k words
# ---------------------------------------------------------------------------

NEGATIVE_PATTERNS = [
    r'\b(?:he|she|they|it)\s+(?:did|could|would|was|were|had|is|are|was not|were not|did not|could not|would not|had not)\s+not\b',
    r'\b(?:He|She|They|It)\s+(?:did|could|would|was|were|had|is|are)\s+not\b',
    r'\bnot\s+(?:a|the|an|his|her|their|its)\b',
    r'\bnever\b',
    r'\bnothing\b',
    r'\bno\s+(?:one|man|woman|child|thing|reason|way|place|time)\b',
    r'\bneither\b',
    r'\bnor\b',
    r'\bwithout\b',
]

# Specific high-density negative patterns (the AI tic)
NEGATIVE_TIC_PATTERNS = [
    r'(?:He|She|They)\s+(?:was|were|did|could|would|had)\s+(?:a|an|the|not)\s+\w+\.\s+(?:He|She|They)\s+(?:had|was|were|did|could|would)\s+',
    r'He\s+was\s+a\s+\w+\.\s+He\s+had\s+\w+\s+to\s+do\.',
    r'(?:He|She)\s+did\s+not\s+\w+\.\s+(?:He|She)\s+(?:could|would|had)\s+not\s+\w+\.',
]


def lint_negative_construction(text, filepath="<string>"):
    """Flag excessive negative-construction density."""
    findings = []
    word_count = _word_count(text)
    if word_count == 0:
        return findings

    neg_count = 0
    for pat in NEGATIVE_PATTERNS:
        neg_count += len(re.findall(pat, text, re.IGNORECASE))

    density = (neg_count / word_count) * 1000

    # Threshold: >15 negative constructions per 1k words is excessive
    if density > 15:
        findings.append({
            "lint": "negative_construction_density",
            "severity": "critical" if density > 25 else "moderate",
            "location": "whole chapter",
            "pattern": f"{neg_count} negative constructions in {word_count} words ({density:.1f}/1k)",
            "example": "",
        })
    elif density > 10:
        findings.append({
            "lint": "negative_construction_density",
            "severity": "minor",
            "location": "whole chapter",
            "pattern": f"{neg_count} negative constructions in {word_count} words ({density:.1f}/1k)",
            "example": "",
        })

    # Detect specific negative-construction tic loops
    tic_matches = []
    for pat in NEGATIVE_TIC_PATTERNS:
        tic_matches.extend(re.findall(pat, text, re.IGNORECASE))
    if len(tic_matches) >= 3:
        findings.append({
            "lint": "negative_tic_loop",
            "severity": "critical",
            "location": "multiple",
            "pattern": f"{len(tic_matches)} instances of negative-construction tic pattern",
            "example": tic_matches[0][:120] if tic_matches else "",
        })

    return findings


# ---------------------------------------------------------------------------
# Lint 4: Banned constructions
# ---------------------------------------------------------------------------

BANNED_CONSTRUCTIONS = [
    (r'\bNot\s+\w+\s+but\s+\w+', "not_X_but_Y"),
    (r'\bNot\s+\w+\.\s+Not\s+\w+\.\s+\w+\.', "not_X_not_Y_Z"),
    (r'(?:There\s+was|There\s+were|There\s+is|There\s+are)\b', "expletive_there"),
    (r'\b(?:grief|horror|devastation|elation|fury|despair|joy|terror|awe|wonder|longing)\b'
     r'(?:\s+(?:hit|struck|overwhelmed|consumed|filled|washed over|gripped|seized))',
     "named_emotion_verb"),
    (r'(?:felt|was overcome with|was filled with|was consumed by)\s+'
     r'(?:grief|horror|devastation|elation|fury|despair|joy|terror|awe|wonder|longing|anger|sadness|fear|happiness)',
     "named_emotion_construction"),
]

# Triplet closing: 3 consecutive sentences of <=6 words
TRIPLET_PATTERN = re.compile(
    r'(?:^|\n)(.{1,60}?)\.\s*\n(.{1,60}?)\.\s*\n(.{1,60}?)\.\s*(?:\n|$)',
    re.MULTILINE
)


def lint_banned_constructions(text, filepath="<string>"):
    """Flag banned constructions from the format rules."""
    findings = []

    for pattern, name in BANNED_CONSTRUCTIONS:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        for m in matches[:5]:  # limit to 5 examples per pattern
            line_num = text[:m.start()].count('\n') + 1
            findings.append({
                "lint": f"banned_{name}",
                "severity": "critical" if name in ("not_X_but_Y", "named_emotion_construction") else "moderate",
                "location": f"line {line_num}",
                "pattern": f"Banned construction: {name}",
                "example": m.group()[:100],
            })

    # Triplet closings
    triplet_matches = list(TRIPLET_PATTERN.finditer(text))
    if len(triplet_matches) >= 3:
        findings.append({
            "lint": "triplet_closing_pattern",
            "severity": "critical",
            "location": f"{len(triplet_matches)} instances",
            "pattern": f"Triplet closing pattern: {len(triplet_matches)} instances (threshold: 3)",
            "example": triplet_matches[0].group()[:100],
        })
    elif len(triplet_matches) == 2:
        findings.append({
            "lint": "triplet_closing_pattern",
            "severity": "moderate",
            "location": "2 instances",
            "pattern": "Triplet closing pattern: 2 instances",
            "example": triplet_matches[0].group()[:100],
        })

    return findings


# ---------------------------------------------------------------------------
# Lint 5: Anti-padding detection
# ---------------------------------------------------------------------------

ROUND_NUMBER_TOLERANCE = 25  # words


def lint_padding(text, filepath="<string>"):
    """Flag chapters landing suspiciously close to round numbers."""
    findings = []
    wc = _word_count(text)

    # Check proximity to round numbers (500, 1000, 1500, 2000, 2500, 3000, etc.)
    round_numbers = list(range(500, 50001, 500))
    for rn in round_numbers:
        if abs(wc - rn) <= ROUND_NUMBER_TOLERANCE and wc > 400:
            findings.append({
                "lint": "round_number_landing",
                "severity": "moderate",
                "location": "chapter",
                "pattern": f"Word count {wc} is within {ROUND_NUMBER_TOLERANCE} of round number {rn}",
                "example": "",
            })
            break  # only flag once per chapter

    return findings


# ---------------------------------------------------------------------------
# Lint 6: Named real public figures
# ---------------------------------------------------------------------------

# Known real historical figures from the project domain
KNOWN_FIGURES = [
    (r'\bBishop\s+M[úu]gica\b', "Bishop Múgica — real Bishop of Vitoria who resisted Franco"),
    (r'\bMateo\s+M[úu]gica\b', "Mateo Múgica — real Bishop of Vitoria who resisted Franco"),
    (r'\bFrancisco\s+Franco\b', "Francisco Franco — real historical figure"),
    (r'\bFranco\b', "Franco — real historical figure"),
    (r'\bHitler\b', "Adolf Hitler — real historical figure"),
    (r'\bMussolini\b', "Benito Mussolini — real historical figure"),
]


def lint_named_figures(text, filepath="<string>"):
    """Flag named real public figures and require accuracy note."""
    findings = []

    for pattern, description in KNOWN_FIGURES:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        if matches:
            line_num = text[:matches[0].start()].count('\n') + 1
            findings.append({
                "lint": "named_figure",
                "severity": "info",
                "location": f"line {line_num}",
                "pattern": f"Named real figure: {description}",
                "example": matches[0].group()[:80],
            })

    return findings


# ---------------------------------------------------------------------------
# Lint 7: Scene-completeness heuristic
# ---------------------------------------------------------------------------

def lint_scene_completeness(text, filepath="<string>"):
    """Heuristic check: is this chapter rendered scene or pure summary?"""
    findings = []
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    word_count = _word_count(text)

    if word_count < 200:
        return findings  # too short to evaluate

    # Count dialogue lines (lines starting with " or containing dialogue markers)
    dialogue_words = 0
    for p in paragraphs:
        lines = p.split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('"') or stripped.startswith('"') or stripped.startswith('*"'):
                dialogue_words += len(stripped.split())

    # Count body-anchor words (physical detail indicators)
    body_anchor_patterns = [
        r'\b(?:hand|hands|finger|fingers|fist|fist|palm|palms)\b',
        r'\b(?:eye|eyes|gaze|stare|glance|look|looked|seeing)\b',
        r'\b(?:breath|breathe|breathing|exhale|inhale|gasp|gasp|cough)\b',
        r'\b(?:spine|back|shoulder|shoulders|neck|throat)\b',
        r'\b(?:jaw|chin|lip|lips|mouth|tongue|teeth)\b',
        r'\b(?:foot|feet|knee|knees|leg|legs|step|stepped)\b',
        r'\b(?:head|hair|forehead|brow|cheek|cheeks|face)\b',
        r'\b(?:skin|bone|blood|flesh|muscle|wound|scar)\b',
        r'\b(?:heart|chest|lung|stomach|gut|belly)\b',
        r'\b(?:sound|noise|silence|voice|whisper|shout|cry)\b',
        r'\b(?:cold|warm|hot|cool|wet|dry|rough|smooth|sharp|dull|heavy|light)\b',
        r'\b(?:smell|scent|odor|stink|fragrance|taste|touch)\b',
        r'\b(?:see|saw|seen|hear|heard|feel|felt|touch|touched|smell|smelled)\b',
    ]

    body_anchored = 0
    for pat in body_anchor_patterns:
        body_anchored += len(re.findall(pat, text, re.IGNORECASE))

    total_sentences = len(_split_sentences(text))
    dialogue_ratio = dialogue_words / word_count if word_count > 0 else 0
    body_density = (body_anchored / word_count) * 1000 if word_count > 0 else 0

    # Pure summary detection: very little dialogue AND very few body anchors
    if dialogue_ratio < 0.05 and body_density < 5 and word_count > 800:
        findings.append({
            "lint": "pure_summary",
            "severity": "critical",
            "location": "chapter",
            "pattern": f"Chapter appears to be pure summary: dialogue ratio {dialogue_ratio:.1%}, body-anchor density {body_density:.1f}/1k words",
            "example": "",
        })
    elif dialogue_ratio < 0.1 and body_density < 8 and word_count > 800:
        findings.append({
            "lint": "low_rendering",
            "severity": "moderate",
            "location": "chapter",
            "pattern": f"Chapter has low rendering: dialogue ratio {dialogue_ratio:.1%}, body-anchor density {body_density:.1f}/1k words",
            "example": "",
        })

    return findings


# ---------------------------------------------------------------------------
# Lint 8: Em-dash overuse (quantitative)
# ---------------------------------------------------------------------------

def lint_emdash(text, filepath="<string>"):
    """Flag em-dash overuse per the naturalism critic threshold."""
    findings = []
    word_count = _word_count(text)
    if word_count == 0:
        return findings

    emdash_count = text.count('—') + text.count('--')
    pages = word_count / 250
    rate = emdash_count / pages if pages > 0 else 0

    if rate > 5:
        findings.append({
            "lint": "emdash_overuse",
            "severity": "critical",
            "location": "chapter",
            "pattern": f"{emdash_count} em-dashes in {pages:.1f} pages ({rate:.1f}/page, threshold: 2)",
            "example": "",
        })
    elif rate > 2:
        findings.append({
            "lint": "emdash_overuse",
            "severity": "moderate",
            "location": "chapter",
            "pattern": f"{emdash_count} em-dashes in {pages:.1f} pages ({rate:.1f}/page, threshold: 2)",
            "example": "",
        })

    return findings


# ---------------------------------------------------------------------------
# Lint 9: Refrain repetition within a single chapter
# ---------------------------------------------------------------------------

def lint_refrain_within_chapter(text, filepath="<string>"):
    """Flag any sentence repeated 3+ times within a single chapter."""
    findings = []
    sentences = _split_sentences(text)
    normalized = [_normalize_sentence(s) for s in sentences]

    counts = Counter()
    first_pos = {}
    for i, norm in enumerate(normalized):
        if len(norm.split()) < 5:
            continue
        counts[norm] += 1
        if norm not in first_pos:
            first_pos[norm] = i

    for norm, count in counts.items():
        if count >= 3:
            findings.append({
                "lint": "intra_chapter_refrain",
                "severity": "critical" if count >= 5 else "moderate",
                "location": f"first at sentence {first_pos[norm] + 1}",
                "pattern": f"Sentence repeated {count} times within chapter",
                "example": norm[:120],
            })

    return findings


# ---------------------------------------------------------------------------
# Critic artifact validation
# ---------------------------------------------------------------------------

LOCATED_FINDING_PATTERN = re.compile(
    r'(?:'
    r'(?:Line|line|Lines|lines)\s*\d+'       # Line N
    r'|(?:paragraph|Paragraph)\s*\d+'         # paragraph N
    r'|(?:page|Page)\s*\d+'                   # page N
    r'|(?:chapter|Chapter)\s*\d+'             # chapter N
    r'|"[^"]{10,}"'                           # quoted text >= 10 chars
    r'|>[^>]{10,}'                            # blockquote text
    r'|(?:Location|location|Loc|loc)[:\s]'    # Location: field
    r'|(?:Text|text)[:\s]*"'                  # Text: "..." field
    r'|(?:Passage|passage|Example|example)[:\s]' # Example: field
    r')'
)


def validate_critic_artifact(filepath):
    """Validate that a critic/editorial file contains located findings, not just PASS assertions."""
    issues = []

    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            content = f.read()
    except Exception:
        issues.append(f"READ_ERROR: Cannot read {filepath}")
        return issues

    content_lower = content.lower()

    # Count located findings
    finding_count = len(LOCATED_FINDING_PATTERN.findall(content))

    # Check for bare PASS/ADVANCE with zero findings
    has_pass = bool(re.search(r'\b(?:PASS|ADVANCE|CLEAN|NATURAL)\b', content, re.IGNORECASE))
    has_findings_section = bool(re.search(r'(?:##|###)\s*(?:Violations?|Findings?|Issues?|Flags?|Problems?|Weaknesses)', content, re.IGNORECASE))

    if has_pass and finding_count == 0 and not has_findings_section:
        issues.append(
            f"EMPTY_VERDICT: {os.path.basename(filepath)} asserts PASS/ADVANCE "
            f"with zero located findings — this is a hollow critic pass"
        )

    # Check minimum content length (a real review is >200 words)
    word_count = len(content.split())
    if word_count < 100:
        issues.append(
            f"TOO_SHORT: {os.path.basename(filepath)} is only {word_count} words — "
            f"a real review requires substantive analysis"
        )

    return issues


def validate_critic_hash_binding(filepath, chapter_hash_map):
    """Validate that a critic artifact references the current chapter hash."""
    issues = []

    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            content = f.read()
    except Exception:
        return issues

    # Look for embedded chapter hash
    hash_match = re.search(r'chapter_hash[:\s]*([a-f0-9]{64})', content, re.IGNORECASE)
    if hash_match:
        embedded_hash = hash_match.group(1)
        # Check if this hash matches any known chapter
        for ch_path, ch_hash in chapter_hash_map.items():
            if embedded_hash == ch_hash:
                return issues  # hash matches — artifact is current
        # If we get here, the hash doesn't match any current chapter
        issues.append(
            f"STALE_ARTIFACT: {os.path.basename(filepath)} references chapter hash "
            f"{embedded_hash[:16]}... which doesn't match any current chapter — "
            f"chapter was revised but this artifact wasn't updated"
        )

    return issues


# ---------------------------------------------------------------------------
# Chapter hashing
# ---------------------------------------------------------------------------

def hash_chapter(filepath):
    """Compute SHA-256 hash of a chapter's clean (artifact-stripped) content."""
    text = _read_chapter(filepath)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hash_all_chapters(base_dir):
    """Hash all chapter files. Returns dict of {rel_path: hash}."""
    chapters_dir = os.path.join(base_dir, "manuscript")
    if not os.path.isdir(chapters_dir):
        return {}

    result = {}
    files = sorted(f for f in globmod.glob(os.path.join(chapters_dir, "*.md"))
                   if os.path.basename(f) != "novel.md")
    real_base = os.path.realpath(base_dir)

    for f in files:
        if not os.path.realpath(f).startswith(real_base + os.sep):
            continue
        rel = os.path.relpath(f, base_dir)
        result[rel] = hash_chapter(f)

    return result


# ---------------------------------------------------------------------------
# Full lint run
# ---------------------------------------------------------------------------

def run_lints_on_chapter(filepath, chapter_hash=None):
    """Run all per-chapter lints on a single file. Returns list of findings."""
    text = _read_chapter(filepath)
    all_findings = []

    all_findings.extend(lint_duplicates(text, filepath))
    all_findings.extend(lint_negative_construction(text, filepath))
    all_findings.extend(lint_banned_constructions(text, filepath))
    all_findings.extend(lint_padding(text, filepath))
    all_findings.extend(lint_named_figures(text, filepath))
    all_findings.extend(lint_scene_completeness(text, filepath))
    all_findings.extend(lint_emdash(text, filepath))
    all_findings.extend(lint_refrain_within_chapter(text, filepath))

    # Add hash to findings metadata
    if chapter_hash:
        for f in all_findings:
            f["chapter_hash"] = chapter_hash

    return all_findings


def run_lints_on_assembly(filepath):
    """Run lints on the assembled manuscript."""
    text = _read_chapter(filepath)
    all_findings = []

    all_findings.extend(lint_duplicates(text, filepath))
    all_findings.extend(lint_negative_construction(text, filepath))
    all_findings.extend(lint_banned_constructions(text, filepath))
    all_findings.extend(lint_emdash(text, filepath))
    all_findings.extend(lint_refrain_within_chapter(text, filepath))

    return all_findings


def run_full_lint_suite(base_dir, json_output=False):
    """Run the complete lint suite on all chapters and assembly."""
    all_findings = {}
    chapter_hashes = hash_all_chapters(base_dir)

    # Per-chapter lints
    for rel_path, ch_hash in chapter_hashes.items():
        full_path = os.path.join(base_dir, rel_path)
        findings = run_lints_on_chapter(full_path, ch_hash)
        if findings:
            all_findings[rel_path] = findings

    # Cross-chapter lints
    chapter_files = [os.path.join(base_dir, p) for p in sorted(chapter_hashes.keys())]
    if len(chapter_files) > 1:
        cross_findings = lint_cross_chapter_repetition(chapter_files)
        if cross_findings:
            all_findings["_cross_chapter"] = cross_findings

    # Assembly lints
    assembly_candidates = [
        os.path.join(base_dir, "manuscript", "novel.md"),
        os.path.join(base_dir, "manuscript", "season.md"),
    ]
    for asm in assembly_candidates:
        if os.path.isfile(asm):
            asm_findings = run_lints_on_assembly(asm)
            if asm_findings:
                all_findings[f"_assembly:{os.path.basename(asm)}"] = asm_findings

    # Critic artifact validation
    critic_dir = os.path.join(base_dir, "critic_outputs")
    coverage_dir = os.path.join(base_dir, "coverage_reports")
    critic_issues = {}

    for d in [critic_dir, coverage_dir]:
        if os.path.isdir(d):
            for fname in sorted(os.listdir(d)):
                if not fname.endswith(".md"):
                    continue
                fpath = os.path.join(d, fname)
                issues = validate_critic_artifact(fpath)
                hash_issues = validate_critic_hash_binding(fpath, chapter_hashes)
                all_issues = issues + hash_issues
                if all_issues:
                    critic_issues[fname] = all_issues

    if critic_issues:
        all_findings["_critic_validation"] = critic_issues

    # Summary
    total_findings = 0
    critical_count = 0
    for key, findings in all_findings.items():
        if isinstance(findings, list):
            for f in findings:
                if isinstance(f, dict):
                    total_findings += 1
                    if f.get("severity") == "critical":
                        critical_count += 1
        elif isinstance(findings, dict):
            for fname, issues in findings.items():
                total_findings += len(issues)

    result = {
        "verdict": "PASS" if total_findings == 0 else "FAIL",
        "total_findings": total_findings,
        "critical_findings": critical_count,
        "chapter_hashes": chapter_hashes,
        "findings": all_findings,
    }

    if json_output:
        print(json.dumps(result, indent=2))
    else:
        print(f"{'='*70}")
        print(f"LINT SUITE RESULTS")
        print(f"{'='*70}")
        print(f"  Verdict: {result['verdict']}")
        print(f"  Total findings: {total_findings}")
        print(f"  Critical: {critical_count}")
        print(f"  Chapters scanned: {len(chapter_hashes)}")
        print()

        if all_findings:
            for key, findings in all_findings.items():
                print(f"  --- {key} ---")
                if isinstance(findings, list):
                    for f in findings:
                        if isinstance(f, dict):
                            sev = f.get("severity", "?").upper()
                            lint = f.get("lint", "?")
                            loc = f.get("location", "?")
                            pat = f.get("pattern", "")
                            print(f"    [{sev}] {lint} @ {loc}: {pat}")
                elif isinstance(findings, dict):
                    for fname, issues in findings.items():
                        for issue in issues:
                            print(f"    {fname}: {issue}")
                print()

        print(f"{'='*70}")
        print(f"LINT VERDICT: {result['verdict']}")
        print(f"{'='*70}")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Deterministic lint suite")
    parser.add_argument("--base-dir", default=None, help="Project base directory")
    parser.add_argument("--chapter", default=None, help="Lint a single chapter file")
    parser.add_argument("--assembly", default=None, help="Lint the assembly file")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--hash-only", action="store_true", help="Only output chapter hashes")
    args = parser.parse_args()

    base_dir = args.base_dir or os.getcwd()

    if args.hash_only:
        hashes = hash_all_chapters(base_dir)
        if args.json:
            print(json.dumps(hashes, indent=2))
        else:
            for path, h in hashes.items():
                print(f"  {path}: {h[:16]}...")
        sys.exit(0)

    if args.chapter:
        findings = run_lints_on_chapter(args.chapter)
        if args.json:
            print(json.dumps(findings, indent=2))
        else:
            for f in findings:
                sev = f.get("severity", "?").upper()
                print(f"  [{sev}] {f.get('lint', '?')} @ {f.get('location', '?')}: {f.get('pattern', '')}")
        sys.exit(0 if not findings else 1)

    if args.assembly:
        findings = run_lints_on_assembly(args.assembly)
        if args.json:
            print(json.dumps(findings, indent=2))
        else:
            for f in findings:
                sev = f.get("severity", "?").upper()
                print(f"  [{sev}] {f.get('lint', '?')} @ {f.get('location', '?')}: {f.get('pattern', '')}")
        sys.exit(0 if not findings else 1)

    result = run_full_lint_suite(base_dir, args.json)
    sys.exit(0 if result["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
