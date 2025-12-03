#!/usr/bin/env python3
"""
Secure Password Generator (spg)

- Cryptographically secure (secrets)
- Linux-friendly CLI, zero deps
- Fine control over length, classes, symbols set, exclusions
- Optional: avoid ambiguous look‑alikes, forbid repeats, require all classes
- multiple outputs: plain / json / csv
- optional clipboard copy via wl-copy / xclip / pbcopy
- prints entropy estimate on request (stderr)

Examples:
  ./spg.py                 # 16-char strong default
  ./spg.py -l 24 -n 5 --require-classes --no-ambiguous
  ./spg.py -l 18 --upper --digits --exclude QO0 --no-ambiguous
  ./spg.py -l 32 --url-safe
  ./spg.py -n 3 --format json
  ./spg.py --copy --show-entropy
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import string
import subprocess
import sys
from secrets import choice, randbelow
from typing import List, Sequence

AMBIGUOUS_DEFAULT = set("O0oIl1|`'\"{}[]()/\\;:,.<>")
URL_SAFE_UNRESERVED = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"


def secure_shuffle(lst: List[str]) -> None:
    # Fisher–Yates with secrets.randbelow
    for i in range(len(lst) - 1, 0, -1):
        j = randbelow(i + 1)
        lst[i], lst[j] = lst[j], lst[i]


def build_pool(args: argparse.Namespace) -> tuple[str, List[str]]:
    # Determine which classes are explicitly requested
    includes_specified = any([args.lower, args.upper, args.digits, args.symbols])

    classes = {
        "lower": string.ascii_lowercase,
        "upper": string.ascii_uppercase,
        "digits": string.digits,
        "symbols": string.punctuation if args.symbols_set is None else args.symbols_set,
    }

    if args.url_safe:
        # Override to URL-safe unreserved characters only
        selected_classes = {"lower": True, "upper": True, "digits": True, "symbols": False}
        pool_parts = [URL_SAFE_UNRESERVED]
        class_names = ["url_safe"]
    else:
        if includes_specified:
            selected_classes = {
                "lower": bool(args.lower),
                "upper": bool(args.upper),
                "digits": bool(args.digits),
                "symbols": bool(args.symbols),
            }
        else:
            selected_classes = {"lower": True, "upper": True, "digits": True, "symbols": True}

        pool_parts = [chars for name, chars in classes.items() if selected_classes[name]]
        class_names = [name for name, ok in selected_classes.items() if ok]

    if not pool_parts:
        sys.exit("Error: no character classes selected. Use --lower/--upper/--digits/--symbols or --url-safe.")

    # Merge and apply filters
    pool = set("".join(pool_parts))

    if args.no_ambiguous and not args.url_safe:
        pool -= AMBIGUOUS_DEFAULT

    if args.exclude:
        pool -= set(args.exclude)

    # Never allow whitespace
    pool -= set("\r\n\t ")

    if not pool:
        sys.exit("Error: character pool is empty after filters. Relax exclusions or enable more classes.")

    return "".join(sorted(pool)), class_names


def build_pool_map(pool: str) -> dict[str, str]:
    return {
        "lower": "".join(sorted(set(pool) & set(string.ascii_lowercase))),
        "upper": "".join(sorted(set(pool) & set(string.ascii_uppercase))),
        "digits": "".join(sorted(set(pool) & set(string.digits))),
        "symbols": "".join(sorted(set(pool) & set(string.punctuation))),
    }


def ensure_requirements(
    length: int,
    class_names: Sequence[str],
    require_classes: bool,
    no_repeat: bool,
    pool: str,
) -> None:
    if length < 1:
        sys.exit("Error: --length must be >= 1.")

    if no_repeat and length > len(pool):
        sys.exit(
            f"Error: --no-repeat requested but length ({length}) exceeds pool size ({len(pool)})."
        )

    if require_classes and ("url_safe" not in class_names):
        pool_map = build_pool_map(pool)
        # Ensure every selected class has at least one available char
        missing = [n for n in class_names if not pool_map.get(n)]
        if missing:
            sys.exit(
                "Error: --require-classes is impossible because these classes are empty after filters: "
                + ", ".join(missing)
            )
        needed = len(class_names)
        if length < needed:
            sys.exit(
                f"Error: --length ({length}) must be >= number of required classes ({needed})."
            )


def pick_from_each_class(class_names: Sequence[str], pool_map: dict[str, str]) -> List[str]:
    picks = []
    for name in class_names:
        if name == "url_safe":
            continue
        s = pool_map[name]
        picks.append(choice(s))
    return picks


def generate_passwords(pool: str, class_names: Sequence[str], args: argparse.Namespace) -> List[str]:
    pool_map = build_pool_map(pool)

    passwords: List[str] = []
    for _ in range(args.count):
        chars: List[str] = []

        if args.require_classes and not args.url_safe:
            chars.extend(pick_from_each_class(class_names, pool_map))

        remaining = args.length - len(chars)
        if remaining < 0:
            remaining = 0

        if args.no_repeat:
            used = set(chars)
            available = [c for c in pool if c not in used]
            # secure shuffle then slice
            av_list = list(available)
            secure_shuffle(av_list)
            if len(av_list) < remaining:
                sys.exit(
                    "Error: not enough unique characters to satisfy --no-repeat with current pool."
                )
            chars.extend(av_list[:remaining])
        else:
            for _i in range(remaining):
                chars.append(choice(pool))

        # Secure shuffle of final chars
        secure_shuffle(chars)
        core = "".join(chars)

        # Prefix/Suffix do not count toward --length
        pwd = f"{args.prefix}{core}{args.suffix}"
        passwords.append(pwd)

    return passwords


def bits_of_entropy(pool_size: int, length: int) -> float:
    if pool_size <= 1 or length <= 0:
        return 0.0
    return length * math.log2(pool_size)


def copy_to_clipboard(text: str) -> None:
    if shutil.which("wl-copy"):
        subprocess.run(["wl-copy"], input=text.encode(), check=False)
    elif shutil.which("xclip"):
        subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=False)
    elif shutil.which("pbcopy"):
        subprocess.run(["pbcopy"], input=text.encode(), check=False)
    else:
        print(
            "Note: No clipboard utility found (expected wl-copy or xclip). Skipping --copy.",
            file=sys.stderr,
        )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="spg",
        description="Secure Password Generator (cryptographically secure, highly customizable).",
    )
    p.add_argument("-l", "--length", type=int, default=16, help="Length of the RANDOM portion (excludes prefix/suffix). Default: 16")
    p.add_argument("-n", "--count", type=int, default=1, help="How many passwords to generate. Default: 1")

    # Character class selection
    p.add_argument("--lower", action="store_true", help="Include lowercase letters.")
    p.add_argument("--upper", action="store_true", help="Include uppercase letters.")
    p.add_argument("--digits", action="store_true", help="Include digits.")
    p.add_argument("--symbols", action="store_true", help="Include symbols.")
    p.add_argument("--symbols-set", type=str, default=None, help='Override symbols set (e.g. "!@#$%^&*"). Default is string.punctuation.')
    p.add_argument("--exclude", type=str, default="", help="Characters to exclude from the pool.")
    p.add_argument("--no-ambiguous", action="store_true", help="Remove ambiguous look-alikes like O/0/I/l/1 etc.")
    p.add_argument("--no-repeat", action="store_true", help="Disallow repeated characters in the RANDOM portion.")
    p.add_argument("--require-classes", action="store_true", default=False, help="Require at least one from each selected class (except --url-safe).")
    p.add_argument("--url-safe", action="store_true", help="Use URL-safe unreserved characters only (A-Z a-z 0-9 - . _ ~). Ignores other class flags.")

    # Decorations and output
    p.add_argument("--prefix", type=str, default="", help="Prefix to prepend (not counted in --length).")
    p.add_argument("--suffix", type=str, default="", help="Suffix to append (not counted in --length).")
    p.add_argument("--format", choices=["plain", "json", "csv"], default="plain", help="Output format. Default: plain")
    p.add_argument("--separator", type=str, default="\n", help="Separator for plain output when --count>1. Default: newline")
    p.add_argument("--show-entropy", action="store_true", help="Print estimated entropy (bits) to stderr.")
    p.add_argument("--copy", action="store_true", help="Copy the first generated password to clipboard (wl-copy/xclip).")
    p.add_argument("--version", action="version", version="spg 1.1.0")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    pool, class_names = build_pool(args)
    ensure_requirements(args.length, class_names, args.require_classes, args.no_repeat, pool)

    pwds = generate_passwords(pool, class_names, args)

    if args.show_entropy:
        bits = bits_of_entropy(len(pool), args.length)
        print(f"~{bits:.1f} bits of entropy per password (random portion only).", file=sys.stderr)

    if args.copy and pwds:
        copy_to_clipboard(pwds[0])

    if args.format == "json":
        print(json.dumps(pwds, ensure_ascii=False))
    elif args.format == "csv":
        print("password")
        for p in pwds:
            if any(ch in p for ch in [",", '"', "\n"]):
                print('"' + p.replace('"', '""') + '"')
            else:
                print(p)
    else:
        if args.count == 1:
            print(pwds[0])
        else:
            print(args.separator.join(pwds))


if __name__ == "__main__":
    main()
