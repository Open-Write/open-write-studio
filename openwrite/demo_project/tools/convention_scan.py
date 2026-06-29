#!/usr/bin/env python3
"""
Convention Ledger Scanner for Novel Manuscript
Scans the full manuscript and produces convention_ledger.json with per-chapter
frequency counts for sentence openers, body-anchor markers, sentence structures,
interiority methods, scene endings, and forbidden-after-N flags.

Usage: python tools/convention_scan.py
Output: state/convention_ledger.json
"""

import re
import json
import os
from datetime import datetime, timezone
from collections import Counter, defaultdict

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANUSCRIPT_PATH = os.path.join(BASE, "manuscript", "novel.md")
OUTPUT_PATH = os.path.join(BASE, "state", "convention_ledger.json")

# ---------------------------------------------------------------------------
# Chapter splitting
# ---------------------------------------------------------------------------
CHAPTER_RE = re.compile(
    r'^# (Chapter\s+(\d+)\s*[\-\u2013\u2014:]\s*(.*)|Interlude\s*[\-\u2013\u2014:]\s*(.*))$',
    re.MULTILINE
)
SECTION_RE = re.compile(r'^# (?:Chapter|Interlude|Part)\b', re.MULTILINE)


def split_chapters(text: str) -> list[dict]:
    """Split manuscript into chapters by header lines."""
    all_sections = list(SECTION_RE.finditer(text))
    matches = list(CHAPTER_RE.finditer(text))
    chapters = []
    for i, m in enumerate(matches):
        start = m.start()
        end = len(text)
        for s in all_sections:
            if s.start() > start:
                end = s.start()
                break
        chapter_text = text[start:end].strip()
        if m.group(2):
            label = f"ch{int(m.group(2)):02d}"
        else:
            title = (m.group(3) or m.group(4) or "Unknown").strip()
            clean_title = re.sub(r'[^a-zA-Z0-9\s]', '', title).strip()
            label = f"interlude_{clean_title.lower().replace(' ', '_')}"
        chapters.append({"label": label, "text": chapter_text})
    return chapters


# ---------------------------------------------------------------------------
# Text cleaning & sentence extraction
# ---------------------------------------------------------------------------

def clean_markdown(text: str) -> str:
    """Remove markdown syntax while preserving dialogue and structure."""
    # Remove headers
    text = re.sub(r'^#{1,4}\s+.*$', '', text, flags=re.MULTILINE)
    # Remove scene break markers
    text = re.sub(r'^---\s*$', '', text, flags=re.MULTILINE)
    # Remove bold/italic markdown but keep content
    text = re.sub(r'\*{1,3}([^*]+)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,3}([^_]+)_{1,3}', r'\1', text)
    # Remove blockquotes
    text = re.sub(r'^>\s?', '', text, flags=re.MULTILINE)
    return text


def extract_sentences(text: str) -> list[str]:
    """Split text into sentences. Preserve dialogue lines as whole sentences
    when they end with dialogue-closing quotes."""
    clean = clean_markdown(text)

    # Protect abbreviations and decimals
    clean = re.sub(r'\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr|St|vs|etc|i\.e|e\.g)\.',
                   r'\1<PERIOD>', clean)
    clean = re.sub(r'(\d)\.(\d)', r'\1<PERIOD>\2', clean)

    # Split into paragraphs first
    paragraphs = re.split(r'\n\s*\n', clean)

    sentences = []
    for para in paragraphs:
        para = para.strip()
        if not para or para == '---':
            continue

        # If paragraph is entirely dialogue (starts and ends with quotes),
        # treat as one sentence or split by dialogue-internal punctuation
        if re.match(r'^[""\u201c]', para):
            # Dialogue paragraph: split on dialogue-internal sentence boundaries
            # Pattern: dialogue-close + dialogue-open, or sentence end inside quotes
            parts = re.split(r'(?<=[.!?][""\u201d])\s+(?=[""\u201c])', para)
            for part in parts:
                part = part.replace('<PERIOD>', '.').strip()
                if len(part) > 3:
                    sentences.append(part)
        else:
            # Prose paragraph: split on sentence-ending punctuation
            parts = re.split(r'(?<=[.!?])\s+', para)
            for part in parts:
                part = part.replace('<PERIOD>', '.').strip()
                if len(part) > 5:
                    sentences.append(part)

    return sentences


