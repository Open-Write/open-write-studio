# PDF Export Guide — Novel

*How to export novels to PDF from the novel template. Covers chapter export, full manuscript export, and assembly.*

---

## Overview

The novel template has three PDF export paths:

| Tool | Input | Output | Location |
|------|-------|--------|----------|
| `tools/assemble.py` | Chapter files | Assembled manuscript (.md) | [`tools/assemble.py`](../tools/assemble.py) |
| `tools/novel_chapter_export.py` | Full manuscript | Per-chapter PDFs + full PDF | [`tools/novel_chapter_export.py`](../tools/novel_chapter_export.py) |
| `tools/export_formats.py` | Full manuscript | TXT + PDF | [`tools/export_formats.py`](../tools/export_formats.py) |

---

## Step 1: Assemble the Manuscript

Before exporting, assemble chapter files into a single manuscript:

```bash
set PYTHONIOENCODING=utf-8 && python tools/assemble.py --title "Your Title" --author "Your Name"
```

This reads all chapter files from `manuscript/chapters/` and produces a single `manuscript/novel.md` (or whatever you name it via `--output`).

**Chapter file naming convention:** Files in `manuscript/chapters/` should follow the pattern:
- `NNN_track_a_Title.md` for Track A chapters
- `NNN_track_b_Title.md` for Track B chapters
- `NNN_interlude_Title.md` for interludes

Where `NNN` is the chapter number (e.g., `001`, `002`, etc.).

---

## Step 2: Export Per-Chapter PDFs

```bash
set PYTHONIOENCODING=utf-8 && python tools/novel_chapter_export.py
```

**What each chapter PDF includes:**
- Chapter title and number header (e.g., "Chapter 12 — The Equations")
- Running page numbers
- Standard manuscript formatting (12pt Times, double-spaced, 1-inch margins)
- Header on each page (except first): title | chapter name

**Output location:** Chapter PDFs are saved to `manuscript/chapters_pdf/`.

**When to use:** During revision passes when you need to review individual chapters in formatted PDF. Also useful for sending individual chapters to beta readers or editors.

---

## Step 3: Export Full Manuscript

```bash
set PYTHONIOENCODING=utf-8 && python tools/export_formats.py
```

**Produces:**
- Full manuscript TXT (`manuscript/novel_full_revised.txt`)
- Full manuscript PDF (`manuscript/novel_full_revised.pdf`)

**When to use:** When the full manuscript is complete and ready for submission or comprehensive review.

---

## Requirements

```bash
pip install fpdf2
```

The export tools use `fpdf2` (not the original `fpdf`). Install with the command above.

---

## Customizing Headers and Footers

The novel chapter PDFs include:
- **Header (each page, except first):** Title | Chapter name
- **Footer (each page):** Page number centered
- **First page:** Chapter number and title as section header

To customize headers/footers, modify `tools/novel_chapter_export.py`. The header template is defined in the `NovelPDF` class.

---

## Known Issues

### Character Encoding

Always set `PYTHONIOENCODING=utf-8` before running export tools. Without this, emoji characters and special Unicode in prose may cause encoding errors.

### Unicode Replacement

The PDF export replaces Unicode characters with latin-1 equivalents:
- Em dashes (—) → `--`
- Curly quotes → straight quotes
- Ellipsis (…) → `...`
- Accented characters → ASCII equivalents

This is necessary because the default PDF font (Times) uses latin-1 encoding. If you need full Unicode support, modify the font configuration in the export script.

### Word Count

The `word_count.py` tool counts words in chapter files. The `export_formats.py` tool reports word count of the assembled manuscript. These may differ slightly due to header/footer stripping.

---

## Workflow Summary

```
1. Write chapters → manuscript/chapters/NNN_track_a_Title.md
2. Run prose audit → python tools/prose_audit.py
3. Run convention scan → python tools/convention_scan.py
4. Run cutter if critics flagged material → export the result
5. Assemble → python tools/assemble.py --title "Title" --author "Author"
6. Export per-chapter PDFs → python tools/novel_chapter_export.py
7. Export full manuscript → python tools/export_formats.py
8. Verify word count → python tools/word_count.py
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Assemble chapters | `set PYTHONIOENCODING=utf-8 && python tools/assemble.py --title "Title" --author "Author"` |
| Export chapter PDFs | `set PYTHONIOENCODING=utf-8 && python tools/novel_chapter_export.py` |
| Export full manuscript | `set PYTHONIOENCODING=utf-8 && python tools/export_formats.py` |
| Count words | `set PYTHONIOENCODING=utf-8 && python tools/word_count.py` |
| Check track balance | `set PYTHONIOENCODING=utf-8 && python tools/track_balance.py` |
| Build cumulative summaries | `set PYTHONIOENCODING=utf-8 && python tools/build_cumulative_summaries.py` |
