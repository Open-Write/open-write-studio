"""
Convert a Fountain screenplay to industry-standard PDF format.

Professional screenplay formatting:
- Courier 12pt
- 1.5" left margin, 1" right/top/bottom
- Character names: centered, ALL CAPS, 3.7" from left edge
- Dialogue: centered block, 2.5" from left, 3.5" wide
- Parentheticals: 3.1" from left, 2.3" wide
- Scene headings: ALL CAPS, left-aligned at margin
- Page numbers: upper right, starting page 2

Usage: python tools/fountain_to_pdf.py <input.fountain> <output.pdf>
"""

import re
import sys
from fpdf import FPDF

# Industry standard screenplay margins (in inches)
LEFT_MARGIN_IN = 1.5
RIGHT_MARGIN_IN = 1.0
TOP_MARGIN_IN = 1.0
BOTTOM_MARGIN_IN = 1.0

# Character/dialogue positioning (in inches from left edge of page)
CHAR_NAME_LEFT_IN = 3.7  # character name starts here
DIALOGUE_LEFT_IN = 2.5   # dialogue starts here
DIALOGUE_WIDTH_IN = 3.5  # dialogue block width
PAREN_LEFT_IN = 3.1      # parenthetical starts here
PAREN_WIDTH_IN = 2.3     # parenthetical width

FONT_SIZE = 12
LINE_HEIGHT_PT = 12


def inches_to_mm(inches):
    return inches * 25.4


class ScreenplayPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.first_page = True
        self.set_auto_page_break(auto=True, margin=inches_to_mm(BOTTOM_MARGIN_IN))
        self.set_margins(
            inches_to_mm(LEFT_MARGIN_IN),
            inches_to_mm(TOP_MARGIN_IN),
            inches_to_mm(RIGHT_MARGIN_IN)
        )

    def header(self):
        if self.first_page:
            return
        self.set_font('Courier', '', FONT_SIZE)
        self.set_y(inches_to_mm(TOP_MARGIN_IN) - 4)
        self.set_x(self.w - inches_to_mm(RIGHT_MARGIN_IN) - 15)
        self.cell(15, 5, f'{self.page_no()}.', align='R')
        self.set_y(inches_to_mm(TOP_MARGIN_IN))

    def footer(self):
        pass

    @staticmethod
    def sanitize(text):
        """Replace Unicode chars with latin-1 equivalents."""
        replacements = {
            '\u2014': '--', '\u2013': '-', '\u2018': "'", '\u2019': "'",
            '\u201c': '"', '\u201d': '"', '\u2026': '...', '\u00a0': ' ',
            '\u200b': '', '\u00e9': 'e', '\u00e8': 'e',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text.encode('latin-1', errors='replace').decode('latin-1')


def parse_fountain(text):
    """
    Parse Fountain markup into typed blocks.
    Returns (title, author, blocks) where blocks is list of (type, content).
    """
    lines = text.split('\n')
    blocks = []
    i = 0
    title = None
    author = None

    # Parse title page metadata
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('Title:'):
            title = line[6:].strip()
            i += 1
            continue
        elif line.startswith('Credit:'):
            i += 1
            continue
        elif line.startswith('Author:'):
            author = line[7:].strip()
            i += 1
            continue
        elif line.startswith('Draft date:'):
            i += 1
            continue
        elif line == '' and (title or author):
            i += 1
            break
        elif not line:
            i += 1
            continue
        else:
            break

    # Parse body
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            blocks.append(('blank', ''))
            i += 1
            continue

        # Page break
        if stripped == '===':
            blocks.append(('page_break', ''))
            i += 1
            continue

        # Scene heading (INT./EXT./EST./INT/EXT or .forced)
        if re.match(r'^(INT\.|EXT\.|EST\.|INT/EXT\.|I/E\.)', stripped, re.IGNORECASE) or stripped.startswith('.'):
            heading = stripped.lstrip('.').upper()
            blocks.append(('scene_heading', heading))
            i += 1
            continue

        # Transition (ALL CAPS ending with TO: or FADE IN/FADE OUT)
        if re.match(r'^[A-Z\s]+:$', stripped) or stripped in ('FADE IN:', 'FADE OUT.', 'FADE TO BLACK.', 'CUT TO BLACK.'):
            blocks.append(('transition', stripped))
            i += 1
            continue

        # Centered text (> text <)
        if stripped.startswith('>') and stripped.endswith('<'):
            blocks.append(('centered', stripped[1:-1].strip()))
            i += 1
            continue

        # Character name (ALL CAPS, possibly with (V.O.) or (CONT'D))
        if re.match(r'^[A-Z][A-Z\s\.]+(\s*\(.*\))?$', stripped) and len(stripped) < 50:
            char_name = stripped
            blocks.append(('character', char_name))
            i += 1
            # Collect dialogue and parentheticals
            while i < len(lines):
                dline = lines[i].strip()
                if not dline:
                    break
                if dline.startswith('(') and dline.endswith(')'):
                    blocks.append(('parenthetical', dline))
                else:
                    blocks.append(('dialogue', dline))
                i += 1
            continue

        # Action / description
        blocks.append(('action', stripped))
        i += 1

    return title, author, blocks


def render_pdf(title, author, blocks, output_path):
    """Render parsed Fountain blocks into a screenplay-formatted PDF."""
    pdf = ScreenplayPDF()
    pdf.add_page()

    # Title page
    if title:
        pdf.set_font('Courier', '', FONT_SIZE)
        pdf.set_y(inches_to_mm(3.5))
        pdf.cell(0, 6, pdf.sanitize(title), align='C', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(6)
        pdf.cell(0, 6, 'written by', align='C', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(6)
        if author:
            pdf.cell(0, 6, pdf.sanitize(author), align='C', new_x='LMARGIN', new_y='NEXT')
        pdf.first_page = False
        pdf.add_page()

    line_h = inches_to_mm(LINE_HEIGHT_PT / 72)  # convert pt to mm

    for block_type, content in blocks:
        if block_type == 'blank':
            pdf.ln(line_h)
            continue

        if block_type == 'page_break':
            pdf.add_page()
            continue

        if block_type == 'scene_heading':
            pdf.ln(line_h)
            pdf.set_font('Courier', '', FONT_SIZE)
            pdf.set_x(inches_to_mm(LEFT_MARGIN_IN))
            pdf.cell(0, line_h, pdf.sanitize(content), new_x='LMARGIN', new_y='NEXT')
            pdf.ln(line_h)
            continue

        if block_type == 'transition':
            pdf.set_font('Courier', '', FONT_SIZE)
            pdf.cell(0, line_h, pdf.sanitize(content), align='R', new_x='LMARGIN', new_y='NEXT')
            pdf.ln(line_h)
            continue

        if block_type == 'centered':
            pdf.set_font('Courier', '', FONT_SIZE)
            pdf.cell(0, line_h, pdf.sanitize(content), align='C', new_x='LMARGIN', new_y='NEXT')
            continue

        if block_type == 'character':
            pdf.ln(line_h)
            pdf.set_font('Courier', '', FONT_SIZE)
            char_x = inches_to_mm(CHAR_NAME_LEFT_IN)
            pdf.set_x(char_x)
            pdf.cell(inches_to_mm(DIALOGUE_WIDTH_IN), line_h, pdf.sanitize(content), align='L', new_x='LMARGIN', new_y='NEXT')
            continue

        if block_type == 'parenthetical':
            pdf.set_font('Courier', '', FONT_SIZE)
            paren_x = inches_to_mm(PAREN_LEFT_IN)
            pdf.set_x(paren_x)
            pdf.multi_cell(inches_to_mm(PAREN_WIDTH_IN), line_h, pdf.sanitize(content))
            continue

        if block_type == 'dialogue':
            pdf.set_font('Courier', '', FONT_SIZE)
            dial_x = inches_to_mm(DIALOGUE_LEFT_IN)
            pdf.set_x(dial_x)
            pdf.multi_cell(inches_to_mm(DIALOGUE_WIDTH_IN), line_h, pdf.sanitize(content))
            pdf.ln(line_h)
            continue

        if block_type == 'action':
            pdf.set_font('Courier', '', FONT_SIZE)
            pdf.set_x(inches_to_mm(LEFT_MARGIN_IN))
            pdf.multi_cell(0, line_h, pdf.sanitize(content))
            pdf.ln(line_h)
            continue

    pdf.output(output_path)
    return pdf.pages_count


def main():
    if len(sys.argv) < 3:
        print("Usage: python fountain_to_pdf.py <input.fountain> <output.pdf>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    title, author, blocks = parse_fountain(text)
    pages = render_pdf(title, author, blocks, output_path)

    print(f'PDF written to {output_path}')
    print(f'Pages: {pages}')
    print(f'Title: {title or "(none)"}')
    print(f'Author: {author or "(none)"}')


if __name__ == '__main__':
    main()
