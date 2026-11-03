#!/usr/bin/env python3
"""Validate v0.8 data joins, provenance, navigation, packets, and v0.7 inheritance."""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_rtsw_v08 import EXPECTED_BASELINE_CHANGES, canonical_sha256

errors: list[str] = []


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid or missing JSON ({exc})")
        return None


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


dataset_dir = ROOT / "data" / "datasets"
raw_wind_path = dataset_dir / "noaa_rtsw_wind_1m_2026-11-03.json"
raw_mag_path = dataset_dir / "noaa_rtsw_mag_1m_2026-11-03.json"
metadata = load_json(dataset_dir / "noaa_rtsw_snapshot_metadata_2026-11-03.json")
wind_raw = load_json(raw_wind_path)
mag_raw = load_json(raw_mag_path)
wind_active_payload = load_json(dataset_dir / "noaa_rtsw_wind_1m_active_2026-11-03.json")
mag_active_payload = load_json(dataset_dir / "noaa_rtsw_mag_1m_active_2026-11-03.json")
joined = load_json(dataset_dir / "noaa_rtsw_active_paired_1m_2026-11-03.json")
daily = load_json(dataset_dir / "noaa_rtsw_daily_context_2026-11-03.json")
registry = load_json(ROOT / "data" / "dataset_registry.json")
packet = load_json(ROOT / "data" / "packets" / "examples" / "solar-wind-noaa-2026-11-03.v0.8.packet.json")
lineage = load_json(ROOT / "data" / "release_v08_lineage.json")

if metadata:
    require(metadata.get("snapshot_id") == "NOAA-RTSW-2026-11-03", "unexpected snapshot ID")
    require(metadata.get("captured_before_utc", "") <= metadata.get("captured_after_utc", ""), "snapshot capture interval is reversed")
    expected_sources = {
        "plasma": "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json",
        "magnetometer": "https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json",
    }
    for key, expected_url in expected_sources.items():
        item = metadata.get("files", {}).get(key, {})
        path = ROOT / item.get("path", "__missing__")
        require(item.get("source_url") == expected_url, f"{key} snapshot URL mismatch")
        require(path.is_file(), f"{key} raw snapshot is missing")
        if path.is_file():
            require(sha256(path) == item.get("sha256"), f"{key} raw snapshot hash differs from capture metadata")
            try:
                rows = json.loads(path.read_text(encoding="utf-8"))
                require(len(rows) == item.get("record_count"), f"{key} raw row count differs from capture metadata")
                tags = [row.get("time_tag") for row in rows]
                require(min(tags) == item.get("time_tag_start"), f"{key} earliest time tag differs from metadata")
                require(max(tags) == item.get("time_tag_end"), f"{key} latest time tag differs from metadata")
            except Exception as exc:
                errors.append(f"{key} raw snapshot cannot be parsed ({exc})")