def first_word(sentence: str) -> str:
    """Get the first word, stripped of punctuation and quotes."""
    s = sentence.strip().strip('"""\u201c\u201d\'')
    m = re.match(r'([A-Za-z\u2019\'-]+)', s)
    return m.group(1) if m else ""


def word_count(sentence: str) -> int:
    return len(sentence.split())


def is_dialogue_line(sentence: str) -> bool:
    """Check if a sentence is dialogue (starts with a quote mark)."""
    s = sentence.strip()
    return bool(re.match(r'^[""\u201c\u2018\'*]', s))


# ---------------------------------------------------------------------------
# Category: Sentence Openers
# ---------------------------------------------------------------------------
PREPOSITIONAL_OPENERS = re.compile(
    r'^(In|On|At|From|With|Through|Between|Against|Before|After|Behind|'
    r'Beyond|Under|Over|Across|Along|Among|Around|Below|Beneath|Beside|'
    r'Despite|Inside|Into|Near|Outside|Past|Since|Toward|Towards|Upon|'
    r'Within|Without)\b', re.IGNORECASE
)
CONJUNCTION_OPENERS = re.compile(
    r'^(And|But|Or|Yet|So|Nor)\b', re.IGNORECASE
)


def classify_opener(sentence: str) -> str:
    """Classify a sentence's opening type."""
    # Strip quotes for classification
    s = sentence.strip()
    while s and s[0] in '"""\u201c\u2018\'*':
        s = s[1:].strip()
    if not s:
        return "other"

    fw = first_word(s)
    if not fw:
        return "other"

    fw_lower = fw.lower()

    # Conjunction
    if fw_lower in ('and', 'but', 'or', 'yet', 'so', 'nor'):
        return "conjunction"

    # Prepositional phrase
    prep_words = {
        'in', 'on', 'at', 'from', 'with', 'through', 'between', 'against',
        'before', 'after', 'behind', 'beyond', 'under', 'over', 'across',
        'along', 'among', 'around', 'below', 'beneath', 'beside', 'despite',
        'inside', 'into', 'near', 'outside', 'past', 'since', 'toward',
        'towards', 'upon', 'within', 'without'
    }
    if fw_lower in prep_words:
        return "prepositional"

    # Adverbial (-ly)
    if fw_lower.endswith('ly') and len(fw_lower) > 4:
        return "adverbial"

    # Participial (-ing or -ed as sentence opener, capitalized)
    if fw[0].isupper() and len(fw) > 4:
        if fw_lower.endswith('ing'):
            return "participial"
        if fw_lower.endswith('ed'):
            return "participial"

    # Everything else that starts with a capital letter = subject-first
    if fw[0].isupper():
        return "subject_first"

    return "other"


def count_sentence_openers(sentences: list[str]) -> dict:
    counts = {
        "subject_first": 0,
        "prepositional": 0,
        "participial": 0,
        "adverbial": 0,
        "conjunction": 0,
        "other": 0,
        "total": len(sentences)
    }
    for s in sentences:
        cat = classify_opener(s)
        counts[cat] += 1
    return counts


