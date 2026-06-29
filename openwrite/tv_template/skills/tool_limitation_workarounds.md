# Tool Limitation Workarounds

*Alternative approaches when Kilo tools fail or are unavailable.*

---

## When Tools Fail

Detection and Diagnosis

Symptoms of tool failure:
- Bash command hangs or times out
- Read tool returns file not found
- Write tool fails on new files
- Edit tool cannot find text
- Path errors on Windows

## Quick Reference

| Tool Failure | Quick Workaround |
|--------------|------------------|
| Write fails | Use New-Item or Set-Content |
| Edit fails | Open in VS Code manually |
| Read timeout | Use partial read methods |
| Bash fails | Try WSL or Git Bash |
| Large file | Split into chunks |
| JSON corrupted | Rebuild from template |
| Python error | Run directly in terminal |
| Path error | Check forward slashes |

## Environment Detection

Before using any commands, check your environment:

### PowerShell (Windows)
```powershell
$PSVersionTable.PSVersion
if ($env:OS -like '*Windows*') { 'Running on Windows PowerShell' }
```

### Bash (Unix/Linux/Mac)
```bash
echo $SHELL
uname
```

### Tool Availability
```powershell
python --version
git --version
node --version
```

## Platform-Specific Guidance

| Platform | Guide |
|----------|-------|
| Windows PowerShell | [`skills/windows_powershell_guide.md`](windows_powershell_guide.md) |
| Bash (Unix/Linux/Mac) | Standard bash commands |
| WSL (Windows Subsystem for Linux) | [`skills/wsl_git_bash_setup.md`](wsl_git_bash_setup.md) |
| Git Bash (Windows) | Bash commands within Git Bash environment |

## Large Files

For files over 1,000 lines, see [`skills/large_file_operations.md`](large_file_operations.md).

*This guide is a living document. Add new workarounds as discovered during production.*
