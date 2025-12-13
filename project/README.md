# Secure Password Generator

A small Python CLI for generating strong passwords on your own machine (no internet needed).
It uses Python’s secrets for secure randomness, and you can tweak length, character sets, exclusions, and output format with flags.

> I promise to meet all deadlines and will fulfill all requirements.

## Why this exists

- Quick password generation without relying on websites or external services
- Works offline and can export results (JSON/CSV) for safe local storage
- Optional constraints like “no ambiguous characters” or “no repeats”

## Features

- Password generation using Python `secrets`
- Adjustable password length
- Customizable character sets:
  - lowercase letters
  - uppercase letters
  - digits
  - symbols
- Custom symbol set (`--symbols-set`)
- Exclude specific characters (`--exclude`)
- Remove ambiguous characters (`--no-ambiguous`)
- Require at least one character from each selected class (`--require-classes`)
- Optional no-repeat mode (`--no-repeat`)
- URL-safe mode (`--url-safe`)
- Prefix and suffix support (not counted toward length)
- Export in json and csv
- Entropy estimation (`--show-entropy`)
- Ability to generate multiple passwords at once

## Basic Usage

### Default generation
```bash
python ./spg.py
```
Generates a 16-char password with any characters possible.

### Change password length
```bash
python ./spg.py -l 24
```

### Generate multiple passwords
```bash
python ./spg.py -n 5 -l 20
```

### Use only uppercase and digits
```bash
python ./spg.py --upper --digits -l 18
```

### Remove ambiguous characters
```bash
python ./spg.py -l 24 --no-ambiguous
```

### Enforce at least one character from each selected class
```bash
python ./spg.py -l 24 --require-classes
```

### URL-safe tokens
```bash
python ./spg.py --url-safe -l 32
```

### CSV output
```bash
python ./spg.py -n 5 --format csv
```

Save 10 passwords as csv:

```bash
python ./spg.py -n 10 --format csv > passwords.csv
```

### JSON output
```bash
python ./spg.py -n 3 --format json
```

Save 5 passwords as json:

```bash
python ./spg.py -n 5 --format json > passwords.json
```

## Command-Line Options

### Length and count
```
-l, --length *number*       Length of the random portion (default: 16)
-n, --count *number*        Number of passwords to generate (default: 1)
```

### Character selection
```
--lower                     Include lowercase letters
--upper                     Include uppercase letters
--digits                    Include digits
--symbols                   Include symbols
--symbols-set *your_text*   Set your symbol set (e.g. "!@#$%^&*")
--exclude *your_text*       Exclude specific characters
--no-ambiguous              Remove visually similar characters (O/0, I/l/1, etc.)
--no-repeat                 Do not repeat characters in the random portion
--require-classes           Require at least one of each selected class
--url-safe                  Use URL-safe unreserved set (A-Z a-z 0-9 - . _ ~)
```

### Output control
```
--prefix *your_text*          Add prefix (not counted in --length)
--suffix *your_text*          Add suffix (not counted in --length)
--format {json,csv}
                              Output format (default: plain)
--separator *your_text*       Separator for multiple passwords in plain mode
--show-entropy                Print entropy estimate to stderr
```

### Utility
```
--version              Show version and exit
-h, --help             Show help message and exit
```

## Entropy Example

```bash
python ./spg.py -l 20 --show-entropy
```

Example output:

```
~118.6 bits of entropy per password (random portion only).
```
