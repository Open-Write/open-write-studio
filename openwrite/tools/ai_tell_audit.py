#!/usr/bin/env python3
"""
AI Tell Audit Tool for Screenplay
Detects patterns commonly associated with AI-generated text:
  - Em-dash density (per-page)
  - Triplet closing patterns (3+ short consecutive sentences)
  - Sentence length uniformity (low coefficient of variation)
  - Paragraph structure uniformity
  - Negation-action sentence pairs
  - Repeated sentence openers

Usage:
    python tools/ai_tell_audit.py script/scenes/01_cold_open.fountain
    python tools/ai_tell_audit.py --all
    python tools/ai_tell_audit.py --assembled                # Audit screenplay.fountain
"""

import re
import sys
import os
import glob
import json
from collections import Counter


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# Em dash: literal — or Fountain double-hyphen --
EM_DASH_RE = re.compile(r'\u2014|--')

# En dash for ranges (do NOT count these)
EN_DASH_RE = re.compile(r'\u2013(?=\d)')

# Slug line pattern (Fountain)
SLUG_RE = re.compile(r'^(INT\.|EXT\.|INT/EXT\.|I/E\.)', re.IGNORECASE)

# Character name in caps (Fountain) — all caps, short, possibly with ^ for dual dialogue
CHARACTER_RE = re.compile(r'^[A-Z][A-Z\s\.\'\-]+(\s*\^)?$')

# Title page keys (Fountain title page uses Key: Value pairs)
TITLE_KEY_RE = re.compile(r'^(Title|Author|Draft date|Contact|Copyright|Notes|Source|Format|Language):', re.IGNORECASE)

# Transition lines (Fountain)
TRANSITION_RE = re.compile(r'^(FADE IN:|FADE OUT\.|CUT TO:|SMASH CUT TO:|DISSOLVE TO:|BLACK\.|WHITE\.)\s*$', re.IGNORECASE)

# Words: any sequence of word characters or apostrophes
WORD_RE = re.compile(r"[\w\u2019']+")

# Sentence ending punctuation
SENTENCE_END_RE = re.compile(r'[.!?]["\u201c\u201d\u2018\u2019\u2014]*\s*$')

# Negation-action pattern: "X doesn't [verb]. [Subject] [verb]s."
NEGATION_ACTION_RE = re.compile(
    r"(\w+)\s+(?:doesn't|don't|didn't|won't|can't|couldn't|wouldn't|isn't|aren't|wasn't)\s+\w+[.!]",
    re.IGNORECASE
)


# ---------------------------------------------------------------------------
# Page estimation
# ---------------------------------------------------------------------------

# Industry standard: ~56 lines per screenplay page (Fountain)
LINES_PER_PAGE = 56


def estimate_pages(lines):
    """Estimate page count from line count."""
    return max(1, len(lines) / LINES_PER_PAGE)


# ---------------------------------------------------------------------------
# Em-dash analysis
# ---------------------------------------------------------------------------

def count_em_dashes(text):
    """Count em dashes (— and --), excluding en dashes used for ranges."""
    # Remove en dashes used for ranges before counting
    cleaned = EN_DASH_RE.sub('', text)
    return len(EM_DASH_RE.findall(cleaned))


def em_dash_per_page(lines):
    """Calculate em-dash density per page."""
    text = '\n'.join(lines)
    total = count_em_dashes(text)
    pages = estimate_pages(lines)
    density = total / pages
    return total, pages, density


def em_dash_verdict(density):
    """Classify em-dash density."""
    if density > 5:
        return 'FAIL', f'{density:.1f}/page — Critical: immediately signals AI generation'
    elif density > 2:
        return 'WARN', f'{density:.1f}/page — Above human-normal frequency'
    else:
        return 'PASS', f'{density:.1f}/page — Within human-normal range'


# ---------------------------------------------------------------------------
# Triplet closing pattern
# ---------------------------------------------------------------------------

def is_fountain_metadata(line):
    """Check if a line is Fountain metadata that should be excluded from prose analysis."""
    stripped = line.strip()
    if not stripped:
        return True
    if SLUG_RE.match(stripped):
        return True
    if CHARACTER_RE.match(stripped) and len(stripped) < 40:
        return True
    if TRANSITION_RE.match(stripped):
        return True
    if stripped.startswith('(') and stripped.endswith(')'):
        return True  # Parenthetical
    if stripped.startswith('===') or stripped.startswith('---'):
        return True
    if stripped.startswith('#'):
        return True
    # Boneyard and synopses
    if stripped.startswith('/*') or stripped.startswith('*/'):
        return True
    if stripped.startswith('='):
        return True
    return False


