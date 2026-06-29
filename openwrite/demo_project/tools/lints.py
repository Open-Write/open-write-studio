"""
lints.py — blocking and advisory lints for the Open-Write finalize gate.

Design notes
------------
- Every threshold below is anchored to a value already used by the red-team
  lint suite (the one that produced the HN release audit), so a manuscript
  that passes finalize will not then fail the audit on the same check.
  Where a number comes from the audit it is cited inline. Tune to match your
  actual suite; keep finalize and the audit in lockstep.
- Each lint reports a `level` (PROSE | ARCHITECT | BIBLE). That maps to the
  routing table in the run prompt: a failing lint tells the agent (or you)
  which level to fix at, not just that something is wrong.
- Honest limits are noted per lint. finalize is a backstop, not a substitute
  for genuine critic independence. A low aggregate density can mask a voice
  fingerprint; a "located finding" can be faked; historical accuracy is not
  mechanically checkable. Those are called out where they apply.
"""

from __future__ import annotations
import re
import os
import glob
from collections import Counter, defaultdict

# ----------------------------------------------------------------------------
# THRESHOLDS  (audit-anchored; edit here, not in the functions)
# ----------------------------------------------------------------------------

WORDS_PER_PAGE = 250                 # assembler convention (~37,057 words -> 148 pages)

# Hollow-critic gate. Audit flagged 11-16 word critic files as TOO_SHORT and
# 39-93 word files as below the "substantive-analysis threshold."
CRITIC_MIN_WORDS = 120               # above the 93 the audit still rejected
CRITIC_MIN_LOCATED_FINDINGS = 3      # raised from 1; harder to fake 3 than 1
CRITIC_REQUIRE_CHAPTER_HASH = True   # critic must embed chapter_hash to prove it read the file

# Padding gate. Audit: chapters landing within 25 words of 2000/2500/3000.
PADDING_BAND_WORDS = 25
PADDING_ROUND_TO = 500               # flag proximity to any multiple of 500

# Refrain / duplication gates. Audit: exact duplicate paragraphs (10 in the
# mimo assembly), cross-chapter refrains (sentences in 4-5 chapters), and
# intra-chapter loops (7-16x "the wind moved the canvas").
DUP_PARAGRAPH_MIN_WORDS = 30         # ignore scene-break stubs and headers
CROSS_CHAPTER_REFRAIN_MIN_CHAPTERS = 3   # same sentence verbatim in >=3 chapters
INTRA_CHAPTER_REPEAT_MIN = 4         # same sentence verbatim >=4x in one chapter
REFRAIN_MIN_WORDS = 6                # only count substantive sentences

# Whitelist file for intentional refrains (one phrase per line, lowercase, stripped)
# If this file exists in the project's state/ directory, listed phrases are excluded
# from the refrain/duplication lint. Use for structural motifs, callbacks, and
# character voice patterns that are deliberately repeated.
WHITELIST_FILENAME = "whitelisted_refrains.txt"

# Negative-construction density. Audit "critical threshold" was >15 per 1k words
# (it cited Ch10 at 32.9 and Ch1 at 36.6). NOTE: this catches egregious cases
# only. A diluted aggregate (mimo finished at ~2.7/1k) can still carry the tell
# everywhere -- density gating is a floor, not a fix. The fix is an independent
# (different-model) critic, which finalize cannot supply.
NEG_CONSTRUCTION_CRITICAL_PER_1K = 15.0

# Em-dash density. Audit called this "fix-before-ship," not BLOCKER -> advisory.
EM_DASH_PER_PAGE_WARN = 2.0          # audit flagged mimo at 3.1/page

# ----------------------------------------------------------------------------
# parsing helpers (heuristic; good enough for gating, not for grading)
# ----------------------------------------------------------------------------

_WORD = re.compile(r"\b[\w']+\b")
_SENT_SPLIT = re.compile(r"(?<=[.!?])[\"'\u201d\u2019)\]]?\s+")

def _words(text: str) -> list[str]:
    return _WORD.findall(text)

def _wc(text: str) -> int:
    return len(_words(text))

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()

def _norm_stripped(s: str) -> str:
    """Normalize and strip trailing punctuation for whitelist matching."""
    n = _norm(s)
    return n.rstrip('.!?,"\' \u201d\u2019')

def _paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

def _sentences(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text).strip()
    return [s.strip() for s in _SENT_SPLIT.split(flat) if s.strip()]

def load_chapters(project: str) -> list[tuple[str, str]]:
    """Return [(filename, text), ...] sorted numerically by leading digits."""
    paths = glob.glob(os.path.join(project, "manuscript", "chapters", "*.md"))
    def key(p):
        m = re.match(r"(\d+)", os.path.basename(p))
        return int(m.group(1)) if m else 0
    out = []
    for p in sorted(paths, key=key):
        with open(p, encoding="utf-8") as fh:
            out.append((os.path.basename(p), fh.read()))
    return out

