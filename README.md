# Secure Password Generator (CLI)

A fast, flexible, cryptographically secure password generator written in Python.  
Works in Linux bash, macOS Terminal, WSL, and Windows PowerShell.

The tool generates strong random passwords with customizable length, character sets, exclusions, URL-safe mode, CSV/JSON output, entropy estimation, and clipboard copying.

---

## Features

- Uses Python `secrets` for cryptographically secure randomness
- Customizable character set:
  - lowercase letters
  - uppercase letters
  - digits
  - symbols
- Custom symbol set via `--symbols-set`
- Exclude specific characters via `--exclude`
- Option to remove ambiguous characters (like `O/0`, `I/l/1`) with `--no-ambiguous`
- Option to require at least one character from each selected class with `--require-classes`
- Option to forbid repeated characters in the random portion with `--no-repeat`
- URL-safe mode (`A-Z a-z 0-9 - . _ ~`) via `--url-safe`
- Optional prefix and suffix (not counted in `--length`)
- Output formats: `plain`, `json`, `csv`
- Entropy estimation with `--show-entropy`
- Clipboard copy (`wl-copy`, `xclip`, or `pbcopy`) with `--copy`
- Supports generating one or many passwords

---

## Installation

Download or copy `spg.py` and make it executable:

```bash
chmod +x spg.py
