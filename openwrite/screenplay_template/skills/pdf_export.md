# PDF Export Guide

*How to export screenplays to PDF. Covers the Fountain-to-PDF pipeline.*

---

## Overview

The template provides a PDF export path:

| Tool | Input | Output | Location |
|------|-------|--------|----------|
| `tools/fountain_to_pdf.py` | Fountain file | Screenplay PDF (spec layout) | [`tools/fountain_to_pdf.py`](../tools/fountain_to_pdf.py) |

---

## Screenplay PDF Export

### Tool: `tools/fountain_to_pdf.py`

Converts Fountain markup to industry-standard screenplay PDF using fpdf2.

**Requirements:**
```bash
pip install fpdf2
```

**Usage:**
```bash
set PYTHONIOENCODING=utf-8 && python tools\fountain_to_pdf.py script\screenplay.fountain script\screenplay.pdf
```

**Format spec:**
- Font: Courier 12pt
- Left margin: 1.5 inches
- Right margin: 1 inch
- Top margin: 1 inch
- Bottom margin: 1 inch
- Page numbers: upper right
- Title page: centered title, author below

### Assembly Before Export

Before exporting a screenplay to PDF, assemble the scene files into a single Fountain file:

```bash
set PYTHONIOENCODING=utf-8 && python tools\assemble_screenplay.py --title "My Screenplay" --author "Original Screenplay by Author Name"
```

This produces `script/screenplay.fountain`, which can then be converted to PDF.

---

## Customizing Headers and Footers

The screenplay PDF follows industry standard formatting:
- **Header:** None (standard spec format has no header)
- **Footer:** Page number upper right
- **Title page:** Centered title, "written by" + author name below

To customize, modify `tools/fountain_to_pdf.py`. The reportlab layout is defined in the `render_pdf()` function.

---

## Known Issues

### Page Count Discrepancy

The `page_count.py` tool estimates from Fountain line count using a rough formula. The `fountain_to_pdf.py` tool renders using actual Courier 12pt layout with proper margins. The discrepancy can be significant — always use PDF page count for industry submission.

**Workaround:** Use line count for internal tracking. Use PDF page count only for submission.

### Font Rendering

The PDF uses Courier (a monospace font) as required by screenplay industry standards. If Courier is not available on the system, fpdf2 falls back to a built-in monospace font. This may cause minor layout differences.

### Character Encoding

Always set `PYTHONIOENCODING=utf-8` before running export tools. Without this, emoji characters and special Unicode in action lines may cause encoding errors.

---

## Workflow Summary

```
1. Write scenes → script/scenes/*.fountain
2. Run critics → revise
3. Run cutter if critics flagged material → export the result
4. Assemble → python tools\assemble_screenplay.py
5. Export PDF → python tools\fountain_to_pdf.py script\screenplay.fountain script\screenplay.pdf
6. Verify page count → check PDF page count (not page_count.py estimate)
```