def extract_sentences(text):
    """Split text into sentences from Fountain body lines.

    In Fountain, each non-blank line is often its own beat.
    We treat each non-metadata line as a sentence candidate,
    then further split lines that contain multiple sentences
    (e.g., 'Yes. It is our medium too. That is new.')
    """
    # First pass: filter to prose-only lines
    prose_lines = []
    for line in text.split('\n'):
        if not is_fountain_metadata(line):
            prose_lines.append(line.strip())

    # Second pass: join and split into sentences
    cleaned = ' '.join(prose_lines)

    # Protect abbreviations
    cleaned = re.sub(r'\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr|St|vs|etc|i\.e|e\.g)\.',
                     r'\1<PERIOD>', cleaned)

    # Split on sentence-ending punctuation followed by whitespace
    raw_sentences = re.split(r'(?<=[.!?])\s+', cleaned)

    # Restore abbreviations and clean
    sentences = []
    for s in raw_sentences:
        s = s.replace('<PERIOD>', '.').strip()
        if s and len(s) > 1:  # Skip single punctuation
            sentences.append(s)

    return sentences


def extract_prose_lines(text):
    """Extract non-metadata Fountain lines as individual prose units.
    Unlike extract_sentences, this preserves line-level granularity
    for em-dash counting and paragraph analysis."""
    prose_lines = []
    for line in text.split('\n'):
        if not is_fountain_metadata(line):
            prose_lines.append(line.strip())
    return [l for l in prose_lines if l]


def sentence_word_count(sentence):
    """Count words in a sentence, excluding punctuation-only tokens."""
    return len(WORD_RE.findall(sentence))


def find_triplet_patterns(sentences, max_words=6):
    """Find passages where 3+ consecutive sentences have max_words or fewer."""
    triplets = []
    i = 0
    while i < len(sentences) - 2:
        # Check if sentences i, i+1, i+2 are all short
        counts = []
        j = i
        while j < len(sentences) and sentence_word_count(sentences[j]) <= max_words:
            counts.append(sentence_word_count(sentences[j]))
            j += 1

        if len(counts) >= 3:
            triplets.append({
                'start_index': i,
                'count': len(counts),
                'sentences': sentences[i:j],
                'word_counts': counts
            })
            i = j  # Skip past this triplet
        else:
            i += 1

    return triplets


# ---------------------------------------------------------------------------
# Sentence length uniformity
# ---------------------------------------------------------------------------

def sentence_length_stats(sentences):
    """Compute sentence length statistics."""
    lengths = [sentence_word_count(s) for s in sentences]
    lengths = [l for l in lengths if l > 0]

    if not lengths:
        return {'count': 0, 'mean': 0, 'std': 0, 'cv': 0, 'min': 0, 'max': 0}

    mean = sum(lengths) / len(lengths)
    variance = sum((l - mean) ** 2 for l in lengths) / len(lengths) if len(lengths) > 1 else 0
    std = variance ** 0.5
    cv = std / mean if mean > 0 else 0

    return {
        'count': len(lengths),
        'mean': round(mean, 1),
        'std': round(std, 1),
        'cv': round(cv, 2),
        'min': min(lengths),
        'max': max(lengths)
    }


def sentence_length_verdict(cv):
    """Classify sentence length variation. Low CV = uniform = AI-like."""
    if cv < 0.35:
        return 'FAIL', f'CV={cv:.2f} — Sentences are suspiciously uniform in length'
    elif cv < 0.50:
        return 'WARN', f'CV={cv:.2f} — Sentence lengths are somewhat uniform'
    else:
        return 'PASS', f'CV={cv:.2f} — Good variation in sentence length'


# ---------------------------------------------------------------------------
# Paragraph structure uniformity
# ---------------------------------------------------------------------------

def paragraph_lengths(text):
    """Get the sentence count per paragraph."""
    paragraphs = re.split(r'\n\s*\n', text)
    counts = []
    for p in paragraphs:
        p = p.strip()
        if not p or p == '---':
            continue
        # Skip slug lines, character names
        if SLUG_RE.match(p) or CHARACTER_RE.match(p):
            continue
        if p.startswith('#') or p.startswith('==='):
            continue
        sents = extract_sentences(p)
        if sents:
            counts.append(len(sents))
    return counts


