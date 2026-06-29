#!/usr/bin/env python3
"""
Episode Export Tool for TV Scripts
Exports an episode script to PDF or clean Fountain format.
Uses reportlab for PDF generation.

Usage:
    python tools/episode_export.py --episode S01E01                    # Export to Fountain
    python tools/episode_export.py --episode S01E01 --format pdf       # Export to PDF
    python tools/episode_export.py --episode S01E01 --format both      # Export both
    python tools/episode_export.py --season 1                          # Export all episodes
"""

import os
import sys
import re
import glob

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
OUTPUT_DIR = os.path.join(BASE_DIR, "scripts", "exports")


def parse_args():
    """Parse command line arguments."""
    episode = None
    season = None
    fmt = "fountain"

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--episode' and i + 1 < len(args):
            episode = args[i + 1].upper()
            i += 2
        elif args[i] == '--season' and i + 1 < len(args):
            season = int(args[i + 1])
            i += 2
        elif args[i] == '--format' and i + 1 < len(args):
            fmt = args[i + 1].lower()
            i += 2
        else:
            i += 1

    return episode, season, fmt


def clean_fountain_export(content):
    """Clean a Fountain file for export — remove internal markers."""
    lines = content.split('\n')
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Remove internal tracking comments
        if stripped.startswith('<!--') and stripped.endswith('-->'):
            continue
        cleaned.append(line)
    return '\n'.join(cleaned)


def export_fountain(episode, input_path, output_dir):
    """Export episode as clean Fountain file."""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    content = clean_fountain_export(content)

    output_path = os.path.join(output_dir, f"{episode}.fountain")
    os.makedirs(output_dir, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  Fountain: {output_path}")
    return output_path


def export_pdf(episode, input_path, output_dir):
    """Export episode as PDF using reportlab."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
    except ImportError:
        print("  PDF export requires reportlab: pip install reportlab")
        return None

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    output_path = os.path.join(output_dir, f"{episode}.pdf")
    os.makedirs(output_dir, exist_ok=True)

    # Parse Fountain content
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=1.5 * inch,
        rightMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch
    )

    styles = getSampleStyleSheet()

    # Custom styles for screenplay format
    title_style = ParagraphStyle(
        'ScreenplayTitle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=12
    )

    scene_heading_style = ParagraphStyle(
        'SceneHeading',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=12,
        spaceBefore=12,
        spaceAfter=6
    )

    action_style = ParagraphStyle(
        'Action',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=12,
        spaceAfter=6
    )

    character_style = ParagraphStyle(
        'Character',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=12,
        alignment=TA_CENTER,
        spaceBefore=12,
        spaceAfter=0
    )

    dialogue_style = ParagraphStyle(
        'Dialogue',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=12,
        leftIndent=1 * inch,
        rightIndent=1.5 * inch,
        spaceAfter=6
    )

    parenthetical_style = ParagraphStyle(
        'Parenthetical',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=12,
        leftIndent=1.5 * inch,
        rightIndent=2 * inch,
        spaceAfter=0
    )

    transition_style = ParagraphStyle(
        'Transition',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=12,
        alignment=TA_CENTER,
        spaceBefore=6,
        spaceAfter=6
    )

    story = []
    lines = content.split('\n')
    in_title_page = True
    current_character = None
    in_dialogue = False

    for line in lines:
        stripped = line.strip()

        # Skip title page
        if in_title_page:
            if re.match(r'^(INT\.|EXT\.|#|COLD OPEN|ACT)', stripped, re.IGNORECASE):
                in_title_page = False
            else:
                if stripped:
                    story.append(Paragraph(stripped.replace('&', '&').replace('<', '<'), title_style))
                continue

        # Empty line
        if not stripped:
            story.append(Spacer(1, 6))
            in_dialogue = False
            continue

        # Page break
        if stripped == '===':
            story.append(PageBreak())
            continue

        # Scene heading
        if re.match(r'^(INT\.|EXT\.)', stripped, re.IGNORECASE):
            story.append(Paragraph(stripped.replace('&', '&').replace('<', '<'), scene_heading_style))
            in_dialogue = False
            continue

        # Transition
        if re.match(r'^(FADE|CUT|DISSOLVE)', stripped, re.IGNORECASE):
            story.append(Paragraph(stripped.replace('&', '&').replace('<', '<'), transition_style))
            continue

        # Act break markers
        if re.match(r'^(END OF ACT|ACT \w+|COLD OPEN|TITLE SEQUENCE)', stripped, re.IGNORECASE):
            story.append(Paragraph(stripped.replace('&', '&').replace('<', '<'), transition_style))
            continue

        # Character name
        if re.match(r'^[A-Z][A-Z\s\.]+(\s*\^)?$', stripped) and len(stripped) < 40:
            story.append(Paragraph(stripped.replace('&', '&').replace('<', '<'), character_style))
            current_character = stripped
            in_dialogue = True
            continue

        # Parenthetical
        if stripped.startswith('(') and stripped.endswith(')'):
            story.append(Paragraph(stripped.replace('&', '&').replace('<', '<'), parenthetical_style))
            continue

        # Dialogue or action
        safe_text = stripped.replace('&', '&').replace('<', '<')
        if in_dialogue:
            story.append(Paragraph(safe_text, dialogue_style))
        else:
            story.append(Paragraph(safe_text, action_style))

    if story:
        doc.build(story)
        print(f"  PDF: {output_path}")
        return output_path
    else:
        print(f"  No content to export for {episode}")
        return None


def main():
    episode, season, fmt = parse_args()

    episodes = []

    if episode:
        episodes = [episode]
    elif season:
        pattern = os.path.join(SCRIPTS_DIR, f"S{season:02d}E*.fountain")
        for f in sorted(glob.glob(pattern)):
            ep = os.path.splitext(os.path.basename(f))[0]
            if not ep.startswith("Season_"):
                episodes.append(ep)
    else:
        print("Error: --episode or --season is required")
        sys.exit(1)

    if not episodes:
        print("No episodes found to export.")
        sys.exit(1)

    output_dir = OUTPUT_DIR

    for ep in episodes:
        input_path = os.path.join(SCRIPTS_DIR, f"{ep}.fountain")
        if not os.path.exists(input_path):
            print(f"  {ep}: Not found ({input_path})")
            print("  Run episode_assemble.py first.")
            continue

        print(f"\nExporting {ep}:")

        if fmt in ('fountain', 'both'):
            export_fountain(ep, input_path, output_dir)

        if fmt in ('pdf', 'both'):
            export_pdf(ep, input_path, output_dir)

        if fmt not in ('fountain', 'pdf', 'both'):
            print(f"  Unknown format: {fmt}. Use 'fountain', 'pdf', or 'both'.")

    print(f"\nExport complete. Output: {output_dir}")


if __name__ == "__main__":
    main()
