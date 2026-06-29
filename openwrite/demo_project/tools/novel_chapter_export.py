"""
Fix line spacing in the novel manuscript and generate per-chapter PDFs.

1. Normalizes blank lines: collapses multiple blank lines to single blank lines
2. Splits into chapters by "# Chapter" or "# Part" headings
3. Generates individual chapter PDFs with title/header on each page
4. Places chapter PDFs in manuscript/chapters_pdf/

Usage: python tools/novel_chapter_export.py
"""

import os
import re
from fpdf import FPDF

INPUT = os.path.join(os.path.dirname(__file__), '..', 'manuscript', 'novel.md')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'manuscript', 'chapters_pdf')
FULL_PDF = os.path.join(os.path.dirname(__file__), '..', 'manuscript', 'novel.pdf')
FULL_TXT = os.path.join(os.path.dirname(__file__), '..', 'manuscript', 'novel.txt')

TITLE = "Untitled"
AUTHOR = "Author"


class NovelPDF(FPDF):
    def __init__(self, chapter_title=""):
        super().__init__()
        self.chapter_title = chapter_title
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() == 1:
            return  # No header on first page of each chapter
        self.set_font('Times', 'I', 9)
        self.set_y(10)
        safe = self._sanitize(self.chapter_title)
        self.cell(0, 5, f'{TITLE}  |  {safe}', align='C', new_x='LMARGIN', new_y='NEXT')
        self.set_y(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', 'I', 9)
        self.cell(0, 10, f'{self.page_no()}', align='C')

    @staticmethod
    def _sanitize(text):
        replacements = {
            '\u2014': '--', '\u2013': '-', '\u2018': "'", '\u2019': "'",
            '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u00a0': ' ',
            '\u200b': '', '\u00e9': 'e', '\u00e8': 'e',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text.encode('latin-1', errors='replace').decode('latin-1')


def normalize_spacing(text):
    """Collapse multiple blank lines to single blank lines."""
    # Replace 2+ consecutive newlines with exactly 2 (one blank line)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Also strip trailing whitespace on each line
    lines = text.split('\n')
    lines = [line.rstrip() for line in lines]
    return '\n'.join(lines)


def split_chapters(text):
    """Split manuscript into chapters by # heading lines."""
    lines = text.split('\n')
    chapters = []
    current_title = "Front Matter"
    current_lines = []
    part_name = ""

    for line in lines:
        # Part heading
        if re.match(r'^# Part \d+', line):
            # Save any accumulated front matter
            if current_lines and current_title == "Front Matter":
                chapters.append((current_title, '\n'.join(current_lines)))
                current_lines = []
            part_name = line.lstrip('#').strip()
            current_lines.append(line)
            continue

        # Chapter heading
        if re.match(r'^# Chapter \d+', line):
            # Save previous chapter
            if current_lines:
                chapters.append((current_title, '\n'.join(current_lines)))
                current_lines = []
            chapter_title = line.lstrip('#').strip()
            if part_name:
                current_title = f"{part_name} — {chapter_title}"
            else:
                current_title = chapter_title
            current_lines.append(line)
            continue

        # Interlude heading
        if re.match(r'^# Interlude', line):
            if current_lines:
                chapters.append((current_title, '\n'.join(current_lines)))
                current_lines = []
            current_title = line.lstrip('#').strip()
            current_lines.append(line)
            continue

        current_lines.append(line)

    # Save last chapter
    if current_lines:
        chapters.append((current_title, '\n'.join(current_lines)))

    return chapters


def make_chapter_pdf(title, content, output_path):
    """Generate a PDF for a single chapter with header on each page."""
    pdf = NovelPDF(chapter_title=title)
    pdf.set_margins(25, 15, 25)  # left, top, right in mm
    pdf.add_page()

    # Chapter title on first page
    pdf.set_font('Times', 'B', 16)
    pdf.ln(20)
    safe_title = pdf._sanitize(title)
    pdf.cell(0, 10, safe_title, align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(10)

    # Body text
    pdf.set_font('Times', '', 11)
    line_height = 5.5

    paragraphs = content.split('\n\n')
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Section breaks (---)
        if para == '---':
            pdf.ln(line_height * 2)
            continue

        # Markdown headings within chapter
        if para.startswith('##'):
            heading_text = para.lstrip('#').strip()
            pdf.ln(line_height)
            pdf.set_font('Times', 'B', 13)
            pdf.cell(0, line_height, pdf._sanitize(heading_text), new_x='LMARGIN', new_y='NEXT')
            pdf.ln(line_height)
            pdf.set_font('Times', '', 11)
            continue

        # Italic text (e.g., *emphasis*)
        # For simplicity, strip markdown formatting
        clean = para.replace('*', '').replace('#', '')
        clean = pdf._sanitize(clean)

        if clean:
            pdf.multi_cell(0, line_height, clean)
            pdf.ln(line_height)

    pdf.output(output_path)
    return pdf.pages_count


def main():
    # Read manuscript
    with open(INPUT, 'r', encoding='utf-8') as f:
        text = f.read()

    # Normalize spacing
    normalized = normalize_spacing(text)
    word_count = len(normalized.split())

    # Write normalized version back
    with open(INPUT, 'w', encoding='utf-8') as f:
        f.write(normalized)

    # Write TXT
    with open(FULL_TXT, 'w', encoding='utf-8') as f:
        f.write(normalized)

    print(f'Manuscript normalized: {word_count} words, {len(normalized.splitlines())} lines')
    print(f'TXT written to {FULL_TXT}')

    # Split into chapters
    chapters = split_chapters(normalized)
    print(f'Found {len(chapters)} chapters/sections')

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate per-chapter PDFs
    total_pages = 0
    file_num = 0
    for title, content in chapters:
        # Skip front matter (title page, etc.)
        if 'Front Matter' in title:
            continue

        file_num += 1

        # Build short filename
        if 'Interlude' in title:
            interlude_name = title.replace('Interlude — ', '').replace('Interlude ', '')
            interlude_name = re.sub(r'[^\w\s]', '', interlude_name).strip()
            interlude_name = re.sub(r'\s+', '_', interlude_name)[:20]
            filename = f'{file_num:02d}_Interlude_{interlude_name}.pdf'
        elif 'Chapter' in title:
            ch_match = re.search(r'Chapter\s+(\d+)', title)
            ch_num = ch_match.group(1) if ch_match else '??'
            ch_name = title.split('—')[-1].strip() if '—' in title else title
            ch_name = re.sub(r'[^\w\s]', '', ch_name).strip()
            ch_name = re.sub(r'\s+', '_', ch_name)[:25]
            filename = f'{file_num:02d}_Ch{ch_num}_{ch_name}.pdf'
        else:
            short = re.sub(r'[^\w\s]', '', title).strip()
            short = re.sub(r'\s+', '_', short)[:25]
            filename = f'{file_num:02d}_{short}.pdf'

        filepath = os.path.join(OUTPUT_DIR, filename)

        pages = make_chapter_pdf(title, content, filepath)
        total_pages += pages
        print(f'  {file_num:02d}. {title} — {pages} pages ({filename})')

    # Generate full PDF
    full_pdf = NovelPDF(chapter_title="")
    full_pdf.set_margins(25, 15, 25)

    # Title page
    full_pdf.add_page()
    full_pdf.set_font('Times', 'B', 28)
    full_pdf.ln(60)
    full_pdf.cell(0, 14, TITLE, align='C', new_x='LMARGIN', new_y='NEXT')
    full_pdf.ln(8)
    full_pdf.set_font('Times', '', 16)
    full_pdf.cell(0, 10, f'by {AUTHOR}', align='C', new_x='LMARGIN', new_y='NEXT')
    full_pdf.ln(40)
    full_pdf.set_font('Times', 'I', 11)
    full_pdf.cell(0, 8, 'A Novel', align='C', new_x='LMARGIN', new_y='NEXT')

    # Body
    full_pdf.set_font('Times', '', 11)
    line_height = 5.5

    paragraphs = normalized.split('\n\n')
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if para == '---':
            full_pdf.ln(line_height * 2)
            continue

        # Part headings
        if re.match(r'^# Part \d+', para):
            heading = para.lstrip('#').strip()
            full_pdf.add_page()
            full_pdf.set_font('Times', 'B', 20)
            full_pdf.ln(60)
            full_pdf.cell(0, 12, full_pdf._sanitize(heading), align='C', new_x='LMARGIN', new_y='NEXT')
            full_pdf.ln(10)
            full_pdf.set_font('Times', '', 11)
            continue

        # Chapter headings
        if re.match(r'^# Chapter \d+', para) or re.match(r'^# Interlude', para):
            heading = para.lstrip('#').strip()
            full_pdf.ln(15)
            full_pdf.set_font('Times', 'B', 14)
            full_pdf.cell(0, 10, full_pdf._sanitize(heading), align='C', new_x='LMARGIN', new_y='NEXT')
            full_pdf.ln(8)
            full_pdf.set_font('Times', '', 11)
            continue

        # Sub-headings
        if para.startswith('##'):
            heading = para.lstrip('#').strip()
            full_pdf.ln(line_height)
            full_pdf.set_font('Times', 'B', 13)
            full_pdf.cell(0, line_height, full_pdf._sanitize(heading), new_x='LMARGIN', new_y='NEXT')
            full_pdf.ln(line_height)
            full_pdf.set_font('Times', '', 11)
            continue

        clean = para.replace('*', '').replace('#', '')
        clean = full_pdf._sanitize(clean)
        if clean:
            full_pdf.multi_cell(0, line_height, clean)
            full_pdf.ln(line_height)

    full_pdf.output(FULL_PDF)
    print(f'\nFull PDF: {FULL_PDF} — {full_pdf.pages_count} pages')
    print(f'Chapter PDFs: {OUTPUT_DIR} — {len(chapters)} files, {total_pages} total pages')


if __name__ == '__main__':
    main()
