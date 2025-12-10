I promise to meet the deadline and will take disciplinary action if this requirement is not met.
# Secure Password Generator (CLI)

This project provides a Python-based command-line tool for generating secure, fully customizable passwords.  
The generator uses Python's `secrets` module to ensure cryptographically strong randomness and supports a wide range of configuration options such as custom character sets, exclusions, URL-safe mode, entropy estimation, and multiple output formats.


## Features

- Cryptographically secure password generation using Python `secrets`
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
- Output formats: plain text, JSON, CSV
- Entropy estimation (`--show-entropy`)
- Ability to generate multiple passwords at once

## Basic Usage

### Default generation
```bash
python ./spg.py
```
Generates a 16-character password using all character classes.

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

Save 10 passwords as CSV:

```bash
python ./spg.py -n 10 --format csv > passwords.csv
```

### JSON output
```bash
python ./spg.py -n 3 --format json
```

Save 5 passwords as JSON:

```bash
python ./spg.py -n 5 --format json > passwords.json
```

## Command-Line Options

### Length and count
```
-l, --length INT       Length of the random portion (default: 16)
-n, --count INT        Number of passwords to generate (default: 1)
```

### Character selection
```
--lower                Include lowercase letters
--upper                Include uppercase letters
--digits               Include digits
--symbols              Include symbols
--symbols-set TEXT     Override symbol set (e.g. "!@#$%^&*")
--exclude TEXT         Exclude specific characters
--no-ambiguous         Remove visually similar characters (O/0, I/l/1, etc.)
--no-repeat            Do not repeat characters in the random portion
--require-classes      Require at least one of each selected class
--url-safe             Use URL-safe unreserved set (A-Z a-z 0-9 - . _ ~)
```

### Output control
```
--prefix TEXT          Add prefix (not counted in --length)
--suffix TEXT          Add suffix (not counted in --length)
--format {plain,json,csv}
                       Output format (default: plain)
--separator TEXT       Separator for multiple passwords in plain mode
--show-entropy         Print entropy estimate to stderr
--copy                 Copy the first generated password to clipboard
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

Example output (stderr):

```
~118.6 bits of entropy per password (random portion only).
```

## Project Structure

```
spg.py        # main CLI script
README.md     # documentation
```

## Security Notes

- Uses Python’s `secrets` module (cryptographically secure)
- Does not store generated passwords
- Output is printed to stdout; avoid logging or exposing it accidentally
- Clipboard copying may be unsafe on shared systems

## License 

MIT License.
