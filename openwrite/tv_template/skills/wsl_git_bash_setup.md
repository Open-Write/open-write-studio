# WSL/Git Bash Setup Guide — TV Production

*Using Windows Subsystem for Linux or Git Bash for TV production work.*

---

## Quick Start

1. Install WSL (if not already installed)
   ```powershell
   wsl --install
   ```

2. Restart your computer and complete WSL setup

3. Access your project from WSL
   ```bash
   wsl
   cd /mnt/c/path/to/your/tv/project
   ```

4. Verify access
   ```bash
   ls -la
   pwd
   ```

---

## Windows Path to WSL Path Mapping

| Windows Path | WSL Path |
|--------------|----------|
| C:\ | /mnt/c/ |
| C:\path\to\project | /mnt/c/path/to/project |
| C:\path\to\project\tools | /mnt/c/path/to/project/tools |
| C:\path\to\project\scripts | /mnt/c/path/to/project/scripts |
| C:\path\to\project\bible | /mnt/c/path/to/project/bible |
| C:\path\to\project\state | /mnt/c/path/to/project/state |

### Create Shortcuts (Optional)

Add to ~/.bashrc:
```bash
alias proj='cd /mnt/c/path/to/your/project'
alias proj-tools='cd /mnt/c/path/to/your/project/tools'
alias proj-scripts='cd /mnt/c/path/to/your/project/scripts'
alias proj-bible='cd /mnt/c/path/to/your/project/bible'
```

Then reload:
```bash
source ~/.bashrc
```

---

## Python Script Execution in WSL

```bash
cd /mnt/c/path/to/your/project/tools
python3 episode_assemble.py --episode S01E01
python3 season_assemble.py
python3 page_count.py --episode S01E01
python3 parenthetical_audit.py --episode S01E01
python3 callback_check.py --episode S01E01
python3 continuity_check.py --episode S01E01
python3 word_count.py
python3 convention_scan.py
```

### Python Environment Setup

```bash
python3 --version  # Should be 3.8+
pip3 --version
pip3 install reportlab
```

---

## Troubleshooting

### Python not found
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### File encoding issues
```bash
export PYTHONIOENCODING=utf-8
echo 'export PYTHONIOENCODING=utf-8' >> ~/.bashrc
source ~/.bashrc
```

### Git permission issues
```bash
git config --global core.fileMode false
```

*This guide is specific to TV series production. Adapt paths for your project location.*