# ----------------------------------------------------------------------------
# located-finding detector for the hollow-critic gate
# ----------------------------------------------------------------------------

_LOCATED = re.compile(
    r"(line\s*\d+|paragraph\s*\d+|\u00b6\s*\d+|p\.?\s*\d+"      # explicit refs
    r'|"[^"]{12,}"|\u201c[^\u201d]{12,}\u201d)',                # quoted spans (>=~4 words)
    re.IGNORECASE,
)

_CHAPTER_HASH = re.compile(r"chapter_hash\s*[:=]\s*[a-fA-F0-9]{16,}", re.IGNORECASE)

def count_located_findings(text: str) -> int:
    return len(_LOCATED.findall(text))

# ----------------------------------------------------------------------------
# the lints. each returns a dict: name, level, blocking, status, findings
# status in {PASS, FAIL, WARN}
# ----------------------------------------------------------------------------

def lint_hollow_critics(project: str) -> dict:
    findings = []
    for path in glob.glob(os.path.join(project, "critic_outputs", "*.md")):
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        wc = _wc(text)
        located = count_located_findings(text)
        has_hash = bool(_CHAPTER_HASH.search(text))
        reasons = []
        if wc < CRITIC_MIN_WORDS:
            reasons.append(f"below {CRITIC_MIN_WORDS}-word floor ({wc})")
        if located < CRITIC_MIN_LOCATED_FINDINGS:
            reasons.append(f"below {CRITIC_MIN_LOCATED_FINDINGS} located findings ({located})")
        if CRITIC_REQUIRE_CHAPTER_HASH and not has_hash:
            reasons.append("missing chapter_hash (proves critic read the file)")
        if reasons:
            findings.append({
                "file": os.path.basename(path),
                "words": wc,
                "located_findings": located,
                "has_chapter_hash": has_hash,
                "reason": "; ".join(reasons),
            })
    return {
        "name": "hollow_critics",
        "level": "PROSE",  # a hollow critic means the check didn't run; rerun it
        "blocking": True,
        "status": "FAIL" if findings else "PASS",
        "findings": findings,
        "note": "Length+located-findings+chapter-hash is a backstop and is gameable; "
                "real fix is an independent (different-model) critic invocation. "
                "chapter_hash proves the critic processed the actual chapter file.",
    }

def lint_padding(chapters: list[tuple[str, str]]) -> dict:
    findings = []
    for name, text in chapters:
        wc = _wc(text)
        nearest = round(wc / PADDING_ROUND_TO) * PADDING_ROUND_TO
        if nearest > 0 and abs(wc - nearest) <= PADDING_BAND_WORDS:
            findings.append({"file": name, "words": wc, "nearest_round": nearest,
                             "distance": abs(wc - nearest)})
    return {
        "name": "round_number_padding",
        "level": "ARCHITECT",  # a length gap is a material problem, not a prose one
        "blocking": True,
        "status": "FAIL" if findings else "PASS",
        "findings": findings,
        "note": "Detects round-number landings only. 'Editing toward a target' "
                "across revisions is visible to the runner (edit history), not "
                "to finalize -- gate that in the runner.",
    }

def lint_refrains(chapters: list[tuple[str, str]], project: str = None) -> dict:
    findings = []

    # Load whitelist if available
    whitelist = set()
    if project:
        wl_path = os.path.join(project, "state", WHITELIST_FILENAME)
        if os.path.exists(wl_path):
            with open(wl_path, encoding="utf-8") as fh:
                for line in fh:
                    phrase = line.strip().lower()
                    if phrase and not phrase.startswith("#"):
                        whitelist.add(_norm_stripped(phrase))

    # exact duplicate paragraphs across the whole manuscript
    para_locations = defaultdict(list)
    for name, text in chapters:
        for p in _paragraphs(text):
            if _wc(p) >= DUP_PARAGRAPH_MIN_WORDS:
                para_locations[_norm(p)].append(name)
    for norm_p, locs in para_locations.items():
        if len(locs) >= 2:
            findings.append({"type": "exact_duplicate_paragraph",
                             "chapters": locs, "preview": norm_p[:80]})

    # cross-chapter verbatim sentence refrains, and intra-chapter loops
    sent_chapter_counts = defaultdict(Counter)   # sentence -> {chapter: count}
    for name, text in chapters:
        for s in _sentences(text):
            if _wc(s) >= REFRAIN_MIN_WORDS:
                sent_chapter_counts[_norm(s)][name] += 1
    for norm_s, ch_counts in sent_chapter_counts.items():
        if _norm_stripped(norm_s) in whitelist:
            continue
        if len(ch_counts) >= CROSS_CHAPTER_REFRAIN_MIN_CHAPTERS:
            findings.append({"type": "cross_chapter_refrain",
                             "chapters": sorted(ch_counts),
                             "preview": norm_s[:80]})
        for ch, c in ch_counts.items():
            if c >= INTRA_CHAPTER_REPEAT_MIN:
                findings.append({"type": "intra_chapter_loop", "chapter": ch,
                                 "count": c, "preview": norm_s[:80]})

    return {
        "name": "refrains_and_duplication",
        "level": "ARCHITECT",  # a structural motif overused -> re-plan; a tic -> PROSE
        "blocking": True,
        "status": "FAIL" if findings else "PASS",
        "findings": findings,
        "note": "Exact-match only. Near-duplicate (fuzzy) detection has false "
                "positives and is left advisory; add a Jaccard pass if wanted.",
    }

