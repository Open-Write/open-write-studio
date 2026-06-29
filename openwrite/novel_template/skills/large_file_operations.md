# Large File Operations Guide

*Working with large files (1,000+ lines) for novel production work.*

---

## Why Large Files Are Problematic

### Memory Issues
- **Tool buffer limits**: The Read tool has a 2000-line limit per call
- **Context consumption**: Large files consume token budget, reducing available context for other tasks
- **Parsing overhead**: Complex parsers (Markdown, JSON) slow down on large inputs

### Tool Limitations
- **Read tool truncation**: Files over 2000 lines are automatically truncated
- **Edit tool failures**: Large oldString/newString combinations exceed character limits
- **Timeout errors**: Processing large files can exceed tool timeout limits (120s default)

### Common Large Files

| File Type | Typical Size | Example |
|-----------|--------------|---------|
| Full novel manuscript | 50,000+ words | `manuscript/novel_full.md` |
| Bible full file | 500+ lines | `bible/00_bible_full.md` |
| State JSON files | 500+ KB | `state/callback_ledger.json` |
| Chapter files | 2,000+ words | `manuscript/chapters/chapter_01.md` |

---

## PowerShell Streaming

### Read File in Chunks

```powershell
Get-Content -Path "manuscript/novel_full.md" -First 100
Get-Content -Path "manuscript/novel_full.md" -Tail 50
Get-Content -Path "manuscript/novel_full.md" -ReadCount 1000 | ForEach-Object { $_ }
```

### Process Line by Line

```powershell
(Get-Content -Path "manuscript/novel_full.md").Count
Select-String -Path "manuscript/novel_full.md" -Pattern "Chapter" | Measure-Object
Get-Content -Path "manuscript/novel_full.md" | Select-Object -Skip 499 -First 51
```

### Write Large Files

```powershell
Get-Content -Path "manuscript/chapters/*.md" | Out-File -FilePath "manuscript/novel_full.md" -Encoding utf8
```

---

## Bash Streaming

### Read File in Chunks

```bash
head -n 100 manuscript/novel_full.md
tail -n 50 manuscript/novel_full.md
sed -n '500,550p' manuscript/novel_full.md
wc -l manuscript/novel_full.md
```

### Split Large Files

```bash
split -l 2000 -d manuscript/novel_full.md manuscript/chunk_
```

---

## Python Streaming

### Read Line by Line

```python
def read_in_chunks(file_path, chunk_size=1000):
    chunks = []
    current_chunk = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            current_chunk.append(line)
            if len(current_chunk) >= chunk_size:
                chunks.append((line_num - len(current_chunk) + 1, current_chunk))
                current_chunk = []
    if current_chunk:
        chunks.append((line_num - len(current_chunk) + 1, current_chunk))
    return chunks
```

### Process Large JSON Files

```python
import json

def update_state_file(file_path, update_func):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    update_func(data)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
```

---

## File Splitting

### Split Manuscript by Chapter

```python
def split_by_chapter(input_path, output_dir):
    import os, re
    os.makedirs(output_dir, exist_ok=True)
    current_chapter = None
    current_content = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            if re.match(r'^#\s+Chapter\s+\d+', line) or re.match(r'^#\s+Chapter\s+\w+', line):
                if current_chapter:
                    output_path = os.path.join(output_dir, f"{current_chapter}.md")
                    with open(output_path, 'w', encoding='utf-8') as out:
                        out.writelines(current_content)
                current_chapter = line.strip().replace(' ', '_')[:30]
                current_content = [line]
            else:
                current_content.append(line)
    if current_chapter:
        output_path = os.path.join(output_dir, f"{current_chapter}.md")
        with open(output_path, 'w', encoding='utf-8') as out:
            out.writelines(current_content)
```

---

## Best Practices

### Chunk Size Recommendations

| Operation | Recommended Chunk Size | Rationale |
|-----------|------------------------|-----------|
| Reading for review | 500-1000 lines | Fits in Read tool limit |
| Editing files | 200-500 lines | Keeps oldString/newString manageable |
| Processing Python output | 1000-2000 lines | Balances memory and I/O |

### File Organization

1. **Split assembled manuscripts**: Keep per-chapter files in `chapters/` subdirectory
2. **Encoding**: Always use UTF-8 encoding for Markdown and JSON files
3. **Line endings**: Normalize to LF (Unix) for consistency

---

## Troubleshooting

### Memory Errors
**Symptom**: `MemoryError` or tool timeout
**Solutions**: Reduce chunk size, use streaming, process in batches

### Encoding Issues
**Symptom**: `UnicodeDecodeError` or garbled text
**Solutions**: Always specify `encoding='utf-8'`, normalize line endings

### Tool Timeout
**Symptom**: Operation exceeds 120 second timeout
**Solutions**: Split operation into smaller batches, implement checkpointing

---

## Quick Reference

### PowerShell

```powershell
Get-Content file.txt -First 100
Get-Content file.txt -Tail 50
(Get-Content file.txt).Count
Select-String -Path file.txt -Pattern "pattern"
```

### Bash

```bash
head -n 100 file.txt
tail -n 50 file.txt
wc -l file.txt
grep "pattern" file.txt
split -l 1000 -d file.txt chunk_
```

*This guide is based on lessons learned from production work with large manuscript and JSON files.*
