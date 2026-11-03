#!/usr/bin/env python3
"""Edition 0.6 structural, provenance, packet, course, visual, and lineage audit."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
errors: list[str] = []


def read_jsonl(name: str):
    try:
        return [json.loads(line) for line in (DATA / name).read_text(encoding="utf-8").splitlines() if line.strip()]
    except Exception as exc:
        errors.append(f"bad JSONL {name}: {exc}")
        return []


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


sources = read_jsonl("sources.jsonl")
claims = read_jsonl("claims.jsonl")
relationships = read_jsonl("relationships.jsonl")
entities = read_jsonl("entities.jsonl")
notes = read_jsonl("research_notes.jsonl")
publications = read_jsonl("publications.jsonl")
documents = read_jsonl("documents.jsonl")
source_ids = {s.get("id") for s in sources}
claim_ids = {c.get("id") for c in claims}

expected = {"sources": 142, "claims": 76, "publications": 26, "entities": 18, "notes": 20, "lessons": 26, "svg": 28}
counts = {"sources": len(sources), "claims": len(claims), "publications": len(publications), "entities": len(entities), "notes": len(notes), "lessons": len(list((ROOT / "courses").glob("[0-9]*.md"))), "svg": len(list((ROOT / "assets").glob("*.svg")))}
for key, wanted in expected.items():
    if counts[key] != wanted:
        errors.append(f"{key}: expected {wanted}, got {counts[key]}")

for collection, rows in (("source", sources), ("claim", claims), ("entity", entities), ("note", notes), ("publication", publications)):
    ids = [row.get("id") for row in rows]
    if len(ids) != len(set(ids)):
        errors.append(f"duplicate {collection} IDs")
urls = [s.get("url", "").split("?")[0].rstrip("/") for s in sources]
if len(urls) != len(set(urls)):
    errors.append("duplicate normalized source URLs")
for source in sources:
    if not source.get("url", "").startswith("https://"):
        errors.append(f"non-HTTPS source: {source.get('id')}")
    if source.get("snapshot_status") not in {"catalog-card-only", "licensed-snapshot"}:
        errors.append(f"unknown snapshot state: {source.get('id')}")
for label, rows in (("claim", claims), ("entity", entities), ("note", notes)):
    for row in rows:
        for sid in row.get("source_ids", []):
            if sid not in source_ids:
                errors.append(f"dangling {label} source reference: {row.get('id')} -> {sid}")
for edge in relationships:
    if edge.get("from", "").startswith("C-") and edge["from"] not in claim_ids:
        errors.append(f"dangling relationship claim: {edge['from']}")
    if edge.get("to", "").startswith("SRC-") and edge["to"] not in source_ids:
        errors.append(f"dangling relationship source: {edge['to']}")

with (DATA / "sources.csv").open(encoding="utf-8", newline="") as f:
    csv_rows = list(csv.DictReader(f))
if {row["id"] for row in csv_rows} != source_ids or len(csv_rows) != len(sources):
    errors.append("sources.csv and sources.jsonl inventory differs")

for publication in publications:
    source = next((s for s in sources if s["id"] == publication.get("source_id")), None)
    if source is None:
        errors.append(f"publication source missing: {publication.get('id')}")
    elif publication.get("source") != source["url"]:
        errors.append(f"publication URL/source-card mismatch: {publication['id']}")
    if publication.get("local_pdf") is not None:
        errors.append(f"unexpected external PDF mirror: {publication['id']}")
    if not (ROOT / "documents" / "publications" / "reference-cards" / f"{publication['id']}.md").is_file():
        errors.append(f"missing publication card: {publication['id']}")
for document in documents:
    if document.get("source_id") and document["source_id"] not in source_ids:
        errors.append(f"dangling document source: {document['document_id']}")
    if document.get("local_pdf_present"):
        path = ROOT / document.get("local_pdf_path", "")
        if not path.is_file() or not path.read_bytes().startswith(b"%PDF-"):
            errors.append(f"invalid or absent local PDF: {document['document_id']}")
        elif digest(path) != document.get("sha256"):
            errors.append(f"local PDF digest mismatch: {document['document_id']}")

lineage = json.loads((DATA / "release_v06_lineage.json").read_text(encoding="utf-8"))
if lineage.get("baseline_archive", {}).get("sha256") != "B7FDA71A48C858CE41A8D44ACA9ACD999D354EFB026A0E191951EFC9198DBAEE":
    errors.append("v0.5 baseline archive digest changed")
inherited = lineage.get("inherited_files", [])
if len(inherited) != 208 or lineage.get("inherited_file_count") != 208:
    errors.append("v0.5 source inventory is not the full 208-file archive")
intentional = set(lineage.get("v06_expected_edits", []))
missing_baseline = []
unexpected_baseline_changes = []
for item in inherited:
    path = ROOT / item["path"]
    if not path.is_file():
        missing_baseline.append(item["path"])
    elif item["path"] not in intentional and digest(path) != item["sha256"]:
        unexpected_baseline_changes.append(item["path"])
if missing_baseline:
    errors.append("missing inherited v0.5 files: " + ", ".join(missing_baseline[:12]))
if unexpected_baseline_changes:
    errors.append("unexpected edits to inherited files: " + ", ".join(unexpected_baseline_changes[:12]))

for svg in (ROOT / "assets").glob("*.svg"):
    try:
        root = ET.parse(svg).getroot()
        title = root.find("{http://www.w3.org/2000/svg}title")
        desc = root.find("{http://www.w3.org/2000/svg}desc")
        if svg.name.endswith("_v06.svg") and (title is None or desc is None):
            errors.append(f"new SVG lacks accessible title/description: {svg.name}")
    except Exception as exc:
        errors.append(f"invalid SVG XML {svg.name}: {exc}")

graph = json.loads((DATA / "topic_graph.json").read_text(encoding="utf-8"))
topic_ids = {node["id"] for node in graph.get("nodes", [])}
for node in graph.get("nodes", []):
    for sid in node.get("sources", []):
        if sid not in source_ids:
            errors.append(f"topic graph source missing: {node['id']} -> {sid}")
    for lesson in node.get("lessons", []):
        if not (ROOT / "courses" / lesson).is_file():
            errors.append(f"topic graph lesson missing: {node['id']} -> {lesson}")
for edge in graph.get("edges", []):
    if edge.get("from") not in topic_ids or edge.get("to") not in topic_ids:
        errors.append("dangling topic graph edge")

aliases = json.loads((DATA / "query_aliases_v06.json").read_text(encoding="utf-8"))
for concept in aliases.get("concepts", []):
    for sid in concept.get("source_ids", []):
        if sid not in source_ids:
            errors.append(f"dangling alias source: {concept['id']} -> {sid}")
packet_path = DATA / "packets" / "examples" / "frequency-stability.v0.6.packet.json"
if packet_path.is_file():
    packet_obj = json.loads(packet_path.read_text(encoding="utf-8"))
    if packet_obj.get("input_sha256", {}).get("sources.jsonl") != digest(DATA / "sources.jsonl"):
        errors.append("sample packet source hash is stale")
    if packet_obj.get("input_sha256", {}).get("claims.jsonl") != digest(DATA / "claims.jsonl"):
        errors.append("sample packet claims hash is stale")
    unsigned = dict(packet_obj)
    checksum = unsigned.pop("packet_sha256", None)
    expected_sum = hashlib.sha256(json.dumps(unsigned, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
    if checksum != expected_sum:
        errors.append("sample packet checksum mismatch")
    if packet_obj.get("atlas_version") != "0.6":
        errors.append("sample packet version mismatch")
else:
    errors.append("missing frequency-stability example packet")

for old_file in ("packet_probe_v05.json", "noaa_f107_v05.json"):
    if not (DATA / "experiments" / old_file).is_file():
        errors.append(f"historical v0.5 evidence missing: {old_file}")
site = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
for marker in ("const CLAIM_COUNT=76;", "const SOURCES=", "const PUBS=", "const LESSONS=", "signal_atlas_logo_header.png", "OPEN RESEARCH V0.6"):
    if marker not in site:
        errors.append(f"offline site missing marker: {marker}")
if "assets/signal_atlas_logo_header.png" not in (ROOT / "README.md").read_text(encoding="utf-8"):
    errors.append("evergreen logo is not the README's lead graphic")
for md in ROOT.rglob("*.md"):
    for groups in re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)|!\[[^\]]*\]\(([^)]+)\)", md.read_text(encoding="utf-8")):
        target = next((part for part in groups if part), "")
        if not target or target.startswith(("https://", "http://", "mailto:", "#")):
            continue
        if not (md.parent / target.split("#")[0]).exists():
            errors.append(f"broken Markdown link: {md.relative_to(ROOT)} -> {target}")

index = DATA / "atlas_index.sqlite"
if index.is_file():
    with sqlite3.connect(index) as db:
        db_sources = db.execute("SELECT count(*) FROM records WHERE kind='source'").fetchone()[0]
        db_claims = db.execute("SELECT count(*) FROM records WHERE kind='claim'").fetchone()[0]
        if (db_sources, db_claims) != (len(sources), len(claims)):
            errors.append("derived SQLite index counts do not match canonical ledgers")
        for filename, sha256, count in db.execute("SELECT filename,sha256,item_count FROM index_manifest"):
            if digest(DATA / filename) != sha256:
                errors.append(f"derived SQLite index manifest stale for {filename}")
else:
    errors.append("missing derived SQLite index")

print("v0.6 audit:", "; ".join(f"{key}={value}" for key, value in counts.items()))
print(f"Inherited v0.5 archive inventory: {len(inherited)} paths; preserved hashes outside declared edit set")
if errors:
    for error in errors:
        print("FAIL:", error)
    sys.exit(1)
print("PASS: local joins, rights state, file lineage, graph, packet hashes, site, and links")