_NEG = re.compile(
    r"\b(?:He|She|They|[A-Z][a-z\u00e0-\u00ff]+(?:\s+[A-Z][a-z\u00e0-\u00ff]+)?)\s+"
    r"(?:did|could|would|was|were|can|will)\s+not\b|\bcannot\b"
)

def lint_negative_density(chapters: list[tuple[str, str]]) -> dict:
    findings = []
    for name, text in chapters:
        wc = _wc(text) or 1
        n = len(_NEG.findall(text))
        per_1k = n * 1000.0 / wc
        if per_1k > NEG_CONSTRUCTION_CRITICAL_PER_1K:
            findings.append({"file": name, "count": n,
                             "per_1k": round(per_1k, 1)})
    return {
        "name": "negative_construction_density",
        "level": "PROSE",
        "blocking": True,
        "status": "FAIL" if findings else "PASS",
        "findings": findings,
        "note": "Per-chapter only. Aggregate rate can be low while the tell is "
                "everywhere; this gate catches spikes, not the fingerprint.",
    }

def lint_em_dash(chapters: list[tuple[str, str]]) -> dict:
    findings = []
    _DASH = re.compile(r"(?<!-)--(?!-)")  # matches -- but not ---
    for name, text in chapters:
        pages = (_wc(text) / WORDS_PER_PAGE) or 1
        unicode_count = text.count("\u2014")
        ascii_count = len(_DASH.findall(text))
        total = unicode_count + ascii_count
        per_page = total / pages
        if per_page > EM_DASH_PER_PAGE_WARN:
            findings.append({"file": name, "per_page": round(per_page, 1),
                             "unicode_dashes": unicode_count,
                             "ascii_double_hyphens": ascii_count})
    return {
        "name": "em_dash_density",
        "level": "PROSE",
        "blocking": False,   # advisory: audit rated this fix-before-ship, not BLOCKER
        "status": "WARN" if findings else "PASS",
        "findings": findings,
        "note": "Counts both Unicode em-dashes and double-hyphens (--). "
                "Agents that substitute -- for — to bypass detection are caught.",
    }

def lint_factual_review(project: str) -> dict:
    """
    Historical accuracy of named real figures is NOT mechanically checkable
    (this is the gate that would have caught the Bishop Mugica inversion).
    Mechanize the *process* instead: the bible declares named real figures in
    state/real_figures.json; an independent reviewer (human or different model)
    records sign-off in state/factual_reviews.json. Missing sign-off -> FAIL.
    """
    reg = os.path.join(project, "state", "real_figures.json")
    rev = os.path.join(project, "state", "factual_reviews.json")
    if not os.path.exists(reg):
        return {"name": "factual_review", "level": "BIBLE", "blocking": True,
                "status": "WARN",
                "findings": [{"reason": "no real_figures.json; cannot verify any "
                              "named real figure was fact-checked"}],
                "note": "Declare real figures in the bible so this can gate."}
    import json
    figures = json.load(open(reg, encoding="utf-8"))
    reviews = json.load(open(rev, encoding="utf-8")) if os.path.exists(rev) else {}
    findings = []
    for fig in figures:
        r = reviews.get(fig)
        if not r or r.get("verdict") != "consistent_with_record":
            findings.append({"figure": fig,
                             "reason": "no independent factual sign-off"})
    return {
        "name": "factual_review",
        "level": "BIBLE",   # a real-figure error is a bible-level fix
        "blocking": True,
        "status": "FAIL" if findings else "PASS",
        "findings": findings,
        "note": "Process gate, not a fact-checker. It confirms the review "
                "happened; the review itself is the independent read / a human.",
    }

def run_all(project: str) -> list[dict]:
    chapters = load_chapters(project)
    return [
        lint_hollow_critics(project),
        lint_padding(chapters),
        lint_refrains(chapters, project=project),
        lint_negative_density(chapters),
        lint_em_dash(chapters),
        lint_factual_review(project),
    ]
