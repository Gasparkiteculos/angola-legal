#!/usr/bin/env python3
"""Read-only metadata search, version reporting and legal relationship graph."""
import argparse
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "records" / "angola"

def rows():
    return [(path, json.loads(path.read_text(encoding="utf-8"))) for path in sorted(RECORDS.glob("*.json"))]

def flatten(value):
    if isinstance(value, dict):
        return " ".join(flatten(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(flatten(item) for item in value)
    return str(value)

def normalize(value):
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return " ".join(re.findall(r"[a-z0-9]+", value))

# Relations that point from the object back to the subject are reversed
# during graph construction so that the edge describes the legal action.
INVERSE = {
    "amended_by": "amends",
    "repealed_by": "repeals",
    "implemented_by": "implements",
    "complemented_by": "complements",
    "consolidated_by": "consolidates",
    "revised_by": "revises",
}

def relationship_graph():
    records = rows()
    nodes = {}
    aliases = {}
    for _, record in records:
        rid = record["record_id"]
        nodes[rid] = {
            "id": rid,
            "title": record.get("title"),
            "official_identifier": record.get("official_identifier"),
            "verification_status": record.get("verification_status"),
            "temporal_status": record.get("temporal_status"),
            "source_url": record.get("source_url"),
            "resolved": True,
        }
        for value in (rid, record.get("title"), record.get("title_pt"),
                      record.get("title_en"), record.get("official_identifier")):
            if value:
                aliases.setdefault(normalize(value), set()).add(rid)

    def resolve(reference):
        key = normalize(reference)
        exact = aliases.get(key, set())
        if len(exact) == 1:
            return next(iter(exact))
        candidates = set()
        if len(key) >= 8:
            for alias, ids in aliases.items():
                if len(alias) >= 8 and (key in alias or alias in key):
                    candidates.update(ids)
        return next(iter(candidates)) if len(candidates) == 1 else None

    edges = []
    unresolved = {}
    for _, record in records:
        source_id = record["record_id"]
        assertions = list(record.get("related_identifiers", []))
        version = record.get("versioning", {})
        if version.get("version_of"):
            assertions.append({
                "scheme": "record_id",
                "value": version["version_of"],
                "relation": "version_of",
            })
        for item in assertions:
            reference = item.get("value", "")
            relation = item.get("relation", "related_to")
            target_id = resolve(reference)
            if target_id is None:
                key = normalize(reference) or reference
                target_id = unresolved.setdefault(key, "external:" + key.replace(" ", "-"))
                nodes.setdefault(target_id, {
                    "id": target_id,
                    "title": reference,
                    "official_identifier": reference,
                    "verification_status": "unresolved_reference",
                    "temporal_status": "unknown",
                    "source_url": None,
                    "resolved": False,
                })
            edge_source, edge_target = source_id, target_id
            canonical_relation = relation
            if relation in INVERSE:
                canonical_relation = INVERSE[relation]
                edge_source, edge_target = target_id, source_id
            edges.append({
                "source": edge_source,
                "target": edge_target,
                "relation": canonical_relation,
                "asserted_by_record": source_id,
                "evidence_url": record.get("source_url"),
                "assertion_verification": record.get("verification_status", "unknown"),
            })

    # Keep repeated reciprocal statements as one edge while preserving all evidence.
    merged = {}
    for edge in edges:
        key = (edge["source"], edge["target"], edge["relation"])
        if key not in merged:
            merged[key] = {**edge, "evidence": []}
        merged[key]["evidence"].append({
            "record_id": edge["asserted_by_record"],
            "url": edge["evidence_url"],
            "verification_status": edge["assertion_verification"],
        })
    return {
        "schema_version": "1.0",
        "scope": "records/angola JSON metadata; unresolved references are explicit",
        "nodes": sorted(nodes.values(), key=lambda node: node["id"]),
        "edges": [merged[key] for key in sorted(merged)],
    }

def dot_escape(value):
    return str(value or "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")

def graph_dot(graph):
    lines = ["digraph AngolaLegal {", '  graph [label="Angola Legal legal relationships", labelloc="t"];',
             "  rankdir=LR;", "  node [shape=box];"]
    for node in graph["nodes"]:
        style = "" if node["resolved"] else ', style="dashed", color="gray"'
        lines.append(f'  "{dot_escape(node["id"])}" [label="{dot_escape(node["title"])}"{style}];')
    for edge in graph["edges"]:
        label = edge["relation"]
        lines.append(f'  "{dot_escape(edge["source"])}" -> "{dot_escape(edge["target"])}" [label="{dot_escape(label)}"];')
    lines.append("}")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    search = commands.add_parser("search")
    search.add_argument("query")
    versions = commands.add_parser("versions")
    versions.add_argument("record_id", nargs="?")
    compare = commands.add_parser("diff")
    compare.add_argument("left")
    compare.add_argument("right")
    graph = commands.add_parser("graph")
    graph.add_argument("--format", choices=("json", "dot"), default="json")
    args = parser.parse_args()

    if args.command == "search":
        terms = args.query.casefold().split()
        matches = []
        for path, record in rows():
            if all(term in flatten(record).casefold() for term in terms):
                matches.append({
                    key: record.get(key) for key in
                    ("record_id", "title", "official_identifier", "verification_status",
                     "temporal_status", "source_url")
                } | {"file": path.relative_to(ROOT).as_posix()})
        print(json.dumps(matches, ensure_ascii=False, indent=2))
        return 0

    if args.command == "versions":
        records = rows()
        ids = {record["record_id"] for _, record in records}
        for _, record in records:
            if args.record_id and record["record_id"] != args.record_id:
                continue
            version = record.get("versioning", {})
            print(json.dumps({
                "record_id": record["record_id"],
                "version": version,
                "parent_present": version.get("version_of") in ids if version.get("version_of") else None,
                "related_identifiers": record.get("related_identifiers", []),
            }, ensure_ascii=False))
        return 0

    if args.command == "graph":
        result = relationship_graph()
        print(graph_dot(result) if args.format == "dot" else json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    left = json.loads(Path(args.left).read_text(encoding="utf-8"))
    right = json.loads(Path(args.right).read_text(encoding="utf-8"))
    changes = []
    def walk(old, new, key=""):
        if isinstance(old, dict) and isinstance(new, dict):
            for child in sorted(set(old) | set(new)):
                walk(old.get(child), new.get(child), f"{key}.{child}" if key else child)
        elif old != new:
            changes.append(key or "<root>")
    walk(left, right)
    print(json.dumps({
        "changed_fields": changes,
        "source_artifact_changed":
            left.get("versioning", {}).get("source_sha256") !=
            right.get("versioning", {}).get("source_sha256"),
    }, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
