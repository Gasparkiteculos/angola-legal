#!/usr/bin/env python3
"""Validate source-registry.json against its JSON Schema."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "source-registry.schema.json"
DEFAULT_REGISTRY = ROOT / "sources" / "source-registry.json"

def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_REGISTRY
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    registry = json.loads(path.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(registry),
                    key=lambda error: list(error.absolute_path))
    if errors:
        for error in errors:
            location = ".".join(map(str, error.absolute_path)) or "<root>"
            print(f"{path}:{location}: {error.message}", file=sys.stderr)
        return 1
    ids = [source["id"] for source in registry["sources"]]
    if len(ids) != len(set(ids)):
        print(f"{path}: duplicate source id", file=sys.stderr)
        return 1
    print(f"Valid source registry: {len(ids)} entries")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
