This repository contains a small, focused Secure Password Generator CLI written in
Python. The code has been split into small modules so the core logic is easy to
test, and the command-line glue is thin and readable.

Supported platforms: Linux (including WSL), macOS, and Windows PowerShell.

What it does
- Generates cryptographically secure random passwords using Python's
  `secrets` module.
- Flexible character selection (lower/upper/digits/symbols), with overrides
  and exclusions.
- Optional URL-safe mode and an option to drop ambiguous characters.
- Output formats: plain text, JSON, CSV. Optional entropy estimate printed to
  stderr.
- Copies the first password to clipboard if a supported tool is found
  (`wl-copy`, `xclip`, or `pbcopy`).

Project layout
- `project/core.py`: core generation logic and helpers.
- `project/cli.py`: argument parsing and program entry point.
- `project/clipboard.py`: clipboard helper.
- `project/spg.py`: thin entry script (keeps calling `spg.py` working).

Quick start
1. Make the script executable (optional):

```bash
chmod +x project/spg.py
```

2. Run with defaults (16-character password):

```bash
python project/spg.py
```

Examples
- Generate three 24-character passwords, require at least one from each class:

```bash
python project/spg.py -l 24 -n 3 --require-classes
```

- Generate a URL-safe 32-character password:

```bash
python project/spg.py -l 32 --url-safe
```

If you want me to also add a small `requirements.txt` or a test file for the
core functions, I can add that next.
