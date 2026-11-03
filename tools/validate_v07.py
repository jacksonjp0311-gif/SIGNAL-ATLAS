#!/usr/bin/env python3
"""Check v0.7 dataset integration, packet integrity, and complete v0.6 inheritance."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_space_weather_v07 import canonical_sha256, EXPECTED_BASELINE_CHANGES

errors: list[str] = []


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON ({exc})")
        return None


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


registry_path = ROOT / "data" / "dataset_registry.json"
registry = load_json(registry_path)
geomag = load_json(ROOT / "data" / "datasets" / "noaa_daily_geomagnetic_2026-11-03.json")
joined = load_json(ROOT / "data" / "datasets" / "noaa_f107_kp_daily_join_2026-11-03.json")
packet_path = ROOT / "data" / "packets" / "examples" / "space-weather-noaa-2026-11-03.v0.7.packet.json"
packet = load_json(packet_path)

if registry:
    require(registry.get("atlas_version") == "0.7", "dataset registry version is not 0.7")
    ids = [item.get("dataset_id") for item in registry.get("datasets", [])]
    require(len(ids) == len(set(ids)), "dataset registry contains duplicate IDs")
    require({"DS-F107-2026-11-02", "DS-GEOMAG-2026-11-03", "DS-SPACEWEATHER-JOIN-2026-11-03", "DS-SYNTHETIC-FREQUENCY-STABILITY-V06"}.issubset(set(ids)), "dataset registry is missing a key observed, derived, or synthetic series")
    kinds = {item.get("dataset_id"): item.get("kind") for item in registry.get("datasets", [])}
    require(kinds.get("DS-F107-2026-11-02") == "observed", "F10.7 series must be marked observed")
    require(kinds.get("DS-GEOMAG-2026-11-03") == "observed", "geomagnetic series must be marked observed")
    require(kinds.get("DS-SPACEWEATHER-JOIN-2026-11-03") == "derived", "joined series must be marked derived")
    require(kinds.get("DS-SYNTHETIC-FREQUENCY-STABILITY-V06") == "synthetic", "teaching series must be marked synthetic")
    for dataset in registry.get("datasets", []):
        for item in dataset.get("files", []):
            path = ROOT / item["path"]
            require(path.is_file(), f"registry file missing: {item['path']}")
            if path.is_file():
                require(sha256(path) == item.get("sha256"), f"registry hash mismatch: {item['path']}")

if geomag:
    rows = geomag.get("records", [])
    require(geomag.get("source_id") == "SRC-144", "geomagnetic data source ID mismatch")
    require(len(rows) == 30 and geomag.get("record_count") == 30, "expected 30 raw geomagnetic dates")
    require(sum(1 for row in rows if row.get("complete_day")) == 29, "expected 29 complete geomagnetic days")
    require(rows[-1]["date"] == "2026-11-03" and not rows[-1]["complete_day"], "partial current-day source row must be retained and marked incomplete")
    require(rows[-1]["estimated_planetary_kp_3h"][1:] == [None] * 7, "source sentinel values must be represented as null")
    require(all(len(row.get("estimated_planetary_kp_3h", [])) == 8 for row in rows), "each geomagnetic row must retain eight Kp intervals")

if joined:
    rows = joined.get("records", [])
    require(joined.get("atlas_version") == "0.7", "joined dataset version is not 0.7")
    require(len(rows) == 29 and joined.get("window", {}).get("row_count") == 29, "expected 29 complete joined observations")
    require(rows[0]["date"] == "2026-10-05" and rows[-1]["date"] == "2026-11-02", "joined date window is unexpected")
    require(len({row["date"] for row in rows}) == len(rows), "joined dataset contains duplicate dates")
    require(all(row.get("complete_kp_intervals") == 8 for row in rows), "joined records must only contain complete Kp days")
    require("causal" in " ".join(joined.get("limitations", [])).lower(), "joined data must carry a causal interpretation limit")

if packet:
    unhashed = dict(packet)
    claimed = unhashed.pop("packet_sha256", None)
    require(claimed == canonical_sha256(unhashed), "packet checksum mismatch")
    require(packet.get("atlas_version") == "0.7", "packet version is not 0.7")
    require(packet.get("window", {}).get("matched_days") == 29, "packet does not carry the joined day count")
    require(len(packet.get("interpretation_limits", [])) >= 4, "packet omits dataset limitations")

source_records = []
for line in (ROOT / "data" / "sources.jsonl").read_text(encoding="utf-8").splitlines():
    if line.strip():
        try:
            source_records.append(json.loads(line))
        except Exception as exc:
            errors.append(f"sources.jsonl contains invalid JSON ({exc})")
source_ids = [item.get("id") for item in source_records]
require(len(source_ids) == len(set(source_ids)), "source catalog contains duplicate IDs")
require(source_ids.count("SRC-144") == 1, "SRC-144 must appear exactly once in sources.jsonl")
with (ROOT / "data" / "sources.csv").open(encoding="utf-8", newline="") as stream:
    csv_ids = [row.get("id") for row in csv.DictReader(stream)]
require(csv_ids.count("SRC-144") == 1, "SRC-144 must appear exactly once in sources.csv")

site_index = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
data_page = ROOT / "site" / "datasets.html"
require('href="datasets.html"' in site_index, "main site navigation does not link the data explorer")
require(data_page.is_file(), "data explorer page is missing")
if data_page.is_file():
    html = data_page.read_text(encoding="utf-8")
    require(html.count("<tr data-date=") == 29, "data explorer does not contain 29 joined table rows")
    require("space_weather_f107_kp_v07.svg" in html, "data explorer chart link is missing")
    require("noaa_f107_kp_daily_join_2026-11-03.csv" in html, "data explorer CSV link is missing")
require((ROOT / "assets" / "signal_atlas_logo_header.png").is_file(), "evergreen README logo asset is missing")
readme = (ROOT / "README.md").read_text(encoding="utf-8")
require("signal_atlas_logo_header.png" in readme, "evergreen README logo reference changed")

lineage_path = ROOT / "data" / "release_v07_lineage.json"
lineage = load_json(lineage_path)
if lineage:
    require(lineage.get("baseline_release") == "v0.6", "v0.7 lineage baseline is not v0.6")
    require(lineage.get("expected_modified_baseline_paths") == EXPECTED_BASELINE_CHANGES, "lineage allowlist differs from validator policy")
    allowed = set(lineage.get("expected_modified_baseline_paths", []))
    for item in lineage.get("baseline_manifest_entries", []):
        rel = item["path"]
        path = ROOT / Path(rel)
        require(path.is_file(), f"inherited v0.6 file is missing: {rel}")
        if path.is_file() and rel not in allowed:
            require(sha256(path) == item["sha256"], f"inherited v0.6 file changed unexpectedly: {rel}")

if errors:
    print("v0.7 validation: FAIL")
    for error in errors:
        print("-", error)
    raise SystemExit(1)

print(
    "v0.7 validation: PASS;"
    f" registry_datasets={len(registry['datasets'])};"
    f" geomagnetic_rows={geomag['record_count']};"
    f" joined_rows={len(joined['records'])};"
    f" inherited_v06_files={len(lineage['baseline_manifest_entries'])};"
    " unexpected_inheritance_changes=0"
)
