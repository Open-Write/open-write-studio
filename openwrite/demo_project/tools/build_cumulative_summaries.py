"""
Build cumulative chapter summaries for the novel.
Each chapter's summary includes condensed versions of ALL previous chapters' summaries,
plus the current chapter's own key points.

Usage: python tools/build_cumulative_summaries.py
"""

import os
import re

SUMMARIES_DIR = os.path.join(os.path.dirname(__file__), '..', 'manuscript', 'chapters_pdf', 'summaries')
CUMULATIVE_DIR = os.path.join(os.path.dirname(__file__), '..', 'manuscript', 'chapters_pdf', 'cumulative_summaries')


def read_summary(filepath):
    """Read a summary file and extract the description and key moments."""
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # Extract the header (title, part, track, pages)
    header_match = re.search(r'(^(?:#|##)\s+.+?)(?=\n## |\Z)', text, re.DOTALL | re.MULTILINE)
    header = header_match.group(1).strip() if header_match else ""

    # Extract the summary paragraph
    summary_match = re.search(r'## Summary\s*\n(.+?)(?=\n## |\Z)', text, re.DOTALL)
    summary = summary_match.group(1).strip() if summary_match else ""

    # Extract key moments
    moments_match = re.search(r'## Key Moments\s*\n(.+?)(?=\n## |\Z)', text, re.DOTALL)
    moments = moments_match.group(1).strip() if moments_match else ""

    return header, summary, moments


def condense_summary(summary, max_sentences=2):
    """Take a full summary and condense to max_sentences."""
    sentences = re.split(r'(?<=[.!?])\s+', summary.strip())
    condensed = ' '.join(sentences[:max_sentences])
    return condensed


def build_cumulative():
    os.makedirs(CUMULATIVE_DIR, exist_ok=True)

    # Get all summary files in order
    files = sorted([f for f in os.listdir(SUMMARIES_DIR) if f.endswith('.md')])

    # Read all summaries
    all_summaries = []
    for f in files:
        filepath = os.path.join(SUMMARIES_DIR, f)
        header, summary, moments = read_summary(filepath)
        all_summaries.append({
            'file': f,
            'header': header,
            'summary': summary,
            'moments': moments,
            'condensed': condense_summary(summary)
        })

    # Build cumulative summaries
    for i, current in enumerate(all_summaries):
        # Extract chapter title from header
        title_line = current['header'].split('\n')[0] if current['header'] else f"Chapter {i+1}"

        output_lines = []
        output_lines.append(f"# Story So Far — Through {title_line.lstrip('#').strip()}")
        output_lines.append("")
        output_lines.append(f"**Chapters covered:** 1-{i+1}")
        output_lines.append("")

        # Previous chapters summary (condensed)
        if i > 0:
            output_lines.append("## Previous Chapters Summary")
            output_lines.append("")
            for j in range(i):
                prev = all_summaries[j]
                prev_title = prev['header'].split('\n')[0].lstrip('#').strip() if prev['header'] else f"Chapter {j+1}"
                output_lines.append(f"**{prev_title}:** {prev['condensed']}")
                output_lines.append("")
            output_lines.append("---")
            output_lines.append("")

        # Current chapter (full detail)
        output_lines.append(f"## Current Chapter — {title_line.lstrip('#').strip()}")
        output_lines.append("")
        output_lines.append(current['summary'])
        output_lines.append("")

        if current['moments']:
            output_lines.append("### Key Moments")
            output_lines.append("")
            output_lines.append(current['moments'])
            output_lines.append("")

        # Write cumulative summary
        output = '\n'.join(output_lines)
        outfile = os.path.join(CUMULATIVE_DIR, current['file'])
        with open(outfile, 'w', encoding='utf-8') as f:
            f.write(output)

        print(f"  {current['file']} — {i+1} chapters summarized")


if __name__ == '__main__':
    print("Building cumulative summaries...")
    build_cumulative()
    print(f"Done. Files written to {CUMULATIVE_DIR}")