if isinstance(wind_raw, list) and isinstance(mag_raw, list):
    wind_selected = [row for row in wind_raw if row.get("active") is True]
    mag_selected = [row for row in mag_raw if row.get("active") is True]
    wind_selected.sort(key=lambda row: (row["time_tag"], row["source"]))
    mag_selected.sort(key=lambda row: (row["time_tag"], row["source"]))
    require(wind_active_payload is not None and wind_active_payload.get("records") == wind_selected, "active plasma view differs from raw JSON boolean selections")
    require(mag_active_payload is not None and mag_active_payload.get("records") == mag_selected, "active magnetometer view differs from raw JSON boolean selections")
    if wind_active_payload:
        require(wind_active_payload.get("record_count") == len(wind_selected), "active plasma record count mismatch")
    if mag_active_payload:
        require(mag_active_payload.get("record_count") == len(mag_selected), "active magnetometer record count mismatch")
    wind_map = {(row.get("time_tag"), row.get("source")): row for row in wind_selected}
    mag_map = {(row.get("time_tag"), row.get("source")): row for row in mag_selected}
    require(len(wind_map) == len(wind_selected), "active plasma contains duplicate time/source keys")
    require(len(mag_map) == len(mag_selected), "active magnetometer contains duplicate time/source keys")
    expected_keys = sorted(set(wind_map) & set(mag_map))
    joined_rows = joined.get("records", []) if joined else []
    actual_keys = [(row.get("time_tag"), row.get("source")) for row in joined_rows]
    require(actual_keys == expected_keys, "paired series is not the exact ordered intersection of active time/source keys")
    require(len(joined_rows) == (joined or {}).get("record_count"), "paired record count mismatch")
    for row in joined_rows:
        key = (row.get("time_tag"), row.get("source"))
        wind, mag = wind_map.get(key, {}), mag_map.get(key, {})
        require(row.get("active") is True, "paired row is not marked active")
        for output, source_key in (("proton_speed_km_s", "proton_speed"), ("proton_density_cm3", "proton_density"), ("proton_temperature_K", "proton_temperature"), ("wind_sample_size", "proton_sample_size"), ("wind_overall_quality", "overall_quality")):
            require(row.get(output) == wind.get(source_key), f"paired {output} differs from plasma input at {key}")
        for output, source_key in (("bt_nT", "bt"), ("bx_gsm_nT", "bx_gsm"), ("by_gsm_nT", "by_gsm"), ("bz_gsm_nT", "bz_gsm"), ("mag_sample_size", "sample_size"), ("mag_overall_quality", "overall_quality")):
            require(row.get(output) == mag.get(source_key), f"paired {output} differs from magnetometer input at {key}")

    csv_path = dataset_dir / "noaa_rtsw_active_paired_1m_2026-11-03.csv"
    if csv_path.is_file():
        with csv_path.open(encoding="utf-8", newline="") as stream:
            csv_rows = list(csv.DictReader(stream))
        require(len(csv_rows) == len(joined_rows), "paired CSV row count differs from JSON")
        require([(row.get("time_tag"), row.get("source")) for row in csv_rows] == actual_keys, "paired CSV keys differ from JSON")
    else:
        errors.append("paired CSV is missing")

if daily and joined:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in joined.get("records", []):
        grouped[row["time_tag"][:10]].append(row)
    daily_rows = daily.get("records", [])
    require(daily.get("atlas_version") == "0.8", "daily dataset version is not 0.8")
    require(len(daily_rows) == len(grouped) == daily.get("record_count"), "daily summary coverage rows do not match paired dates")
    for row in daily_rows:
        date = row.get("date_utc")
        members = grouped.get(date, [])
        require(len(members) == row.get("matched_active_minutes"), f"daily count differs from paired rows for {date}")
        require(row.get("expected_minutes_in_utc_day") == 1440, f"daily denominator mismatch for {date}")
        require(row.get("time_tag_timezone") == "UTC", f"daily timezone label missing for {date}")
        require(row.get("coverage_status") == ("complete_utc_day" if len(members) == 1440 else "partial_utc_day"), f"daily completeness label mismatch for {date}")
        require(row.get("coverage_fraction_of_utc_day") == round(len(members) / 1440, 5), f"daily coverage fraction mismatch for {date}")
        require(row.get("source_sample_counts") == dict(sorted(Counter(item["source"] for item in members).items())), f"daily spacecraft counts mismatch for {date}")
        kp = row.get("planetary_kp_context", {})
        require(kp.get("source_id") == "SRC-144" and kp.get("estimated") is True, f"Kp provenance/status mismatch for {date}")
        if not kp.get("complete_day"):
            require(kp.get("max") is None and kp.get("mean") is None, f"incomplete Kp was summarized for {date}")
    require(all(row.get("coverage_status") == "partial_utc_day" for row in daily_rows), "the rolling sample should mark each observed UTC date partial")
    require("causal" in " ".join(joined.get("limitations", [])).lower(), "joined dataset omits its causal interpretation limitation")
    require("propagation delay" in " ".join(joined.get("limitations", [])).lower(), "joined dataset omits the upstream timing limitation")

