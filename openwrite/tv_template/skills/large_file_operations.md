# Large File Operations Guide

*Working with large files (1,000+ lines) for TV production work.*

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
| Assembled episode Fountain | 2,000+ lines | `scripts/S01E01/S01E01.fountain` |
| Season assemble output | 10,000+ lines | `scripts/season_1.fountain` |
| State JSON files | 500+ KB | `state/character_state_tracker.json` |
| Python tools | 500+ lines | `tools/episode_assemble.py` |

---

## PowerShell Streaming

### Read File in Chunks

```powershell
Get-Content -Path "scripts/S01E01/S01E01.fountain" -First 100
Get-Content -Path "scripts/S01E01/S01E01.fountain" -Tail 50
Get-Content -Path "scripts/season_1.fountain" -ReadCount 1000 | ForEach-Object { $_ }
```

### Process Line by Line

```powershell
(Get-Content -Path "scripts/S01E01/S01E01.fountain").Count
Select-String -Path "scripts/S01E01/S01E01.fountain" -Pattern "INT\." | Measure-Object
Get-Content -Path "scripts/S01E01/S01E01.fountain" | Select-Object -Skip 499 -First 51
```

### Write Large Files

```powershell
Get-Content -Path "scripts/S01E01/scenes/*.fountain" | Out-File -FilePath "scripts/S01E01/S01E01.assembled" -Encoding utf8
```

---

## Bash Streaming

### Read File in Chunks

```bash
head -n 100 scripts/S01E01/S01E01.fountain
tail -n 50 scripts/S01E01/S01E01.fountain
sed -n '500,550p' scripts/S01E01/S01E01.fountain
wc -l scripts/S01E01/S01E01.fountain
```

### Split Large Files

```bash
split -l 2000 -d scripts/season_1.fountain scripts/season_1_chunk_
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

### Split by Line Count (PowerShell)

```powershell
$file = "scripts/S01E01/S01E01.fountain"
$lines = Get-Content $file
$chunkSize = 500
for ($i = 0; $i -lt $lines.Count; $i += $chunkSize) {
    $chunk = $lines[$i..[Math]::Min($i + $chunkSize - 1, $lines.Count - 1)]
    $chunk | Out-File "scripts/S01E01/chunk_$($i/$chunkSize).fountain" -Encoding utf8
}
```

---

## Incremental Construction

### Build Episode from Scenes

```python
def assemble_episode_incrementally(scene_dir, output_path):
    import os
    scene_files = sorted([f for f in os.listdir(scene_dir) if f.endswith('.fountain')])
    with open(output_path, 'w', encoding='utf-8') as out:
        for scene_file in scene_files:
            scene_path = os.path.join(scene_dir, scene_file)
            with open(scene_path, 'r', encoding='utf-8') as f:
                out.write(f.read())
            out.write('\n\n')
```

---

## Best Practices

### Memory Efficiency

1. **Always stream, never load entire file**: Use streaming readers instead of `file.read()`
2. **Process line by line**: For simple operations, iterate line by line
3. **Use generators**: For large datasets, use generators instead of lists
4. **Close file handles**: Always close files explicitly or use context managers

### Chunk Size Recommendations

| Operation | Recommended Chunk Size | Rationale |
|-----------|------------------------|-----------|
| Reading for review | 500-1000 lines | Fits in Read tool limit |
| Editing files | 200-500 lines | Keeps oldString/newString manageable |
| Processing Python output | 1000-2000 lines | Balances memory and I/O |
| Splitting for parallel processing | 5000-10000 lines | Reduces overhead |

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

*This guide is based on lessons learned from production work with large Fountain, JSON, and Python files.*
