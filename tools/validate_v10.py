#!/usr/bin/env python3
"""Validate v1.0 provenance, dataset, search, packet, lineage, and navigation."""
from __future__ import annotations
import csv, hashlib, json, re, sys
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from build_v10 import pair_rows, canon
from release_files import iter_release_files

errors=[]
def check(ok,message):
    if not ok:errors.append(message)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def sha256(data):return hashlib.sha256(data).hexdigest()
def loadj(path):
    try:return json.loads((ROOT/path).read_text(encoding="utf-8"))
    except Exception as exc:errors.append(f"{path}: invalid JSON ({exc})");return None
def loadl(path):
    try:return [json.loads(x) for x in (ROOT/path).read_text(encoding="utf-8").splitlines() if x.strip()]
    except Exception as exc:errors.append(f"{path}: invalid JSONL ({exc})");return []

class EmbeddedJSON(HTMLParser):
    def __init__(self,target):super().__init__();self.target=target;self.active=False;self.parts=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=="script" and attrs.get("id")==self.target:self.active=True
    def handle_endtag(self,tag):
        if tag=="script" and self.active:self.active=False
    def handle_data(self,data):
        if self.active:self.parts.append(data)

sources=loadl("data/sources.jsonl");claims=loadl("data/claims.jsonl");notes=loadl("data/research_notes.jsonl")
source_ids={x.get("id") for x in sources};claim_ids={x.get("id") for x in claims}
check(len(sources)==len(source_ids)==150,"source IDs/count are not unique or unexpected")
check(len(claims)==len(claim_ids)==82,"claim IDs/count are not unique or unexpected")
check(len(notes)==21,"unexpected research note count")
for record in claims+notes:
    for sid in record.get("source_ids",[]):check(sid in source_ids,f"{record.get('id')}: unknown source {sid}")

try:
    with (ROOT/"data/sources.csv").open(encoding="utf-8",newline="") as f:csv_sources=list(csv.DictReader(f))
    check({x["id"] for x in csv_sources}==source_ids,"sources.csv and source JSONL IDs differ")
except Exception as exc:errors.append(f"sources.csv: {exc}")

meta=loadj("data/datasets/noaa_goes_primary_xrays_6hour_2026-11-03.metadata.json")
raw_path=ROOT/"data/datasets/noaa_goes_primary_xrays_6hour_2026-11-03.json"
raw=loadj("data/datasets/noaa_goes_primary_xrays_6hour_2026-11-03.json")
paired=loadj("data/datasets/noaa_goes_primary_xrays_6hour_paired_2026-11-03.json")
registry=loadj("data/dataset_registry.json")
if meta and raw is not None and paired and registry:
    check(meta.get("source_url")=="https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json","NOAA capture URL mismatch")
    check(sha(raw_path)==meta.get("raw_sha256"),"raw NOAA snapshot hash differs from capture record")
    check(len(raw)==meta.get("record_count")==716,"raw NOAA row count mismatch")
    check(sorted({x.get("energy") for x in raw})==["0.05-0.4nm","0.1-0.8nm"],"unexpected GOES channel labels")
    expected=pair_rows(raw)
    check(expected==paired.get("records"),"paired GOES records differ from deterministic exact pairing")
    check(len(expected)==paired.get("record_count")==358,"paired GOES row count mismatch")
    actual_keys={(x["time_tag"],x["satellite"],x["energy"]) for x in raw}
    check(len(actual_keys)==len(raw),"duplicate timestamp/satellite/channel in raw NOAA payload")
    groups=defaultdict(set)
    for x in raw:groups[(x["time_tag"],x["satellite"])].add(x["energy"])
    check(all(v=={"0.05-0.4nm","0.1-0.8nm"} for v in groups.values()),"unmatched GOES channel row")
    check(registry.get("atlas_version")=="1.0" and len(registry.get("datasets",[]))==10,"dataset registry release/version mismatch")
    for ds in registry.get("datasets",[]):
        for item in ds.get("files",[]):
            path=ROOT/item["path"]
            check(path.is_file(),f"dataset file missing: {item['path']}")
            if path.is_file():check(sha(path)==item["sha256"],f"dataset file hash mismatch: {item['path']}")

prov=loadl("data/provenance/release_v10_sources.jsonl")
prov_ids={x.get("record_id") for x in prov}
check(len(prov)==7 and len(prov_ids)==7,"v1.0 provenance record IDs/count mismatch")
for s in sources:
    if s.get("research_batch") in {"v1.0-public-history","v1.0-observations"}:
        check("PROV-V10-"+s["id"] in prov_ids,f"missing provenance for {s['id']}")
check(any(x.get("record_id")=="PROV-V10-NOAA-XRS-PAIR" and x.get("input_sha256")==((meta or {}).get("raw_sha256")) for x in prov),"derived GOES provenance is not tied to raw hash")

