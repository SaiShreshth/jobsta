# ENVIRONMENT SPECIFICATION (MANDATORY)

## HOST SYSTEM
- Operating System: Windows 10/11
- Shells available:
  - PowerShell (native)
  - WSL (Ubuntu) for bash scripts

## PYTHON ENVIRONMENT
- Python version: >= 3.10
- Virtual environment:
  - MUST use `venv` for the entire project
  - venv folder name: `.venv`
  - venv must be activated before running Python commands

### venv Commands
- Create:
  python -m venv .venv

- Activate (PowerShell):
  .\.venv\Scripts\Activate.ps1

- Activate (WSL / bash):
  source .venv/bin/activate

ALL Python commands MUST run inside the venv.

---

## SHELL SCRIPT EXECUTION
- Bash scripts (`.sh`) MUST be run via WSL
- Use:
  wsl bash scripts/<script_name>.sh

- The agent MUST NOT attempt to run `.sh` scripts directly in PowerShell.

---

## GIT
- Git is available on Windows
- Git commands can be run from PowerShell or WSL
- Auto-commit and rollback scripts MUST be executed via WSL

---

## PACKAGE MANAGEMENT
- Python packages: pip (inside venv only)
- Node.js is OPTIONAL (only if Tailwind build requires it)

---

## DATABASE
- External PostgreSQL (Neon)
- Connection via DATABASE_URL in `.env`
- SSL REQUIRED

---

## ENV FILES
- `.env` is NOT committed
- `.env.example` MUST be maintained and updated

---

## FAILURE HANDLING
If a script fails due to environment mismatch:
1. Retry once using WSL bash
2. If still failing, trigger rollback using `rollback.sh`

---

## NON-NEGOTIABLE RULE
If a command would break venv isolation or bypass WSL rules:
DO NOT RUN IT.