# ---------------------------------------------------------------------------
# Category: Body-Anchor Markers
# ---------------------------------------------------------------------------
BODY_ANCHOR_PATTERNS = {
    "hands_fingers": re.compile(
        r'\b(?:thumb|finger|fingers|palm|palms|hand|hands|fist|fists|grip|grasp|'
        r'knuckle|knuckles|thumbnail|fingernail|fingertip|fingertips|'
        r'index finger|middle finger|thumb crescent|crescent mark|'
        r'nail bed|nail beds|finger flex|heel of palm|palm pressed|'
        r'hand tightened|hand resting|hand flat|hands in lap|'
        r'fingers drumming|fingers laced|touched the top of)\b',
        re.IGNORECASE
    ),
    "jaw_teeth": re.compile(
        r'\b(?:jaw|teeth|bite|clench|clenched|grind|ground|'
        r'jaw joint|jaw pop|teeth against|teeth gritted|'
        r'molars|inside of cheek|worked.*jaw)\b',
        re.IGNORECASE
    ),
    "throat_tongue": re.compile(
        r'\b(?:throat|swallow|swallowed|tongue|copper taste|'
        r'voice caught|dry mouth|back of tongue|'
        r'sound of.*swallowing|esophagus)\b',
        re.IGNORECASE
    ),
    "feet_legs": re.compile(
        r'\b(?:foot|feet|knee|knees|ankle|ankles|heel|heels|'
        r'weight shift|weight between|weight transfer|'
        r'cold tile|cold through.*socks|'
        r'arch compress|stood|sat down|'
        r'tile was cold)\b',
        re.IGNORECASE
    ),
    "shoulders_neck": re.compile(
        r'\b(?:shoulder|shoulders|neck|collar|collarbone|'
        r'base of.*neck|back of.*neck|knot at base|'
        r'higher than they should|muscles at.*base|'
        r'pulled.*collar)\b',
        re.IGNORECASE
    ),
    "eyes": re.compile(
        r'\b(?:eye|eyes|eyelid|eyelids|blink|blinked|gaze|stare|stared|'
        r'pupil|pupils|eye socket|visual field|'
        r'closed her eyes|open her eyes|phosphenes|'
        r'scatter plot behind|behind her eyelids)\b',
        re.IGNORECASE
    ),
    "breathing": re.compile(
        r'\b(?:breath|breathes|exhale|exhaled|inhale|inhaled|breathing|'
        r'air caught|breath caught|held her breath|'
        r'too fast|rib.*sore|air stopping halfway|'
        r'weight of Daniel.*breathing)\b',
        re.IGNORECASE
    ),
    "temperature": re.compile(
        r'\b(?:cold|warm|warmth|heat|chill|chilled|fever|'
        r'cold glass|cold tile|cold window|'
        r'temperature of.*room|the kind of cold|'
        r'cold spreading|cold through|the glass was cold)\b',
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
# Category: Sentence Structures
# ---------------------------------------------------------------------------
COMPOUND_PATTERN = re.compile(
    r',\s*(?:and|but|or|yet)\s+|;\s+'
)
COMPLEX_SUBORDINATE_PATTERN = re.compile(
    r'\b(?:that|which|who|whom|when|where|because|although|though|while|if|'
    r'unless|since|after|before|until|as though|even though|so that)\b',
    re.IGNORECASE
)
EM_DASH_PATTERN = re.compile(r'\s[\u2014\u2013]\s|[\u2014\u2013]')


def count_sentence_structures(sentences: list[str]) -> dict:
    counts = {
        "short_declarative": 0,
        "compound": 0,
        "complex_subordinate": 0,
        "em_dash": 0,
        "total": len(sentences)
    }
    for s in sentences:
        wc = word_count(s)
        if wc < 8:
            counts["short_declarative"] += 1
        if COMPOUND_PATTERN.search(s):
            counts["compound"] += 1
        if COMPLEX_SUBORDINATE_PATTERN.search(s):
            counts["complex_subordinate"] += 1
        if EM_DASH_PATTERN.search(s):
            counts["em_dash"] += 1
    return counts


# ---------------------------------------------------------------------------
# Category: Interiority Methods
# ---------------------------------------------------------------------------
PHYSICAL_BEHAVIOR_PATTERNS = re.compile(
    r'\b(?:hand|hands|finger|fingers|jaw|throat|shoulder|shoulders|'
    r'breath|breathing|exhale|inhale|blink|blinked|stare|stared|'
    r'grip|grasp|clench|clenched|fist|fists|palm|palms|'
    r'swallow|swallowed|knee|knees|ankle|heel|'
    r'pressed|tightened|relaxed|shifted|leaned|'
    r'nodded|shook|trembled|shivered|flinched|'
    r'reached|touched|held|turned away|'
    r'closed her eyes|opened her eyes|'
    r'looked down|looked up|looked away|'
    r'crossed her arms|rubbed her|pushed her)\b',
    re.IGNORECASE
)

NOTICE_PATTERN = re.compile(
    r'\b(?:she (?:saw|noticed|observed|watched|found|recognized|'
    r'spotted|caught|registered|perceived|'
    r'looked at|gazed at|stared at|focused on)|'
    r'(?:the sound|the smell|the sight|the taste|the feel|'
    r'the texture|the color|the shape|the light|'
    r'the silence|the darkness|the cold|the warmth|the absence))\b',
    re.IGNORECASE
)

NEGATION_PATTERN = re.compile(
    r"\b(?:did not|didn't|never|refused to|chose not to|"
    r"would not|wouldn't|could not|couldn't|"
    r"had not|hadn't|was not|wasn't|were not|weren't|"
    r"does not|doesn't|do not|don't|"
    r"cannot|can't)\b",
    re.IGNORECASE
)

DIRECT_THOUGHT_PATTERN = re.compile(
    r'(?:she thought|he thought|she wondered|he wondered|'
    r'she realized|he realized|she knew|he knew|'
    r'if only|what if)',
    re.IGNORECASE
)


def count_interiority(sentences: list[str]) -> dict:
    counts = {
        "physical_behavior": 0,
        "what_character_notices": 0,
        "what_character_does_not_do": 0,
        "direct_thought": 0,
        "total": len(sentences)
    }
    for s in sentences:
        if PHYSICAL_BEHAVIOR_PATTERNS.search(s):
            counts["physical_behavior"] += 1
        if NOTICE_PATTERN.search(s):
            counts["what_character_notices"] += 1
        if NEGATION_PATTERN.search(s):
            counts["what_character_does_not_do"] += 1
        if DIRECT_THOUGHT_PATTERN.search(s):
            counts["direct_thought"] += 1
    return counts


# ---------------------------------------------------------------------------
# Category: Scene Endings
# ---------------------------------------------------------------------------

def classify_scene_ending(last_paragraph: str) -> str:
    """Classify the final paragraph of a chapter."""
    p = last_paragraph.strip()
    if not p or p == '---':
        return "empty"

    # Check for "did not sleep" pattern
    if re.search(r'did not sleep|didn\'t sleep|could not sleep|couldn\'t sleep|'
                  r'would not sleep|wouldn\'t sleep|refused to sleep|'
                  r'did not rest|didn\'t rest', p, re.IGNORECASE):
        return "she_did_not_sleep"

    # Check for dialogue (paragraph starts with a quote)
    if re.match(r'^[""\u201c]', p):
        return "dialogue"

    # Check for action verbs (character doing something)
    action_verbs = re.compile(
        r'\b(?:walked|drove|stood|sat|turned|left|opened|closed|'
        r'reached|picked|set|put|pushed|pulled|moved|stepped|'
        r'ran|went|came|took|gave|held|carried|'
        r'nodded|shook|typed|filed|submitted|hung up|'
        r'pressed|drove south|drove north|drove home|'
        r'she closed|she opened|she turned|she stood|she sat|'
        r'she walked|she drove|she reached|she pressed)\b',
        re.IGNORECASE
    )

    # Image/description patterns
    image_patterns = re.compile(
        r'\b(?:the room|the house|the sky|the light|the dark|the silence|'
        r'the water|the air|the ocean|the ceiling|the floor|the window|'
        r'the wall|the door|the street|the trees?|the leaves?|the rain|'
        r'the snow|the sun|the moon|the stars?|the clouds?|the horizon|'
        r'the distance|the shadows?|the dawn|the dusk|the data|'
        r'it was quiet|it was dark|it was luminous|'
        r'the sound of|the smell of|the taste of|'
        r'outside|inside|above|below|behind)\b',
        re.IGNORECASE
    )

    has_action = bool(action_verbs.search(p))
    has_image = bool(image_patterns.search(p))

    # Dialogue embedded in prose (contains quote marks mid-paragraph)
    if re.search(r'[""\u201c\u201d]', p) and not has_action:
        return "dialogue"

    if has_action and not has_image:
        return "action"
    elif has_image and not has_action:
        return "image"
    elif has_action and has_image:
        return "action_in_setting"
    else:
        # Default heuristic: short sentences tend to be image-like
        if word_count(p) < 12:
            return "image"
        return "action"


def get_last_meaningful_paragraph(chapter_text: str) -> str:
    """Extract the last non-header, non-empty, non-scene-break paragraph."""
    lines = chapter_text.strip().split('\n')
    paragraphs = []
    current = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#'):
            continue
        if stripped == '' or stripped == '---':
            if current:
                paragraphs.append(' '.join(current))
                current = []
        else:
            current.append(stripped)
    if current:
        paragraphs.append(' '.join(current))

    for p in reversed(paragraphs):
        p = p.strip()
        if p and p != '---' and not p.startswith('#'):
            return p
    return ""


# ---------------------------------------------------------------------------
# Forbidden-After-N Flags
# ---------------------------------------------------------------------------

def find_physical_tic_overuse(chapter_anchors: dict) -> list[str]:
    """Flag any body-anchor category used 3+ times in same chapter."""
    flags = []
    for cat, count in chapter_anchors.items():
        if count >= 3:
            flags.append(f"{cat}: {count} occurrences")
    return flags


def find_verbatim_phrase_repetition(all_chapters: list[dict]) -> list[dict]:
    """Find phrases of 5+ words that appear verbatim 2+ times across manuscript."""
    phrase_counts = Counter()
    phrase_locations = defaultdict(set)

    for ch in all_chapters:
        text = ch["text"]
        # Normalize whitespace and case for matching
        normalized = re.sub(r'\s+', ' ', text.lower())
        words = re.findall(r'\b[a-z]+\b', normalized)

        for n in [6, 7, 8]:  # phrase lengths — 6+ to reduce noise
            for i in range(len(words) - n + 1):
                phrase = ' '.join(words[i:i+n])
                # Skip ultra-common function-word phrases
                common_starts = {'of the', 'in the', 'to the', 'and the',
                                 'on the', 'at the', 'for the', 'with the',
                                 'from the', 'that the', 'into the', 'was the',
                                 'she had', 'he had', 'it was', 'she was',
                                 'he was', 'there was', 'there were'}
                if phrase[:len(max(common_starts, key=len))] in common_starts:
                    continue
                phrase_counts[phrase] += 1
                phrase_locations[phrase].add(ch["label"])

    # Filter to 2+ occurrences
    flags = []
    seen_longer = set()
    for phrase, count in phrase_counts.most_common(1000):
        if count < 2:
            break
        # Skip if this is a substring of an already-reported longer phrase
        is_sub = False
        for longer in seen_longer:
            if phrase in longer and phrase != longer:
                is_sub = True
                break
        if not is_sub:
            seen_longer.add(phrase)
            flags.append({
                "phrase": phrase,
                "count": count,
                "chapters": sorted(phrase_locations[phrase])
            })
        if len(flags) >= 50:
            break

    return flags


def find_scene_ending_repetition(scene_endings: dict) -> list[dict]:
    """Flag any scene-ending pattern used 3+ times across manuscript."""
    pattern_counts = Counter()
    pattern_chapters = defaultdict(list)

    for ch_label, ending_type in scene_endings.items():
        if ending_type == "empty":
            continue
        pattern_counts[ending_type] += 1
        pattern_chapters[ending_type].append(ch_label)

    flags = []
    for pattern, count in pattern_counts.items():
        if count >= 3:
            flags.append({
                "pattern": pattern,
                "count": count,
                "chapters": sorted(pattern_chapters[pattern])
            })

    return flags


# ---------------------------------------------------------------------------
# Main scanning function
# ---------------------------------------------------------------------------
def scan_manuscript():
    """Main entry point: scan manuscript and produce convention ledger."""
    print(f"Reading manuscript from {MANUSCRIPT_PATH}...")
    with open(MANUSCRIPT_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    word_count_total = len(re.findall(r'\b\w+\b', text))
    print(f"Manuscript word count: {word_count_total:,}")

    chapters = split_chapters(text)
    print(f"Chapters found: {len(chapters)}")

    # Initialize global accumulators
    global_openers = Counter()
    global_anchors = Counter()
    global_structures = Counter()
    global_interiority = Counter()
    global_ending_counts = Counter()

    per_chapter_openers = {}
    per_chapter_anchors = {}
    per_chapter_structures = {}
    per_chapter_interiority = {}
    per_chapter_endings = {}

    scene_endings_map = {}

    for ch in chapters:
        label = ch["label"]
        ch_text = ch["text"]
        sentences = extract_sentences(ch_text)

        # Sentence openers
        openers = count_sentence_openers(sentences)
        per_chapter_openers[label] = openers
        for k, v in openers.items():
            if k != "total":
                global_openers[k] += v

        # Body anchors
        anchors = count_body_anchors(ch_text)
        per_chapter_anchors[label] = anchors
        for k, v in anchors.items():
            global_anchors[k] += v

        # Sentence structures
        structures = count_sentence_structures(sentences)
        per_chapter_structures[label] = structures
        for k, v in structures.items():
            if k != "total":
                global_structures[k] += v

        # Interiority methods
        interiority = count_interiority(sentences)
        per_chapter_interiority[label] = interiority
        for k, v in interiority.items():
            if k != "total":
                global_interiority[k] += v

        # Scene endings
        last_para = get_last_meaningful_paragraph(ch_text)
        ending_type = classify_scene_ending(last_para)
        per_chapter_endings[label] = {
            "type": ending_type,
            "last_paragraph_preview": last_para[:200] + ("..." if len(last_para) > 200 else "")
        }
        global_ending_counts[ending_type] += 1
        scene_endings_map[label] = ending_type

    # Forbidden-after-N flags
    print("Computing forbidden-after-N flags...")

    tic_flags = []
    for label, anchors in per_chapter_anchors.items():
        overuse = find_physical_tic_overuse(anchors)
        if overuse:
            tic_flags.append({"chapter": label, "flags": overuse})

    phrase_flags = find_verbatim_phrase_repetition(chapters)
    ending_flags = find_scene_ending_repetition(scene_endings_map)

    # Compute global percentages
    total_sentences = sum(v for k, v in global_openers.items() if k != "total") or 1

    opener_pcts = {}
    for k in ["subject_first", "prepositional", "participial", "adverbial", "conjunction"]:
        count = global_openers.get(k, 0)
        opener_pcts[k] = f"{count} ({count/total_sentences*100:.1f}%)"

    struct_pcts = {}
    for k in ["short_declarative", "compound", "complex_subordinate", "em_dash"]:
        count = global_structures.get(k, 0)
        struct_pcts[k] = f"{count} ({count/total_sentences*100:.1f}%)"

    int_pcts = {}
    for k in ["physical_behavior", "what_character_notices",
              "what_character_does_not_do", "direct_thought"]:
        count = global_interiority.get(k, 0)
        int_pcts[k] = f"{count} ({count/total_sentences*100:.1f}%)"

    # Build the ledger
    ledger = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "manuscript_word_count": word_count_total,
        "chapter_count": len(chapters),

        "sentence_openers": {
            "targets": {
                "subject_first": "40-50%",
                "prepositional": "10-15%",
                "participial": "5-10%",
                "adverbial": "3-5%",
                "conjunction": "2-4%"
            },
            "global_counts": dict(global_openers),
            "global_percentages": opener_pcts,
            "per_chapter": per_chapter_openers
        },

        "body_anchors": {
            "targets_per_chapter": {
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
            "per_chapter": per_chapter_anchors,
            "flags": tic_flags
        },

        "sentence_structures": {
            "targets": {
                "short_declarative": "15-25%",
                "compound": "20-30%",
                "complex_subordinate": "20-30%",
                "em_dash": "5-8%"
            },
            "global_counts": dict(global_structures),
            "global_percentages": struct_pcts,
            "per_chapter": per_chapter_structures
        },

        "interiority_methods": {
            "targets": {
                "physical_behavior": "60%+",
                "what_character_notices": "20-30%",
                "what_character_does_not_do": "5-10%",
                "direct_thought": "2-3%"
            },
            "global_counts": dict(global_interiority),
            "global_percentages": int_pcts,
            "per_chapter": per_chapter_interiority
        },

        "scene_endings": {
            "targets": {
                "image": "preferred",
                "action": "acceptable",
                "dialogue": "5% max",
                "she_did_not_sleep": "BANNED after first use"
            },
            "global_counts": dict(global_ending_counts),
            "per_chapter": per_chapter_endings
        },

        "flags": {
            "physical_tic_overuse": tic_flags,
            "verbatim_phrase_repetition": phrase_flags,
            "scene_ending_pattern_repetition": ending_flags
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
    print(f"Chapters: {len(chapters)}")
    print(f"Total sentences (approx): {total_sentences}")
    print(f"\n--- Sentence Openers ---")
    for k, v in opener_pcts.items():
        print(f"  {k}: {v}")
    print(f"\n--- Body Anchors (global) ---")
    for k, v in sorted(global_anchors.items()):
        print(f"  {k}: {v}")
    print(f"\n--- Sentence Structures ---")
    for k, v in struct_pcts.items():
        print(f"  {k}: {v}")
    print(f"\n--- Interiority Methods ---")
    for k, v in int_pcts.items():
        print(f"  {k}: {v}")
    print(f"\n--- Scene Endings ---")
    for k, v in sorted(global_ending_counts.items()):
        print(f"  {k}: {v}")
    print(f"\n--- Flags ---")
    print(f"  Physical tic overuse: {len(tic_flags)} chapters flagged")
    print(f"  Verbatim phrase repetition: {len(phrase_flags)} phrases flagged")
    print(f"  Scene ending pattern repetition: {len(ending_flags)} patterns flagged")

    if tic_flags:
        print(f"\n  Tic overuse details:")
        for tf in tic_flags[:10]:
            print(f"    {tf['chapter']}: {', '.join(tf['flags'])}")

    if phrase_flags:
        print(f"\n  Top verbatim repetitions:")
        for pf in phrase_flags[:10]:
            print(f"    \"{pf['phrase']}\" ({pf['count']}x in {', '.join(pf['chapters'][:5])}{'...' if len(pf['chapters']) > 5 else ''})")

    if ending_flags:
        print(f"\n  Scene ending repetitions:")
        for ef in ending_flags:
            print(f"    {ef['pattern']}: {ef['count']}x in {', '.join(ef['chapters'][:5])}{'...' if len(ef['chapters']) > 5 else ''}")

    return ledger


if __name__ == "__main__":
    scan_manuscript()
