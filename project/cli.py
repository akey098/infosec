from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .core import build_pool, ensure_requirements, generate_passwords, bits_of_entropy
from .clipboard import copy_to_clipboard


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


def _print_csv(passwords: list[str]) -> None:
    # Simple CSV emitter that quotes when needed
    print("password")
    for p in passwords:
        if any(ch in p for ch in [",", '"', "\n"]):
            print('"' + p.replace('"', '""') + '"')
        else:
            print(p)


def main(argv: Any = None) -> None:
    args = parse_args() if argv is None else parse_args()

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
        _print_csv(pwds)
    else:
        if args.count == 1:
            print(pwds[0])
        else:
            print(args.separator.join(pwds))