def paragraph_uniformity_verdict(counts):
    """Check if paragraph lengths are too uniform."""
    if len(counts) < 3:
        return 'PASS', 'Too few paragraphs to assess'

    most_common = Counter(counts).most_common(1)[0]
    dominant_length, dominant_count = most_common
    ratio = dominant_count / len(counts)

    if ratio > 0.7:
        return 'FAIL', f'{ratio:.0%} of paragraphs are exactly {dominant_length} sentences — structural uniformity'
    elif ratio > 0.5:
        return 'WARN', f'{ratio:.0%} of paragraphs are {dominant_length} sentences — approaching uniformity'
    else:
        return 'PASS', f'Paragraph lengths are varied (most common: {dominant_length} at {ratio:.0%})'


# ---------------------------------------------------------------------------
# Negation-action pattern
# ---------------------------------------------------------------------------

def find_negation_action_pairs(sentences):
    """Find consecutive negation-action sentence pairs."""
    pairs = []
    for i in range(len(sentences) - 1):
        s1 = sentences[i].strip()
        s2 = sentences[i + 1].strip()

        # Check: sentence 1 contains a negation verb
        if NEGATION_ACTION_RE.search(s1):
            # Check: sentence 2 starts with a pronoun or character name doing something
            if re.match(r'^(She|He|They|It|Mira|Daniel|Theo|Okafor|Thorn)\s+\w+s?\b', s2, re.IGNORECASE):
                pairs.append({
                    'index': i,
                    'negation': s1,
                    'action': s2
                })

    return pairs


# ---------------------------------------------------------------------------
# Repeated sentence openers
# ---------------------------------------------------------------------------

def sentence_opener_analysis(sentences):
    """Find repeated sentence openers (first 2 words)."""
    openers = []
    for s in sentences:
        words = WORD_RE.findall(s)
        if len(words) >= 2:
            openers.append(f"{words[0]} {words[1]}".lower())
        elif words:
            openers.append(words[0].lower())

    counter = Counter(openers)
    repeated = {k: v for k, v in counter.items() if v >= 3}
    return repeated


# ---------------------------------------------------------------------------
# Full audit
# ---------------------------------------------------------------------------

