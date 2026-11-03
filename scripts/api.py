#!/usr/bin/env python3
"""Read-only JSON API route logic for Angola Legal metadata."""
from __future__ import annotations

import json
from pathlib import Path
from datetime import date
from urllib.parse import parse_qs, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "records" / "angola"
WEB = ROOT / "web"
API_PREFIX = "/api/v1"


def load_records():
    return [json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(RECORDS.glob("*.json"))]


def load_coverage():
    return json.loads((ROOT / "coverage" / "catalogue-coverage.json").read_text(encoding="utf-8"))


def load_sources():
    registry = json.loads((ROOT / "sources" / "source-registry.json").read_text(encoding="utf-8"))
    fields = ("id", "source_name", "institution", "source_url", "source_type",
              "jurisdiction_coverage", "verification_status")
    return {"sources": [{key: source.get(key) for key in fields} for source in registry["sources"]]}


def _text(value):
    if isinstance(value, dict):
        return " ".join(_text(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(_text(item) for item in value)
    return str(value or "")


def search_documents(records, params):
    query = " ".join(params.get("q", [""])).casefold().split()
    filters = {
        "document_nature": "nature",
        "issuing_authority": "institution",
        "legal_force": "legal_force",
        "temporal_status": "temporal_status",
        "verification_status": "verification_status",
    }
    matched = []
    for record in records:
        haystack = _text(record).casefold()
        if query and not all(term in haystack for term in query):
            continue
        if any(params.get(param, [None])[0] != record.get(field)
               for field, param in filters.items() if params.get(param)):
            continue
        subject = params.get("subject", [None])[0]
        if subject and subject.casefold() not in " ".join(record.get("subject_matter", [])).casefold():
            continue
        date_value = record.get("date_published") or record.get("date_issued")
        start = params.get("date_from", [None])[0]
        end = params.get("date_to", [None])[0]
        if start and (not date_value or date_value < start):
            continue
        if end and (not date_value or date_value > end):
            continue
        matched.append({key: record.get(key) for key in (
            "record_id", "title", "official_identifier", "document_nature",
            "issuing_authority", "date_published", "legal_force",
            "temporal_status", "verification_status", "subject_matter", "source_url"
        )})
    matched.sort(key=lambda item: (item.get("date_published") or "", item["record_id"]), reverse=True)
    try:
        limit = int(params.get("limit", ["20"])[0])
        offset = int(params.get("offset", ["0"])[0])
    except (TypeError, ValueError):
        raise ValueError("limit and offset must be integers")
    if limit < 1 or limit > 100 or offset < 0:
        raise ValueError("limit must be 1-100 and offset must be non-negative")
    for param in ("date_from", "date_to"):
        value = params.get(param, [None])[0]
        if value:
            try:
                date.fromisoformat(value)
            except ValueError as exc:
                raise ValueError(f"{param} must use YYYY-MM-DD") from exc
    return {"total": len(matched), "limit": limit, "offset": offset,
            "results": matched[offset:offset + limit]}


def document_facets(records):
    facets = {}
    for field in ("document_nature", "issuing_authority", "legal_force",
                  "temporal_status", "verification_status"):
        facets[field] = sorted({record[field] for record in records if record.get(field)})
    facets["subject_matter"] = sorted({subject for record in records
                                       for subject in record.get("subject_matter", [])})
    return {"facets": facets}


def graph_neighborhood(graph, record_id=None, depth=1):
    if record_id is None:
        return graph
    node_map = {node["id"]: node for node in graph["nodes"]}
    if record_id not in node_map or not node_map[record_id].get("resolved"):
        raise KeyError(record_id)
    reached = {record_id}
    frontier = {record_id}
    for _ in range(depth):
        next_frontier = set()
        for edge in graph["edges"]:
            if edge["source"] in frontier:
                next_frontier.add(edge["target"])
            if edge["target"] in frontier:
                next_frontier.add(edge["source"])
        next_frontier -= reached
        reached.update(next_frontier)
        frontier = next_frontier
    edges = [edge for edge in graph["edges"]
             if edge["source"] in reached and edge["target"] in reached]
    return {**graph, "nodes": [node for node in graph["nodes"] if node["id"] in reached],
            "edges": edges, "focus_record_id": record_id, "depth": depth}


def dispatch(path, records=None, coverage=None):
    """Pure route dispatcher returning status, MIME type and a response body."""
    records = load_records() if records is None else records
    coverage = load_coverage() if coverage is None else coverage
    parts = urlsplit(path)
    route = parts.path
    params = parse_qs(parts.query)
    if route == API_PREFIX + "/health":
        return 200, "application/json; charset=utf-8", {"status": "ok", "api_version": "1"}
    if route == API_PREFIX + "/search":
        try:
            return 200, "application/json; charset=utf-8", search_documents(records, params)
        except ValueError as exc:
            return 400, "application/json; charset=utf-8", {"error": str(exc)}
    if route == API_PREFIX + "/sources":
        return 200, "application/json; charset=utf-8", load_sources()
    if route == API_PREFIX + "/facets":
        return 200, "application/json; charset=utf-8", document_facets(records)
    if route == API_PREFIX + "/coverage":
        from catalog import catalogue_coverage
        return 200, "application/json; charset=utf-8", catalogue_coverage(coverage, records)
    if route == API_PREFIX + "/graph":
        try:
            depth = int(params.get("depth", ["1"])[0])
        except ValueError:
            return 400, "application/json; charset=utf-8", {"error": "depth must be an integer from 0 to 3"}
        if depth < 0 or depth > 3:
            return 400, "application/json; charset=utf-8", {"error": "depth must be an integer from 0 to 3"}
        record_id = params.get("record_id", [None])[0]
        from catalog import build_relationship_graph
        graph = build_relationship_graph(records)
        try:
            return 200, "application/json; charset=utf-8", graph_neighborhood(graph, record_id, depth)
        except KeyError:
            return 404, "application/json; charset=utf-8", {"error": "record_id not found"}
    if route.startswith(API_PREFIX + "/documents/"):
        record_id = unquote(route[len(API_PREFIX + "/documents/"):])
        record = next((item for item in records if item["record_id"] == record_id), None)
        if record is None:
            return 404, "application/json; charset=utf-8", {"error": "document not found"}
        return 200, "application/json; charset=utf-8", record
    return 404, "application/json; charset=utf-8", {"error": "route not found"}


def main():
    from production import main as serve
    serve()


if __name__ == "__main__":
    main()