index=loadj("data/unified_search_index_v10.json");manifest=loadj("data/unified_search_manifest_v10.json")
if index and manifest:
    copy=dict(manifest);reported=copy.pop("manifest_sha256",None)
    check(reported==canon(copy),"search input manifest digest mismatch")
    check(index.get("manifest_sha256")==reported,"index and input manifest digest differ")
    check(index.get("entry_count")==len(index.get("entries",[]))==manifest.get("entry_count"),"search item count mismatch")
    for item in manifest.get("inputs",[]):
        path=ROOT/item["path"]
        check(path.is_file(),f"search input missing: {item['path']}")
        if path.is_file():check(sha(path)==item["sha256"],f"search input hash mismatch: {item['path']}")
    by_kind=Counter(x["kind"] for x in index["entries"])
    check(all(by_kind[k]>0 for k in ["source","claim","research_note","publication","dataset","document"]),"search index missing one or more record types")
    ids={x["id"] for x in index["entries"]}
    check(source_ids <= ids,"one or more source cards absent from unified search")
    check(claim_ids <= ids,"one or more claims absent from unified search")
    check("DS-GOES-XRS-PRIMARY-6H-2026-11-03" in ids and "DS-GOES-XRS-PAIRED-2026-11-03" in ids,"new GOES datasets absent from search")

    search_html=(ROOT/"site/unified_search.html").read_text(encoding="utf-8")
    check(not re.search(r"\bfetch\s*\(",search_html),"unified search contains a live fetch call")
    check(not re.search(r"<script[^>]+src=",search_html,re.I),"unified search has an external script dependency")
    parser=EmbeddedJSON("catalog");parser.feed(search_html)
    try:embedded=json.loads("".join(parser.parts));check(embedded==index["entries"],"search page does not embed the exact index entries")
    except Exception as exc:errors.append(f"unified search embedded catalog invalid ({exc})")
    coverage=loadj("data/coverage_report_v10.json")
    cp=EmbeddedJSON("report");cp.feed((ROOT/"site/coverage.html").read_text(encoding="utf-8"))
    try:check(json.loads("".join(cp.parts))==coverage,"coverage page and report differ")
    except Exception as exc:errors.append(f"coverage page embedded report invalid ({exc})")
    if coverage:check(coverage["counts"]["sources"]==len(sources) and coverage["counts"]["claims"]==len(claims) and coverage["counts"]["datasets"]==10,"coverage counts differ from ledgers")

packet=loadj("data/packets/examples/atlas-cross-domain-research.v1.0.packet.json")
if packet and index and manifest:
    copy=dict(packet);reported=copy.pop("packet_sha256",None)
    check(reported==canon(copy),"AI packet checksum mismatch")
    check(packet.get("inputs",{}).get("index_sha256")==sha(ROOT/"data/unified_search_index_v10.json"),"AI packet index hash mismatch")
    check(packet.get("inputs",{}).get("manifest_sha256")==manifest.get("manifest_sha256"),"AI packet manifest hash mismatch")
    check(bool(packet.get("results")),"AI example packet contains no results")

lineage=loadj("data/release_v10_lineage.json")
if lineage:
    parent=lineage.get("parent_entries",[]);parent_text="".join(f"{x['sha256']}  {x['path']}\n" for x in parent)
    check(len(parent)==lineage.get("parent_entry_count"),"parent lineage count mismatch")
    check(sha256(parent_text.encode())==lineage.get("parent_manifest_sha256"),"parent manifest digest cannot be reproduced")
    allowed=set(lineage.get("allowed_changed_paths",[]));base={x["path"]:x["sha256"] for x in parent}
    for path,digest in base.items():
        f=ROOT/path
        check(f.is_file(),f"inherited v0.8 path missing: {path}")
        if f.is_file() and sha(f)!=digest:check(path in allowed,f"undeclared v0.8 file change: {path}")
    current={p.relative_to(ROOT).as_posix() for p in iter_release_files(ROOT) if p.name not in {"MANIFEST.sha256","release_v10_lineage.json"}}
    actual_added=(current-set(base))|{"data/release_v10_lineage.json"}
    check(actual_added==set(lineage.get("added_paths",[])),"added release paths differ from lineage inventory")
    release_entries={x["path"]:x["sha256"] for x in lineage.get("release_entries",[])}
    check(len(release_entries)==lineage.get("release_entry_count"),"release path hash count mismatch")
    check(set(release_entries)==current,"release file inventory differs from stored hashes")
    for path,digest in release_entries.items():
        if (ROOT/path).is_file():check(sha(ROOT/path)==digest,f"release content hash differs from lineage: {path}")
    old={x["path"]:x["sha256"] for x in parent}
    check(old.get("assets/signal_atlas_logo_header.png")==sha(ROOT/"assets/signal_atlas_logo_header.png"),"evergreen README logo changed")
    changed_now=sorted(path for path,h in old.items() if sha(ROOT/path)!=h)
    check(changed_now==sorted(allowed),"declared changed paths are not the exact v0.8 delta")

readme=(ROOT/"README.md").read_text(encoding="utf-8")
check(readme.startswith("# SIGNAL ATLAS\n\n![Signal Atlas evergreen identity](assets/signal_atlas_logo_header.png)"),"evergreen logo is not first in README")
site=(ROOT/"site/index.html").read_text(encoding="utf-8")
check("const CLAIM_COUNT=82;" in site and "SRC-152" in site and "UNIFIED SEARCH" in site,"main explorer navigation or embedded ledgers are stale")

if errors:
    for item in errors:print("ERROR",item)
    print(f"v1.0 validation: FAIL ({len(errors)} issue(s))")
    sys.exit(1)
print(f"v1.0 validation: PASS; sources={len(sources)} claims={len(claims)} datasets=10; GOES raw={len(raw)} paired={len(paired['records'])}; search={index['entry_count']} entries; parent={lineage['parent_entry_count']} files; added={len(lineage['added_paths'])}")
