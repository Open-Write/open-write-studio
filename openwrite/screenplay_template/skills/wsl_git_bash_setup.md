# WSL/Git Bash Setup Guide — Screenplay Production

*Using Windows Subsystem for Linux or Git Bash for screenplay production work.*

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
   cd /mnt/c/path/to/your/screenplay/project
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
| C:\path\to\project\script | /mnt/c/path/to/project/script |
| C:\path\to\project\bible | /mnt/c/path/to/project/bible |
| C:\path\to\project\state | /mnt/c/path/to/project/state |

### Create Shortcuts (Optional)

Add to ~/.bashrc:
```bash
alias proj='cd /mnt/c/path/to/your/project'
alias proj-tools='cd /mnt/c/path/to/your/project/tools'
alias proj-script='cd /mnt/c/path/to/your/project/script'
```

Then reload:
```bash
source ~/.bashrc
```

---

## Python Script Execution in WSL

```bash
cd /mnt/c/path/to/your/project/tools
python3 fountain_to_pdf.py ../script/screenplay.fountain ../script/screenplay.pdf
python3 page_count.py
python3 parenthetical_audit.py
python3 callback_check.py
python3 assemble_screenplay.py
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

*This guide is specific to screenplay production. Adapt paths for your project location.*
