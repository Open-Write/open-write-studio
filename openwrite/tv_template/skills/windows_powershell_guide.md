# Windows PowerShell Guide — TV Production System

*Windows PowerShell commands and patterns for TV production work. Use this guide when working on Windows PowerShell instead of Unix/bash.*

---

## 1. Environment Detection

Check your environment before proceeding:

```powershell
$PSVersionTable.PSVersion
if ($env:OS -like '*Windows*') { 'Running on Windows' }
Get-Command python, python3, git, node
python --version
```

---

## 2. PowerShell vs Bash Equivalents

| Bash | PowerShell | Description |
|------|-----------|-------------|
| `cat file` | `Get-Content file` | Read file |
| `cat > file` | `Set-Content file` | Write file |
| `cat >> file` | `Add-Content file` | Append to file |
| `head -n 10 file` | `Get-Content file -Head 10` | Read first 10 lines |
| `tail -n 10 file` | `Get-Content file -Tail 10` | Read last 10 lines |
| `wc -l file` | `(Get-Content file).Count` | Count lines |
| `grep pattern file` | `Select-String pattern file` | Search file |
| `rm file` | `Remove-Item file` | Delete file |
| `cp src dst` | `Copy-Item src dst` | Copy file |
| `mv src dst` | `Move-Item src dst` | Move file |
| `mkdir dir` | `New-Item -ItemType Directory dir` | Create directory |
| `ls` | `Get-ChildItem` | List directory |
| `pwd` | `Get-Location` | Show current directory |
| `find . -name '*.fountain'` | `Get-ChildItem -Recurse -Filter '*.fountain'` | Find files |

---

## 3. File Operations

### Reading Files

```powershell
Get-Content -Path 'scripts/S01E01/S01E01.fountain' -Encoding UTF8
Get-Content -Path 'scripts/S01E01/S01E01.fountain' -Head 10 -Encoding UTF8
Get-Content -Path 'scripts/S01E01/S01E01.fountain' -Tail 10 -Encoding UTF8
(Get-Content -Path 'scripts/S01E01/S01E01.fountain' -Encoding UTF8).Count
```

### Writing Files

```powershell
$content = @"
INT. LOCATION - DAY

The room is dark.
"@
$content | Out-File -FilePath 'scene.fountain' -Encoding UTF8
```

### UTF-8 Encoding

Always specify UTF-8 encoding:

```powershell
Get-Content -Path 'file.txt' -Encoding UTF8
$content | Out-File -FilePath 'file.txt' -Encoding UTF8
```

---

## 4. Python Script Execution

```powershell
$env:PYTHONIOENCODING='utf-8'

python tools/page_count.py --episode S01E01
python tools/parenthetical_audit.py --episode S01E01
python tools/callback_check.py --episode S01E01
python tools/continuity_check.py --episode S01E01
python tools/convention_scan.py
python tools/episode_assemble.py --episode S01E01
python tools/season_assemble.py
python tools/word_count.py
python tools/episode_export.py --episode S01E01
```

---

## 5. Working with Large Files

```powershell
Get-Content -Path 'scripts/S01E01/S01E01.fountain' -ReadCount 1000 | ForEach-Object { $_ }
```

---

## 6. Best Practices

1. **Always use backslashes for Windows paths**
2. **Always specify UTF-8 encoding**
3. **Set PYTHONIOENCODING before running Python**: `$env:PYTHONIOENCODING='utf-8'`
4. **Use streaming for large files (1,000+ lines)**
5. **Test commands individually before combining**
6. **Use absolute paths when in doubt**

---

## 7. Troubleshooting

### Command Not Found

```powershell
Get-Command python
$env:PATH -split ';'
```

### Encoding Issues

```powershell
$env:PYTHONIOENCODING='utf-8'
```

*This guide is specific to Windows PowerShell. For Unix/Linux/Mac environments, use standard bash commands. For WSL setup, see [`skills/wsl_git_bash_setup.md`](wsl_git_bash_setup.md).*