if registry:
    require(registry.get("atlas_version") == "0.8", "dataset registry version is not 0.8")
    datasets = registry.get("datasets", [])
    ids = [item.get("dataset_id") for item in datasets]
    require(len(ids) == len(set(ids)), "dataset registry contains duplicate dataset IDs")
    required_ids = {
        "DS-F107-2026-11-02", "DS-GEOMAG-2026-11-03", "DS-SPACEWEATHER-JOIN-2026-11-03",
        "DS-SYNTHETIC-FREQUENCY-STABILITY-V06", "DS-RTSW-PLASMA-2026-11-03", "DS-RTSW-MAG-2026-11-03",
        "DS-RTSW-PAIRED-2026-11-03", "DS-RTSW-DAILY-CONTEXT-2026-11-03",
    }
    require(required_ids.issubset(set(ids)), "dataset registry is missing an inherited or v0.8 dataset")
    by_id = {item.get("dataset_id"): item for item in datasets}
    for dataset in datasets:
        for item in dataset.get("files", []):
            path = ROOT / item.get("path", "__missing__")
            require(path.is_file(), f"registry file missing: {item.get('path')}")
            if path.is_file():
                require(sha256(path) == item.get("sha256"), f"registry file hash mismatch: {item.get('path')}")
    require(by_id.get("DS-RTSW-PLASMA-2026-11-03", {}).get("kind") == "observed", "plasma dataset must be observed")
    require(by_id.get("DS-RTSW-MAG-2026-11-03", {}).get("kind") == "observed", "magnetometer dataset must be observed")
    require(by_id.get("DS-RTSW-PAIRED-2026-11-03", {}).get("kind") == "derived", "paired dataset must be derived")
    require(by_id.get("DS-RTSW-DAILY-CONTEXT-2026-11-03", {}).get("kind") == "derived", "daily context must be derived")
    require(by_id.get("DS-SYNTHETIC-FREQUENCY-STABILITY-V06", {}).get("kind") == "synthetic", "teaching series must remain synthetic")

source_ids: set[str] = set()
for line in (ROOT / "data" / "sources.jsonl").read_text(encoding="utf-8").splitlines():
    if line.strip():
        try:
            source_ids.add(json.loads(line)["id"])
        except Exception as exc:
            errors.append(f"sources.jsonl contains invalid record ({exc})")
require("SRC-145" in source_ids, "source catalog is missing SRC-145")
require("SRC-146" in source_ids, "source catalog is missing SRC-146")
with (ROOT / "data" / "sources.csv").open(encoding="utf-8", newline="") as stream:
    csv_source_ids = [row.get("id") for row in csv.DictReader(stream)]
require(csv_source_ids.count("SRC-145") == 1 and csv_source_ids.count("SRC-146") == 1, "source CSV does not contain both v0.8 sources exactly once")

if packet:
    claimed = packet.get("packet_sha256")
    unhashed = dict(packet)
    unhashed.pop("packet_sha256", None)
    require(claimed == canonical_sha256(unhashed), "AI packet canonical checksum mismatch")
    require(packet.get("atlas_version") == "0.8", "AI packet version is not 0.8")
    require(packet.get("window", {}).get("paired_records") == (joined or {}).get("record_count"), "AI packet paired row count mismatch")
    require(packet.get("dataset_registry", {}).get("sha256") == sha256(ROOT / "data" / "dataset_registry.json"), "AI packet dataset registry checksum mismatch")
    require(len(packet.get("interpretation_limits", [])) >= 5, "AI packet omits collection limitations")
    require({"SRC-144", "SRC-145", "SRC-146"}.issubset({item.get("id") for item in packet.get("source_records", [])}), "AI packet does not list all source records")

