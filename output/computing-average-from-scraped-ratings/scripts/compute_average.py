#!/usr/bin/env python3
"""Compute an average from a list of numeric values.

Usage:
  python compute_average.py --values "9.7,9.6,9.5" --decimals 2 --expected-count 3

Notes:
- Designed for deterministic arithmetic and basic validation.
- Exits non-zero on validation failures.
"""

from __future__ import annotations

import argparse
import sys


def parse_values(s: str) -> list[float]:
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if not parts:
        raise ValueError("No values provided")
    vals: list[float] = []
    for p in parts:
        try:
            vals.append(float(p))
        except ValueError as e:
            raise ValueError(f"Non-numeric value: {p!r}") from e
    return vals


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--values", required=True, help="Comma-separated numeric values")
    ap.add_argument("--decimals", type=int, default=2)
    ap.add_argument("--expected-count", type=int, default=None)
    ap.add_argument("--print-sum", action="store_true")
    args = ap.parse_args(argv)

    try:
        values = parse_values(args.values)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if args.expected_count is not None and len(values) != args.expected_count:
        print(
            f"ERROR: expected {args.expected_count} values but got {len(values)}",
            file=sys.stderr,
        )
        return 2

    total = sum(values)
    mean = total / len(values)
    rounded = round(mean, args.decimals)

    if args.print_sum:
        print(f"count={len(values)} sum={total}")
    # Print with fixed decimals for presentation
    print(f"{rounded:.{args.decimals}f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