def audit_fountain(filepath):
    """Run full AI-tell audit on a Fountain file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return None, f"File not found: {filepath}"

    lines = content.split('\n')

    # Skip title page: Fountain title page ends at the first blank line
    # after Key: Value pairs, OR at the first scene heading / transition
    in_title = True
    body_lines = []
    seen_non_blank = False
    for line in lines:
        stripped = line.strip()
        if in_title:
            if TITLE_KEY_RE.match(stripped):
                seen_non_blank = True
                continue
            # Title page ends at first blank line after we've seen keys,
            # or at any line that looks like body content
            if not stripped:
                if seen_non_blank:
                    in_title = False
                continue
            # If it's not a title key and not blank, we've left the title page
            if not TITLE_KEY_RE.match(stripped):
                in_title = False
        body_lines.append(line)

    body_text = '\n'.join(body_lines)

    # Extract sentences from body text
    all_sentences = extract_sentences(body_text)

    # --- Em-dash analysis ---
    em_total, em_pages, em_density = em_dash_per_page(body_lines)
    em_verdict, em_detail = em_dash_verdict(em_density)

    # --- Triplet pattern ---
    triplets = find_triplet_patterns(all_sentences)
    triplet_verdict = 'PASS'
    triplet_detail = f'{len(triplets)} triplet patterns found'
    if len(triplets) >= 3:
        triplet_verdict = 'FAIL'
        triplet_detail = f'{len(triplets)} triplet patterns — mechanical rhythm'
    elif len(triplets) >= 2:
        triplet_verdict = 'WARN'
        triplet_detail = f'{len(triplets)} triplet patterns — approaching mechanical'

    # --- Sentence length uniformity ---
    sent_stats = sentence_length_stats(all_sentences)
    sl_verdict, sl_detail = sentence_length_verdict(sent_stats['cv'])

    # --- Paragraph uniformity ---
    para_counts = paragraph_lengths(body_text)
    para_verdict, para_detail = paragraph_uniformity_verdict(para_counts)

    # --- Negation-action pairs ---
    neg_pairs = find_negation_action_pairs(all_sentences)
    neg_verdict = 'PASS'
    neg_detail = f'{len(neg_pairs)} negation-action pairs'
    if len(neg_pairs) >= 3:
        neg_verdict = 'WARN'
        neg_detail = f'{len(neg_pairs)} negation-action pairs — pattern emerging'

    # --- Repeated openers ---
    repeated_openers = sentence_opener_analysis(all_sentences)
    opener_verdict = 'PASS'
    opener_detail = 'No significantly repeated openers'
    if repeated_openers:
        worst = max(repeated_openers.items(), key=lambda x: x[1])
        opener_detail = f'Most repeated opener: "{worst[0]}" ({worst[1]}x)'
        if worst[1] >= 5:
            opener_verdict = 'WARN'

    # --- Overall verdict ---
    findings = [em_verdict, triplet_verdict, sl_verdict, para_verdict, neg_verdict, opener_verdict]
    fail_count = findings.count('FAIL')
    warn_count = findings.count('WARN')

    if fail_count >= 2:
        overall = 'MECHANICAL'
    elif fail_count >= 1 or warn_count >= 3:
        overall = 'NEEDS REVISION'
    else:
        overall = 'NATURAL'

    return {
        'file': os.path.basename(filepath),
        'overall_verdict': overall,
        'metrics': {
            'em_dashes': {
                'total': em_total,
                'pages': round(em_pages, 1),
                'density_per_page': round(em_density, 1),
                'verdict': em_verdict,
                'detail': em_detail
            },
            'triplet_patterns': {
                'count': len(triplets),
                'verdict': triplet_verdict,
                'detail': triplet_detail,
                'instances': [
                    {'sentences': t['sentences'], 'word_counts': t['word_counts']}
                    for t in triplets[:5]  # Cap at 5 for report
                ]
            },
            'sentence_length': {
                **sent_stats,
                'verdict': sl_verdict,
                'detail': sl_detail
            },
            'paragraph_uniformity': {
                'count': len(para_counts),
                'verdict': para_verdict,
                'detail': para_detail,
                'distribution': dict(Counter(para_counts).most_common(5))
            },
            'negation_action': {
                'count': len(neg_pairs),
                'verdict': neg_verdict,
                'detail': neg_detail,
                'instances': [
                    {'negation': p['negation'], 'action': p['action']}
                    for p in neg_pairs[:5]
                ]
            },
            'repeated_openers': {
                'count': len(repeated_openers),
                'verdict': opener_verdict,
                'detail': opener_detail,
                'top_openers': dict(Counter(repeated_openers).most_common(5))
            }
        }
    }, None


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def format_report(result):
    """Format audit result as a markdown report."""
    m = result['metrics']
    lines = [
        f"# AI Tell Audit: {result['file']}",
        "",
        f"## Overall Verdict: **{result['overall_verdict']}**",
        "",
        "---",
        "",
        "## Em-Dash Density",
        f"- Total: {m['em_dashes']['total']} across {m['em_dashes']['pages']} pages",
        f"- Density: {m['em_dashes']['density_per_page']}/page",
        f"- Verdict: **{m['em_dashes']['verdict']}** — {m['em_dashes']['detail']}",
        "",
        "## Triplet Closing Patterns",
        f"- Found: {m['triplet_patterns']['count']}",
        f"- Verdict: **{m['triplet_patterns']['verdict']}** — {m['triplet_patterns']['detail']}",
    ]

    if m['triplet_patterns']['instances']:
        lines.append("")
        lines.append("### Instances")
        for i, inst in enumerate(m['triplet_patterns']['instances'], 1):
            lines.append(f"**{i}.** (word counts: {inst['word_counts']})")
            for s in inst['sentences']:
                lines.append(f"  - \"{s}\"")

    lines.extend([
        "",
        "## Sentence Length Distribution",
        f"- Count: {m['sentence_length']['count']} sentences",
        f"- Mean: {m['sentence_length']['mean']} words",
        f"- Std Dev: {m['sentence_length']['std']}",
        f"- Coefficient of Variation: {m['sentence_length']['cv']}",
        f"- Range: {m['sentence_length']['min']}–{m['sentence_length']['max']} words",
        f"- Verdict: **{m['sentence_length']['verdict']}** — {m['sentence_length']['detail']}",
        "",
        "## Paragraph Structure",
        f"- Total paragraphs: {m['paragraph_uniformity']['count']}",
        f"- Verdict: **{m['paragraph_uniformity']['verdict']}** — {m['paragraph_uniformity']['detail']}",
    ])

    if m['paragraph_uniformity']['distribution']:
        lines.append("- Distribution (sentences per paragraph → count):")
        for k, v in sorted(m['paragraph_uniformity']['distribution'].items()):
            lines.append(f"  - {k} sentences: {v} paragraphs")

    lines.extend([
        "",
        "## Negation-Action Pairs",
        f"- Found: {m['negation_action']['count']}",
        f"- Verdict: **{m['negation_action']['verdict']}** — {m['negation_action']['detail']}",
    ])

    if m['negation_action']['instances']:
        lines.append("")
        lines.append("### Instances")
        for i, inst in enumerate(m['negation_action']['instances'], 1):
            lines.append(f"**{i}.** \"{inst['negation']}\" → \"{inst['action']}\"")

    lines.extend([
        "",
        "## Repeated Sentence Openers",
        f"- Verdict: **{m['repeated_openers']['verdict']}** — {m['repeated_openers']['detail']}",
    ])

    if m['repeated_openers']['top_openers']:
        lines.append("- Top openers:")
        for opener, count in sorted(m['repeated_openers']['top_openers'].items(),
                                     key=lambda x: -x[1]):
            lines.append(f"  - \"{opener}\": {count}x")

    lines.extend([
        "",
        "---",
        "",
        "## Severity Guide",
        "- **NATURAL**: No FAIL results, ≤2 WARN. Reads as human-written.",
        "- **NEEDS REVISION**: 1 FAIL or ≥3 WARN. Specific pattern fixes needed.",
        "- **MECHANICAL**: ≥2 FAIL. Scene reads as AI-generated. Requires significant revision.",
        "",
    ])

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='AI Tell Audit — detect AI-generated text patterns in Fountain files'
    )
    parser.add_argument('files', nargs='*', help='Fountain files to audit')
    parser.add_argument('--all', action='store_true',
                        help='Audit all scene files in script/scenes/')
    parser.add_argument('--assembled', action='store_true',
                        help='Audit the assembled screenplay.fountain')
    parser.add_argument('--json', action='store_true',
                        help='Output raw JSON instead of formatted report')
    parser.add_argument('--output-dir', default='critic_outputs',
                        help='Directory for report files (default: critic_outputs)')

    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    files = []

    if args.all:
        scene_dir = os.path.join(base_dir, 'script', 'scenes')
        files = sorted(glob.glob(os.path.join(scene_dir, '*.fountain')))
    elif args.assembled:
        assembled = os.path.join(base_dir, 'script', 'screenplay.fountain')
        if os.path.exists(assembled):
            files = [assembled]
        else:
            print(f"Error: Assembled file not found: {assembled}")
            sys.exit(1)
    elif args.files:
        files = args.files
    else:
        parser.print_help()
        sys.exit(0)

    if not files:
        print("No files found to audit.")
        sys.exit(1)

    all_results = []

    for filepath in files:
        result, error = audit_fountain(filepath)
        if error:
            print(f"Error: {error}")
            continue

        all_results.append(result)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            report = format_report(result)
            print(report)

            # Write report to file
            basename = os.path.splitext(result['file'])[0]
            report_path = os.path.join(output_dir, f'{basename}_naturalism_audit.md')
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\nReport written to: {report_path}")

    # Summary for --all mode
    if len(all_results) > 1 and not args.json:
        print("\n" + "=" * 60)
        print("SUMMARY — ALL SCENES")
        print("=" * 60)
        verdicts = Counter(r['overall_verdict'] for r in all_results)
        print(f"Total scenes: {len(all_results)}")
        for verdict in ['NATURAL', 'NEEDS REVISION', 'MECHANICAL']:
            count = verdicts.get(verdict, 0)
            print(f"  {verdict}: {count}")

        print("\nScenes needing attention:")
        for r in all_results:
            if r['overall_verdict'] != 'NATURAL':
                em = r['metrics']['em_dashes']
                tri = r['metrics']['triplet_patterns']
                print(f"  {r['file']}: {r['overall_verdict']} "
                      f"(em-dash: {em['density_per_page']}/page, "
                      f"triplets: {tri['count']}, "
                      f"sentence CV: {r['metrics']['sentence_length']['cv']})")


if __name__ == '__main__':
    main()