provenance_path = ROOT / "data" / "provenance" / "release_v08_sources.jsonl"
if provenance_path.is_file():
    provenance = [json.loads(line) for line in provenance_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    provenance_by_id = {item.get("record_id"): item for item in provenance}
    require(set(provenance_by_id) == {"PROV-003", "PROV-004", "PROV-005", "PROV-006"}, "v0.8 provenance record IDs are incomplete")
    for record in provenance:
        for key in ("input_files", "output_files"):
            for item in record.get(key, []):
                path = ROOT / item["path"]
                require(path.is_file(), f"provenance file missing: {item['path']}")
                if path.is_file():
                    require(sha256(path) == item.get("sha256"), f"provenance hash mismatch: {item['path']}")
    for record in provenance:
        if record.get("record_type") == "captured_source_snapshot":
            path = ROOT / record.get("raw_file", "__missing__")
            require(path.is_file(), f"provenance raw input missing: {record.get('raw_file')}")
            if path.is_file():
                require(sha256(path) == record.get("raw_sha256"), f"provenance raw hash mismatch: {record.get('raw_file')}")
else:
    errors.append("v0.8 provenance ledger is missing")

site_index = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
explorer_path = ROOT / "site" / "solar_wind.html"
explorer = explorer_path.read_text(encoding="utf-8") if explorer_path.is_file() else ""
require('href="solar_wind.html"' in site_index, "main Atlas navigation does not link the Solar-wind Explorer")
require("solar_wind_rtsw_v08.svg" in explorer, "Solar-wind Explorer chart link is missing")
require("noaa_rtsw_active_paired_1m_2026-11-03.csv" in explorer, "Solar-wind Explorer paired CSV link is missing")
require("noaa_rtsw_snapshot_metadata_2026-11-03.json" in explorer, "Solar-wind Explorer snapshot metadata link is missing")
require(explorer.count("<tr><td>") == 2, "Solar-wind Explorer does not render both daily summary rows")
chart = ROOT / "assets" / "solar_wind_rtsw_v08.svg"
require(chart.is_file() and "<title" in chart.read_text(encoding="utf-8"), "v0.8 teaching chart is missing or lacks an accessible title")
readme = (ROOT / "README.md").read_text(encoding="utf-8")
require("signal_atlas_logo_header.png" in readme, "evergreen README logo reference is missing")
require((ROOT / "assets" / "signal_atlas_logo_header.png").is_file(), "evergreen README logo asset is missing")
for path in (
    ROOT / "docs" / "science" / "09_solar_wind_observations.md",
    ROOT / "courses" / "28_solar_wind_time_alignment.md",
    ROOT / "docs" / "research" / "DATA_COLLECTION_GUIDE_v08.md",
    ROOT / "docs" / "research" / "RELEASE_SUMMARY_v08.md",
    ROOT / "docs" / "research" / "RELEASE_AUDIT_v08.md",
):
    require(path.is_file(), f"v0.8 learning/release document is missing: {path.relative_to(ROOT)}")

if lineage:
    require(lineage.get("baseline_release") == "v0.7", "v0.8 lineage baseline is not v0.7")
    require(lineage.get("expected_modified_baseline_paths") == EXPECTED_BASELINE_CHANGES, "v0.8 baseline allowlist differs from builder policy")
    allowed = set(EXPECTED_BASELINE_CHANGES)
    missing: list[str] = []
    changed: list[str] = []
    for item in lineage.get("baseline_manifest_entries", []):
        rel = item.get("path", "")
        path = ROOT / Path(rel)
        if not path.is_file():
            missing.append(rel)
        elif rel not in allowed and sha256(path) != item.get("sha256"):
            changed.append(rel)
    require(not missing, f"inherited v0.7 files are missing: {missing[:8]}")
    require(not changed, f"inherited v0.7 files changed outside the integration allowlist: {changed[:8]}")
    require(len(lineage.get("baseline_manifest_entries", [])) >= 250, "v0.7 inheritance manifest is unexpectedly small")

if errors:
    print("v0.8 validation: FAIL")
    for error in errors:
        print("-", error)
    raise SystemExit(1)

print(
    "v0.8 validation: PASS; "
    f"raw_plasma={metadata['files']['plasma']['record_count']}; "
    f"raw_magnetometer={metadata['files']['magnetometer']['record_count']}; "
    f"active_pairs={joined['record_count']}; "
    f"partial_daily_rows={daily['record_count']}; "
    f"registry_datasets={len(registry['datasets'])}; "
    f"inherited_v07_files={len(lineage['baseline_manifest_entries'])}; "
    "unexpected_inheritance_changes=0"
)
