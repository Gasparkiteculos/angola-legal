#!/usr/bin/env python3
"""Validate Angola Legal JSON metadata records against the project schema."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", nargs="+", type=Path, help="JSON record file(s)")
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "schemas" / "legal-document.schema.json",
    )
    args = parser.parse_args()

    try:
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
    except (OSError, json.JSONDecodeError, Exception) as exc:
        print(f"Invalid schema {args.schema}: {exc}", file=sys.stderr)
        return 2

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    failed = False
    for path in args.records:
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"{path}: cannot read JSON: {exc}", file=sys.stderr)
            failed = True
            continue

        errors = sorted(validator.iter_errors(record), key=lambda error: list(map(str, error.path)))
        if errors:
            failed = True
            for error in errors:
                location = ".".join(map(str, error.absolute_path)) or "<root>"
                print(f"{path}:{location}: {error.message}", file=sys.stderr)
        else:
            print(f"{path}: valid")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
