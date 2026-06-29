# Large File Operations Guide

*Working with large files (1,000+ lines) for screenplay production work.*

---

## Why Large Files Are Problematic

### Memory Issues
- **Tool buffer limits**: The Read tool has a 2000-line limit per call
- **Context consumption**: Large files consume token budget, reducing available context for other tasks
- **Parsing overhead**: Complex parsers (Fountain, JSON) slow down on large inputs

### Tool Limitations
- **Read tool truncation**: Files over 2000 lines are automatically truncated
- **Edit tool failures**: Large oldString/newString combinations exceed character limits
- **Timeout errors**: Processing large files can exceed tool timeout limits (120s default)

### Common Large Files

| File Type | Typical Size | Example |
|-----------|--------------|---------|
| Assembled screenplay Fountain | 1,500+ lines | `script/screenplay.fountain` |
| Bible full file | 500+ lines | `bible/00_bible_full.md` |
| State JSON files | 500+ KB | `state/callback_ledger.json` |
| Python tools | 500+ lines | `tools/fountain_to_pdf.py` |

---

## PowerShell Streaming

### Read File in Chunks

```powershell
Get-Content -Path "script/screenplay.fountain" -First 100
Get-Content -Path "script/screenplay.fountain" -Tail 50
Get-Content -Path "script/screenplay.fountain" -ReadCount 1000 | ForEach-Object { $_ }
```

### Process Line by Line

```powershell
(Get-Content -Path "script/screenplay.fountain").Count
Select-String -Path "script/screenplay.fountain" -Pattern "INT\." | Measure-Object
Get-Content -Path "script/screenplay.fountain" | Select-Object -Skip 499 -First 51
```

### Write Large Files

```powershell
Get-Content -Path "script/scenes/*.fountain" | Out-File -FilePath "script/assembled.fountain" -Encoding utf8
```

---

## Bash Streaming

### Read File in Chunks

```bash
head -n 100 script/screenplay.fountain
tail -n 50 script/screenplay.fountain
sed -n '500,550p' script/screenplay.fountain
wc -l script/screenplay.fountain
```

### Split Large Files

```bash
split -l 2000 -d script/screenplay.fountain script/chunk_
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

### Split Fountain by Scene

```python
def split_fountain_by_scene(input_path, output_dir):
    import os
    os.makedirs(output_dir, exist_ok=True)
    current_scene = None
    current_content = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('SCENE ') or (line.strip().startswith('INT.') or line.strip().startswith('EXT.')):
                if current_scene:
                    output_path = os.path.join(output_dir, f"{current_scene}.fountain")
                    with open(output_path, 'w', encoding='utf-8') as out:
                        out.writelines(current_content)
                current_scene = line.strip().replace(' ', '_')[:30]
                current_content = [line]
            else:
                current_content.append(line)
    if current_scene:
        output_path = os.path.join(output_dir, f"{current_scene}.fountain")
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

1. **Split assembled files**: Keep per-scene files in `scenes/` subdirectory
2. **Encoding**: Always use UTF-8 encoding for Fountain and JSON files
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

*This guide is based on lessons learned from production work with large Fountain and JSON files.*
