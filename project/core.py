from __future__ import annotations

import math
import string
import sys
from secrets import choice, randbelow
from typing import List, Sequence

AMBIGUOUS_DEFAULT = set("O0oIl1|`'\"{}[]()/\\;:,.<>")
URL_SAFE_UNRESERVED = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"


def secure_shuffle(lst: List[str]) -> None:
    # Fisher–Yates shuffle using cryptographic RNG
    for i in range(len(lst) - 1, 0, -1):
        j = randbelow(i + 1)
        lst[i], lst[j] = lst[j], lst[i]


def build_pool(args) -> tuple[str, List[str]]:
    # Build the set of allowed characters and list of active class names
    includes_specified = any([args.lower, args.upper, args.digits, args.symbols])

    classes = {
        "lower": string.ascii_lowercase,
        "upper": string.ascii_uppercase,
        "digits": string.digits,
        "symbols": string.punctuation if args.symbols_set is None else args.symbols_set,
    }

    if args.url_safe:
        # URL-safe uses a fixed pool and is not considered a normal class
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
            # default: include all classes
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

    # Never allow whitespace characters
    pool -= set("\r\n\t ")

    if not pool:
        sys.exit("Error: character pool is empty after filters. Relax exclusions or enable more classes.")

    return "".join(sorted(pool)), class_names


def build_pool_map(pool: str) -> dict[str, str]:
    # For each named class, return the characters from the pool belonging to it
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
    # Validate constraints that depend on chosen pool and flags
    if length < 1:
        sys.exit("Error: --length must be >= 1.")

    if no_repeat and length > len(pool):
        sys.exit(
            f"Error: --no-repeat requested but length ({length}) exceeds pool size ({len(pool)})."
        )

    if require_classes and ("url_safe" not in class_names):
        pool_map = build_pool_map(pool)
        # Check each requested class still has characters after filtering
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
    # Pick one random character from each requested class (skip url_safe)
    picks = []
    for name in class_names:
        if name == "url_safe":
            continue
        s = pool_map[name]
        picks.append(choice(s))
    return picks


def generate_passwords(pool: str, class_names: Sequence[str], args) -> List[str]:
    # Produce the list of passwords according to args; no IO here
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

        # Shuffle the selected characters and build the final password
        secure_shuffle(chars)
        core = "".join(chars)
        pwd = f"{args.prefix}{core}{args.suffix}"
        passwords.append(pwd)

    return passwords


def bits_of_entropy(pool_size: int, length: int) -> float:
    # Estimate entropy in bits for the random portion
    if pool_size <= 1 or length <= 0:
        return 0.0
    return length * math.log2(pool_size)
