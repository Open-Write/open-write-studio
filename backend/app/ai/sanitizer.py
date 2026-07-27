# ai/sanitizer.py -- Em Dash Sanitizer
# =======================================
# Em-dash policy (unified, Open-Write advisory stance):
#   Em dashes and en dashes are a LEGITIMATE prose choice. They are NOT banned.
#   Density is governed downstream by the deterministic `em_dash` lint
#   (advisory, flags > 2.0 dashes/page -- see app.pipeline.lints.lint_em_dash)
#   and by the naturalism critic, which hunts em-dash OVERUSE, not presence.
#
# This module therefore does NOT strip em/en dashes from model output. Doing so
# would (a) forbid a punctuation mark the Open-Write methodology explicitly
# permits, and (b) corrupt critic reports by rewriting the em dashes inside
# quoted chapter passages, so located findings no longer match the source text.
#
# What remains here:
#   - contains_em_dash(): a pure detector, still useful as an informational
#     signal (logged, and surfaced as a "model emitted em dashes" hint) and
#     used by the density lint's counting logic.
#   - sanitize()/sanitize_chat()/sanitize_dict(): kept as pass-throughs that
#     only collapse accidental repeated whitespace. They are still called from
#     the AI call paths so this remains the single chokepoint if the policy
#     ever needs to change again.
#
# Unicode reference:
#   Em dash:  — (U+2014) -- the long dash, like this—example
#   En dash:  – (U+2013) -- the medium dash, like this–example
#   Minus:    - (U+002D) -- the standard hyphen/minus, always allowed

import re


def sanitize(text: str) -> str:
    """
    Normalize AI output without removing em/en dashes.

    Em dashes are permitted under the Open-Write advisory policy (density is
    checked by the em_dash lint and the naturalism critic, not stripped here).
    We only collapse accidental repeated whitespace.
    """
    if not text:
        return ""
    # Clean up accidental repeated spaces from any upstream substitution.
    text = re.sub(r"  +", " ", text)
    return text


def contains_em_dash(text: str) -> bool:
    """
    Returns True if the text contains an em or en dash.
    Used as an informational signal (logging, density lint counting).
    """
    return "\u2014" in text or "\u2013" in text


def sanitize_chat(text: str) -> str:
    """
    Normalize a chat response without removing em/en dashes.

    Previously this also rewrote ` -- ` constructs to commas to enforce a hard
    no-em-dash rule. Under the unified Open-Write advisory policy em dashes
    (and their double-hyphen fallback) are permitted prose, so both passes are
    dropped and only whitespace is normalized.
    """
    return sanitize(text)


def sanitize_dict(data: dict) -> dict:
    """
    Recursively walk a nested dict/list structure and normalize all string
    values (whitespace only -- em/en dashes are preserved).
    """
    if isinstance(data, dict):
        return {k: sanitize_dict(v) for k, v in data.items()}
    if isinstance(data, list):
        return [sanitize_dict(item) for item in data]
    if isinstance(data, str):
        return sanitize(data)
    return data
