#!/usr/bin/env python3
"""Search, version, graph and integrity tools for Angola Legal metadata."""
import argparse
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "records" / "angola"
RELATIONS = {
    "amends", "amended_by", "repeals", "repealed_by", "regulates", "implements",
    "implemented_by", "complements", "complemented_by", "consolidates",
    "consolidated_by", "revises", "revised_by", "republication_under",
    "version_of", "related_to",
}
INVERSE = {
    "amended_by": "amends",
    "repealed_by": "repeals",
    "implemented_by": "implements",
    "complemented_by": "complements",
    "consolidated_by": "consolidates",
    "revised_by": "revises",
}
INSTRUMENT_PATTERN = re.compile(
    r"\b(lei|decreto legislativo|decreto presidencial|decreto|"
    r"resolu[cç][aã]o|rectifica[cç][aã]o|despacho)\s+n[.ºo°]*\s*"
    r"\d+\s*/\s*\d{2,4}\b",
    re.IGNORECASE,
)

def rows():
    return [(path, json.loads(path.read_text(encoding="utf-8")))
            for path in sorted(RECORDS.glob("*.json"))]

def flatten(value):
    if isinstance(value, dict):
        return " ".join(flatten(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(flatten(item) for item in value)
    return str(value)

def normalize(value):
    value = unicodedata.normalize("NFKD", str(value).casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return " ".join(re.findall(r"[a-z0-9]+", value))

def _index_records(records):
    aliases = {}
    for record in records:
        rid = record["record_id"]
        values = (rid, record.get("title"), record.get("title_pt"),
                  record.get("title_en"), record.get("official_identifier"))
        for value in values:
            if not value:
                continue
            aliases.setdefault(normalize(value), set()).add(rid)
            for match in INSTRUMENT_PATTERN.finditer(value):
                aliases.setdefault(normalize(match.group(0)), set()).add(rid)
    return aliases

def _resolve(reference, aliases):
    key = normalize(reference)
    exact = aliases.get(key, set())
    if len(exact) == 1:
        return next(iter(exact)), "resolved"
    candidates = set()
    if len(key) >= 8:
        for alias, ids in aliases.items():
            if len(alias) >= 8 and (key in alias or alias in key):
                candidates.update(ids)
    if len(candidates) == 1:
        return next(iter(candidates)), "resolved"
    return None, "ambiguous" if len(candidates) > 1 or len(exact) > 1 else "unresolved"

def _assertions(record):
    assertions = list(record.get("related_identifiers", []))
    parent = record.get("versioning", {}).get("version_of")
    if parent:
        assertions.append({"scheme": "record_id", "value": parent, "relation": "version_of"})
    return assertions

def build_relationship_graph(records):
    """Build a graph from record dictionaries, preserving assertion provenance."""
    aliases = _index_records(records)
    nodes = {}
    for record in records:
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

    edges = []
    external_ids = {}
    for record in records:
        source_id = record["record_id"]
        for item in _assertions(record):
            reference = item.get("value", "")
            relation = item.get("relation") or "related_to"
            target_id, resolution = _resolve(reference, aliases)
            if target_id is None:
                key = normalize(reference) or str(reference)
                external_key = (resolution, key)
                target_id = external_ids.setdefault(
                    external_key, f"{resolution}:{key.replace(' ', '-')}"
                )
                nodes.setdefault(target_id, {
                    "id": target_id,
                    "title": reference,
                    "official_identifier": reference,
                    "verification_status": f"{resolution}_reference",
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

    merged = {}
    for edge in edges:
        key = (edge["source"], edge["target"], edge["relation"])
        if key not in merged:
            merged[key] = {
                "source": edge["source"], "target": edge["target"],
                "relation": edge["relation"], "evidence": [],
            }
        merged[key]["evidence"].append({
            "record_id": edge["asserted_by_record"],
            "url": edge["evidence_url"],
            "verification_status": edge["assertion_verification"],
        })
    return {
        "schema_version": "1.1",
        "scope": "records/angola metadata; unresolved and ambiguous references are explicit",
        "nodes": sorted(nodes.values(), key=lambda node: node["id"]),
        "edges": [merged[key] for key in sorted(merged)],
    }

def relationship_graph():
    return build_relationship_graph([record for _, record in rows()])

def check_graph_integrity(records):
    """Return errors/warnings for invalid, self, duplicate, or weakly evidenced edges."""
    aliases = _index_records(records)
    ids = {record.get("record_id") for record in records}
    errors, warnings = [], []
    seen = set()
    for record in records:
        rid = record.get("record_id")
        for item in _assertions(record):
            reference = str(item.get("value", "")).strip()
            relation = item.get("relation") or "related_to"
            if relation not in RELATIONS:
                errors.append({"code": "invalid_relation", "record_id": rid,
                               "relation": relation, "reference": reference})
            if not reference:
                errors.append({"code": "empty_reference", "record_id": rid})
                continue
            duplicate_key = (rid, relation, normalize(reference))
            if duplicate_key in seen:
                errors.append({"code": "duplicate_assertion", "record_id": rid,
                               "relation": relation, "reference": reference})
            seen.add(duplicate_key)
            target, resolution = _resolve(reference, aliases)
            if resolution == "ambiguous":
                warnings.append({"code": "ambiguous_reference", "record_id": rid,
                                 "reference": reference})
            elif resolution == "unresolved":
                warnings.append({"code": "unresolved_reference", "record_id": rid,
                                 "reference": reference})
            elif target == rid:
                errors.append({"code": "self_reference", "record_id": rid,
                               "relation": relation, "reference": reference})

    graph = build_relationship_graph(records)
    node_ids = {node["id"] for node in graph["nodes"]}
    for edge in graph["edges"]:
        if edge["source"] not in node_ids or edge["target"] not in node_ids:
            errors.append({"code": "missing_endpoint", "edge": edge})
        evidence = edge.get("evidence", [])
        if not evidence:
            errors.append({"code": "missing_provenance", "edge": edge})
        for item in evidence:
            if item.get("record_id") not in ids or not item.get("url", "").startswith("https://"):
                errors.append({"code": "invalid_provenance", "evidence": item})
        provenance_keys = [(item.get("record_id"), item.get("url")) for item in evidence]
        if len(provenance_keys) != len(set(provenance_keys)):
            errors.append({"code": "duplicate_provenance", "edge": edge})
    return {
        "status": "invalid" if errors else "pass",
        "record_count": len(records),
        "node_count": len(graph["nodes"]),
        "edge_count": len(graph["edges"]),
        "unresolved_reference_count": sum(
            node["verification_status"] == "unresolved_reference" for node in graph["nodes"]
        ),
        "ambiguous_reference_count": sum(
            node["verification_status"] == "ambiguous_reference" for node in graph["nodes"]
        ),
        "errors": errors,
        "warnings": warnings,
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
        lines.append(f'  "{dot_escape(edge["source"])}" -> "{dot_escape(edge["target"])}" [label="{dot_escape(edge["relation"])}"];')
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
    commands.add_parser("check-graph")
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
                "record_id": record["record_id"], "version": version,
                "parent_present": version.get("version_of") in ids if version.get("version_of") else None,
                "related_identifiers": record.get("related_identifiers", []),
            }, ensure_ascii=False))
        return 0

    if args.command == "graph":
        result = relationship_graph()
        print(graph_dot(result) if args.format == "dot" else json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "check-graph":
        result = check_graph_integrity([record for _, record in rows()])
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result["status"] == "invalid" else 0

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
