"""
Export the novel manuscript to TXT and PDF formats.
Reads manuscript/novel.md and produces:
  - manuscript/novel.txt
  - manuscript/novel.pdf
"""

import re
import os
from fpdf import FPDF

INPUT = os.path.join(os.path.dirname(__file__), '..', 'manuscript', 'novel.md')
TXT_OUT = os.path.join(os.path.dirname(__file__), '..', 'manuscript', 'novel.txt')
PDF_OUT = os.path.join(os.path.dirname(__file__), '..', 'manuscript', 'novel.pdf')


def read_manuscript():
    with open(INPUT, 'r', encoding='utf-8') as f:
        return f.read()


def md_to_plain_text(md: str) -> str:
    """Strip markdown formatting to produce clean plain text."""
    text = md
    # Title page
    text = re.sub(r'^#\s+(.+)$', r'\1', text, flags=re.MULTILINE)  # # heading -> heading
    text = re.sub(r'^\*(.+)\*$', r'\1', text, flags=re.MULTILINE)  # *italic* -> italic
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # **bold** -> bold
    text = re.sub(r'\*(.+?)\*', r'\1', text)  # *italic* -> italic
    text = re.sub(r'---+', '\n\n', text)  # horizontal rules -> blank line
    # Clean up multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


class NovelPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        pass  # No header on regular pages

    def footer(self):
        self.set_y(-15)
        self.set_font('Times', 'I', 9)
        self.cell(0, 10, f'{self.page_no()}', align='C')

    def title_page(self, title, author):
        self.add_page()
        self.set_font('Times', 'B', 28)
        self.ln(60)
        self.cell(0, 14, self.sanitize(title), align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(8)
        self.set_font('Times', '', 16)
        self.cell(0, 10, self.sanitize(f'by {author}'), align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(40)
        self.set_font('Times', 'I', 11)
        self.cell(0, 8, 'A Novel', align='C', new_x='LMARGIN', new_y='NEXT')

    def part_page(self, part_name):
        self.add_page()
        self.set_font('Times', 'B', 20)
        self.ln(80)
        self.cell(0, 14, self.sanitize(part_name), align='C', new_x='LMARGIN', new_y='NEXT')

    def chapter_heading(self, title):
        self.ln(20)
        self.set_font('Times', 'B', 16)
        self.cell(0, 12, self.sanitize(title), align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(8)
        self.set_font('Times', '', 11)

    @staticmethod
    def sanitize(text):
        """Replace Unicode characters with latin-1 equivalents for PDF."""
        replacements = {
            '\u2014': '--',   # em dash
            '\u2013': '-',    # en dash
            '\u2018': "'",    # left single quote
            '\u2019': "'",    # right single quote
            '\u201c': '"',    # left double quote
            '\u201d': '"',    # right double quote
            '\u2026': '...',  # ellipsis
            '\u00a0': ' ',    # non-breaking space
            '\u200b': '',     # zero-width space
            '\u2022': '-',    # bullet
            '\u00b7': '-',    # middle dot
            '\u2010': '-',    # hyphen
            '\u2011': '-',    # non-breaking hyphen
            '\u2012': '-',    # figure dash
            '\u00e9': 'e',    # e-acute
            '\u00e8': 'e',    # e-grave
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        # Strip any remaining non-latin-1 characters
        text = text.encode('latin-1', errors='replace').decode('latin-1')
        return text

    def add_body_text(self, text):
        self.set_font('Times', '', 11)
        # Clean markdown artifacts
        text = text.replace('*', '').replace('#', '')
        text = self.sanitize(text.strip())
        if text:
            self.multi_cell(0, 5.5, text)
            self.ln(2)


def build_pdf(md: str):
    """Build PDF from markdown source."""
    pdf = NovelPDF()

    # Title page
    pdf.title_page('Untitled', 'Author')

    # Parse the manuscript into structural sections
    lines = md.split('\n')

    current_section = []
    current_heading = None
    in_title_block = True  # Skip the title/author block at the top
    title_block_done = False

    for line in lines:
        stripped = line.strip()

        # Skip the initial title block (# Title, *by Author*)
        if not title_block_done:
            if stripped.startswith('# ') and not stripped.startswith('# Chapter') and not stripped.startswith('# Part') and not stripped.startswith('# Interlude'):
                continue
            if stripped.startswith('*by '):
                continue
            if stripped == '---':
                if not any(s.strip() for s in current_section if s.strip()):
                    title_block_done = True
                    continue
            if stripped.startswith('# Chapter') or stripped.startswith('# Interlude') or stripped.startswith('# Part'):
                title_block_done = True
                # Fall through to process this heading

        if not title_block_done:
            continue

        # Detect headings
        if stripped.startswith('# Part'):
            # Flush current section
            if current_section:
                body = '\n'.join(current_section).strip()
                if body:
                    pdf.add_body_text(body)
                current_section = []

            # Part page
            part_name = stripped.lstrip('#').strip()
            pdf.part_page(part_name)
            pdf.add_page()
            pdf.set_font('Times', '', 11)
            continue

        if stripped.startswith('# Chapter') or stripped.startswith('# Interlude'):
            # Flush current section
            if current_section:
                body = '\n'.join(current_section).strip()
                if body:
                    pdf.add_body_text(body)
                current_section = []

            # Chapter heading
            heading = stripped.lstrip('#').strip()
            pdf.chapter_heading(heading)
            continue

        # Section break (---)
        if stripped == '---':
            if current_section:
                body = '\n'.join(current_section).strip()
                if body:
                    pdf.add_body_text(body)
                    pdf.ln(3)
                current_section = []
            continue

        # Regular content
        current_section.append(line)

    # Flush final section
    if current_section:
        body = '\n'.join(current_section).strip()
        if body:
            pdf.add_body_text(body)

    pdf.output(PDF_OUT)
    print(f'PDF written to {PDF_OUT}')
    print(f'Pages: {pdf.pages_count}')


def main():
    md = read_manuscript()

    # TXT
    plain = md_to_plain_text(md)
    with open(TXT_OUT, 'w', encoding='utf-8') as f:
        f.write(plain)
    print(f'TXT written to {TXT_OUT}')
    print(f'Words: {len(plain.split())}')

    # PDF
    build_pdf(md)


if __name__ == '__main__':
    main()
