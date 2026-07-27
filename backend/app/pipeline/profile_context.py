"""
profile_context.py — Phase G: importance-aware profile context for the pipeline.

Bridges Storythread's rich profile system (trait blocks + importance levels) into
the Open-Write pipeline prompts. This is the Python counterpart of the frontend
``formatProfileForAI`` (app/src/utils/profileFormat.ts), with the Phase G
addition of *importance-aware routing*: which traits reach a phase depends on
their importance level, so the writer + critics get exactly the context they
need.

This module is deliberately self-contained: it parses the on-disk profile
Markdown directly (stdlib + PyYAML) rather than importing
``app.routers.profiles``. That keeps the pipeline toolchain testable without the
full FastAPI/async-backend environment, mirroring the other pipeline modules.

Importance routing (Phase G step 2)
-----------------------------------
  core        — always attached (writer + every critic). The defining traits.
  present     — attached to architect + writer + voice/continuity critics.
                These surface when the character is on the page.
  background  — planning context only (architect). Grounding, not per-scene.
  contextual  — planning context only (architect). World flavor.
  hidden      — subtext only. Attached to the continuity critic and writer
                with an explicit "NEVER name or state directly" instruction.

Voice registers (Phase G step 3)
--------------------------------
The Storythread model has no dedicated voice-register field; the closest analog
is the ``voice_notes`` trait-block section. This module treats each voice_notes
block as a named register (trait = register name, description = how/when it
surfaces) and surfaces them into the voice critic's prompt so it can check
against declared registers rather than inferring them.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

import yaml


# ── Importance levels & per-phase routing ────────────────────────────────────

CORE = "core"
PRESENT = "present"
BACKGROUND = "background"
CONTEXTUAL = "contextual"
HIDDEN = "hidden"

# Which importance levels each pipeline consumer receives.
ROUTING: dict[str, set[str]] = {
    "architect":    {CORE, PRESENT, BACKGROUND, CONTEXTUAL, HIDDEN},
    "writer":       {CORE, PRESENT, HIDDEN},
    "voice":        {CORE, PRESENT},
    "continuity":   {CORE, PRESENT, HIDDEN},
}

# Sections whose trait blocks represent voice material (Phase G step 3).
VOICE_SECTION_KEYS = ("voice_notes",)

# Map the on-disk section heading text -> section key, for characters. Mirrors
# app.routers.profiles.SECTION_CONFIGS["character"] so we don't import it.
_HEADING_TO_KEY = {
    "overview": "overview",
    "physical traits": "physical_traits",
    "personality traits": "personality_traits",
    "motivations": "motivations",
    "voice notes": "voice_notes",
    "hidden and foreshadowing traits": "hidden_and_foreshadowing",
    "hidden and foreshadowing": "hidden_and_foreshadowing",
    "relationships overview": "relationships_overview",
    "notes": "notes",
}
_KEY_TO_HEADING = {
    "overview": "Overview",
    "physical_traits": "Physical Traits",
    "personality_traits": "Personality Traits",
    "motivations": "Motivations",
    "voice_notes": "Voice Notes",
    "hidden_and_foreshadowing": "Hidden and Foreshadowing Traits",
    "relationships_overview": "Relationships Overview",
    "notes": "Notes",
}


# ── Lightweight profile model + parser ───────────────────────────────────────

@dataclass
class Trait:
    trait: str
    description: str
    importance: str


@dataclass
class Section:
    content: str = ""
    trait_blocks: list[Trait] = field(default_factory=list)


@dataclass
class Profile:
    name: str
    role: str = ""
    sections: dict[str, Section] = field(default_factory=dict)
    full_ai_summary: str = ""


_BLOCK_ITEM = re.compile(r"^\s*-\s+trait\s*:", re.IGNORECASE)


def _parse_profile_markdown(raw: str) -> Profile:
    """Parse a character profile Markdown file into a lightweight Profile.

    Understands the same on-disk shape as app.routers.profiles: YAML frontmatter
    delimited by ``---``, body split on ``# Heading`` lines, and trait blocks as
    ``- trait:`` / ``description:`` / ``importance:`` YAML-ish items. Robust to
    minor formatting drift; malformed input yields an empty Profile rather than
    raising.
    """
    raw = raw.replace("\ufeff", "")
    parts = raw.split("---", 2)
    name = ""
    role = ""
    if len(parts) >= 3:
        try:
            meta = yaml.safe_load(parts[1]) or {}
            if isinstance(meta, dict):
                name = str(meta.get("name") or "")
                role = str(meta.get("role") or "")
        except yaml.YAMLError:
            pass
        body = parts[2]
    else:
        body = raw

    profile = Profile(name=name, role=role)

    # Split body on single-# headings (capture keeps the heading text).
    chunks = re.split(r"^# (.+)$", body, flags=re.MULTILINE)
    # chunks == [pre, heading1, content1, heading2, content2, ...]
    i = 1
    while i + 1 < len(chunks):
        heading = chunks[i].strip()
        content = chunks[i + 1]
        key = _HEADING_TO_KEY.get(heading.lower())
        if key:
            profile.sections[key] = _parse_section(content)
        i += 2

    return profile


def _parse_section(content: str) -> Section:
    """Parse a section body into prose + trait blocks."""
    section = Section()
    lines = content.splitlines()

    # Locate the first trait-block item to split prose from blocks.
    first_block = None
    for idx, line in enumerate(lines):
        if _BLOCK_ITEM.match(line):
            first_block = idx
            break

    if first_block is None:
        section.content = content.strip()
        return section

    section.content = "\n".join(lines[:first_block]).strip()

    # Group the block region into items. Each item begins with `- trait:`; split
    # with a lookahead so the delimiter stays attached, then parse each item as a
    # one-element YAML list (exactly the on-disk block format).
    block_text = "\n".join(lines[first_block:])
    items = re.split(r"(?m)^(?=\s*-\s+trait\s*:)", block_text)
    for item in items:
        item = item.strip()
        if not item or not _BLOCK_ITEM.match(item):
            continue
        block = _parse_trait_item(item)
        if block:
            section.trait_blocks.append(block)
    return section


def _parse_trait_item(item_text: str) -> Trait | None:
    """Parse a complete `- trait: ... \n description: ... \n importance: ...`
    block into a Trait by loading it as a one-element YAML list."""
    try:
        data = yaml.safe_load(item_text)
    except yaml.YAMLError:
        return None
    if isinstance(data, list) and data and isinstance(data[0], dict):
        d = data[0]
    elif isinstance(data, dict):
        d = data
    else:
        return None
    importance = str(d.get("importance") or d.get("influence") or "present").strip().lower()
    return Trait(
        trait=str(d.get("trait") or "").strip(),
        description=str(d.get("description") or "").strip(),
        importance=importance,
    )


# ── Profile loading ──────────────────────────────────────────────────────────

def load_character_profiles(project: str) -> list[Profile]:
    """Load and parse every character profile under <project>/profiles/characters/.

    Returns Profile objects. Missing or empty folders return [] (the pipeline
    must still run without profiles). Malformed profiles are skipped, never fatal.
    """
    return _load_profiles_from(project, "characters")


def load_relationship_profiles(project: str) -> list[Profile]:
    """Load and parse every relationship profile under <project>/profiles/relationships/."""
    return _load_profiles_from(project, "relationships")


def load_location_profiles(project: str) -> list[Profile]:
    """Load and parse every location profile under <project>/profiles/locations/."""
    return _load_profiles_from(project, "locations")


def load_lore_profiles(project: str) -> list[Profile]:
    """Load and parse every lore entry under <project>/profiles/lore/."""
    return _load_profiles_from(project, "lore")


def _load_profiles_from(project: str, subfolder: str) -> list[Profile]:
    """Generic profile loader for any profiles/<subfolder>/ directory."""
    prof_dir = os.path.join(project, "profiles", subfolder)
    if not os.path.isdir(prof_dir):
        return []
    profiles: list[Profile] = []
    for filename in sorted(os.listdir(prof_dir)):
        if not filename.endswith(".md"):
            continue
        path = os.path.join(prof_dir, filename)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                raw = f.read()
            profiles.append(_parse_profile_markdown(raw))
        except Exception:
            continue
    return profiles


# ── Formatting ───────────────────────────────────────────────────────────────

def format_profile_for_ai(profile: Profile, include_levels: set[str],
                          sections: set[str] | None = None) -> str:
    """
    Serialize one profile into AI-readable text, keeping only trait blocks whose
    importance is in ``include_levels`` (and, if ``sections`` is given, only
    those section keys). Importance is annotated inline so the model can weight
    each trait.
    """
    lines = [f"Profile: {profile.name} (character)"]
    if profile.role:
        lines.append(f"Role: {profile.role}")
    if profile.full_ai_summary:
        lines.append("")
        lines.append("## AI Summary")
        lines.append(profile.full_ai_summary.strip())

    for section_key, section in profile.sections.items():
        if sections is not None and section_key not in sections:
            continue
        heading = _KEY_TO_HEADING.get(section_key, section_key.replace("_", " ").title())
        kept_blocks = [b for b in section.trait_blocks if b.importance in include_levels]
        has_prose = bool(section.content and section.content.strip())
        if not kept_blocks and not has_prose:
            continue
        lines.append("")
        lines.append(f"## {heading}")
        if has_prose:
            lines.append(section.content.strip())
        for block in kept_blocks:
            lines.append(f"- {block.trait} [{block.importance}]: {block.description}")
    return "\n".join(lines).strip()


# ── Phase-aware context builders ─────────────────────────────────────────────

def character_context(project: str, consumer: str) -> str:
    """
    Build the concatenated character context for a pipeline consumer
    (architect | writer | voice | continuity), applying the importance routing
    table. Returns "" if there are no profiles.
    """
    levels = ROUTING.get(consumer, ROUTING["writer"])
    profiles = load_character_profiles(project)
    if not profiles:
        return ""
    parts = [format_profile_for_ai(p, levels) for p in profiles]
    parts = [p for p in parts if p]
    if not parts:
        return ""
    header = "--- CHARACTER PROFILES ---"
    footer = "--- END CHARACTER PROFILES ---"
    note = ""
    if HIDDEN in levels:
        note = ("\nNote: [hidden] traits are subtext only. NEVER name, quote, or "
                "state them directly in prose; use them only to shape what is "
                "implied beneath the surface.")
    return "\n\n".join([header, "\n\n".join(parts) + note, footer])


def voice_registers_context(project: str) -> str:
    """
    Surface character voice registers (the voice_notes section) into a compact
    block for the voice critic, so it checks dialogue against *declared*
    registers rather than inferring them.
    """
    profiles = load_character_profiles(project)
    if not profiles:
        return ""
    parts = []
    for profile in profiles:
        reg_lines = []
        for section_key in VOICE_SECTION_KEYS:
            section = profile.sections.get(section_key)
            if not section:
                continue
            for block in section.trait_blocks:
                reg_lines.append(f"- {profile.name} — {block.trait}: {block.description}")
            if section.content and section.content.strip():
                reg_lines.append(f"- {profile.name} — voice notes: {section.content.strip()}")
        if reg_lines:
            parts.append("\n".join(reg_lines))
    if not parts:
        return ""
    return ("--- DECLARED VOICE REGISTERS (check dialogue against these) ---\n"
            + "\n".join(parts)
            + "\n--- END VOICE REGISTERS ---")


# ── World-building context (relationships, locations, lore) ──────────────────
# These profile types have simpler formats (free-text sections, no trait blocks
# with importance levels). The formatter dumps all prose sections so the
# pipeline prompts have full world-building context.

def format_world_profile(profile: Profile) -> str:
    """Serialize a non-character profile (relationship/location/lore) into
    AI-readable text. Dumps all sections with prose content."""
    kind = profile.role or "entry"
    lines = [f"{kind}: {profile.name}"]
    for section_key, section in profile.sections.items():
        heading = _KEY_TO_HEADING.get(section_key, section_key.replace("_", " ").title())
        has_prose = bool(section.content and section.content.strip())
        has_blocks = bool(section.trait_blocks)
        if not has_prose and not has_blocks:
            continue
        lines.append(f"\n## {heading}")
        if has_prose:
            lines.append(section.content.strip())
        for block in section.trait_blocks:
            lines.append(f"- {block.trait}: {block.description}")
    return "\n".join(lines).strip()


def _world_context_block(project: str, label: str, loader, header: str) -> str:
    """Build a labeled context block for one world-building profile type."""
    profiles = loader(project)
    if not profiles:
        return ""
    parts = [format_world_profile(p) for p in profiles]
    parts = [p for p in parts if p]
    if not parts:
        return ""
    return f"{header}\n\n" + "\n\n".join(parts) + f"\n{header.replace('--- ', '--- END ')}"


def relationship_context(project: str) -> str:
    """Build relationship profile context for pipeline prompts."""
    return _world_context_block(project, "relationships", load_relationship_profiles,
                                "--- RELATIONSHIP PROFILES ---")


def location_context(project: str) -> str:
    """Build location profile context for pipeline prompts."""
    return _world_context_block(project, "locations", load_location_profiles,
                                "--- LOCATION PROFILES ---")


def lore_context(project: str) -> str:
    """Build lore entry context for pipeline prompts."""
    return _world_context_block(project, "lore", load_lore_profiles,
                                "--- LORE ENTRIES ---")


def world_context(project: str) -> str:
    """Build the full world-building context block (relationships + locations + lore).

    Returns a single string with all non-character profiles, suitable for
    injection into architect/writer/critic prompts. Returns "" if none exist.
    """
    blocks = []
    for builder in (relationship_context, location_context, lore_context):
        block = builder(project)
        if block:
            blocks.append(block)
    return "\n\n".join(blocks) if blocks else ""
