#!/usr/bin/env python3
"""Build Signal Atlas v0.8 solar-wind data products from frozen local snapshots."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import re
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATASETS = DATA / "datasets"
RAW_WIND = DATASETS / "noaa_rtsw_wind_1m_2026-11-03.json"
RAW_MAG = DATASETS / "noaa_rtsw_mag_1m_2026-11-03.json"
SNAPSHOT_META = DATASETS / "noaa_rtsw_snapshot_metadata_2026-11-03.json"
GEOMAG = DATASETS / "noaa_daily_geomagnetic_2026-11-03.json"
WIND_ACTIVE = DATASETS / "noaa_rtsw_wind_1m_active_2026-11-03.json"
MAG_ACTIVE = DATASETS / "noaa_rtsw_mag_1m_active_2026-11-03.json"
JOIN_JSON = DATASETS / "noaa_rtsw_active_paired_1m_2026-11-03.json"
JOIN_CSV = DATASETS / "noaa_rtsw_active_paired_1m_2026-11-03.csv"
DAILY_JSON = DATASETS / "noaa_rtsw_daily_context_2026-11-03.json"
DAILY_CSV = DATASETS / "noaa_rtsw_daily_context_2026-11-03.csv"
REGISTRY = DATA / "dataset_registry.json"
SOURCE_JSONL = DATA / "sources.jsonl"
SOURCE_CSV = DATA / "sources.csv"
PROVENANCE = DATA / "provenance" / "release_v08_sources.jsonl"
PACKET = DATA / "packets" / "examples" / "solar-wind-noaa-2026-11-03.v0.8.packet.json"
CHART = ROOT / "assets" / "solar_wind_rtsw_v08.svg"
EXPLORER = ROOT / "site" / "solar_wind.html"

WIND_URL = "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json"
MAG_URL = "https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json"

EXPECTED_BASELINE_CHANGES = sorted([
    "CHANGELOG.md",
    "README.md",
    "THREAD-RESUME-HANDOFF.md",
    "courses/README.md",
    "data/README.md",
    "data/atlas_index.sqlite",
    "data/dataset_registry.json",
    "data/datasets/README.md",
    "data/sources.csv",
    "data/sources.jsonl",
    "docs/INDEX.md",
    "docs/research/ROADMAP_TO_1.0.md",
    "docs/science/README.md",
    "site/datasets.html",
    "site/index.html",
    "tools/release.py",
])


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256_bytes(payload.encode("utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def ensure_lineage() -> dict:
    path = DATA / "release_v08_lineage.json"
    if path.is_file():
        lineage = json.loads(path.read_text(encoding="utf-8"))
        if lineage.get("baseline_release") != "v0.7":
            raise ValueError("Existing v0.8 lineage must identify v0.7 as its baseline")
        if lineage.get("expected_modified_baseline_paths") != EXPECTED_BASELINE_CHANGES:
            raise ValueError("The v0.8 lineage change allowlist differs from the builder contract")
        return lineage
    manifest = ROOT / "MANIFEST.sha256"
    if not manifest.is_file():
        raise FileNotFoundError("The complete v0.7 MANIFEST.sha256 is required")
    entries = []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        entries.append({"path": relative.replace("\\", "/"), "sha256": digest})
    if not entries:
        raise ValueError("The v0.7 baseline manifest is empty")
    lineage = {
        "schema": "signal-atlas.release-lineage.v1",
        "baseline_release": "v0.7",
        "baseline_manifest_sha256": sha256_file(manifest),
        "baseline_manifest_entries": entries,
        "expected_modified_baseline_paths": EXPECTED_BASELINE_CHANGES,
        "preservation_rule": "Every v0.7 baseline path remains in v0.8. Hashes stay unchanged except for the explicitly listed integration files.",
    }
    write_json(path, lineage)
    return lineage


def source_records() -> list[dict]:
    return [
        {
            "id": "SRC-145",
            "title": "NOAA SWPC real-time solar-wind plasma, one-minute product",
            "publisher": "NOAA Space Weather Prediction Center",
            "country": "International",
            "domain": "science",
            "url": WIND_URL,
            "summary": "One-minute in-situ solar-wind proton speed, density, and temperature records from the available upstream spacecraft; source and active-selection fields are preserved in a dated snapshot.",
            "source_type": "official observation product",
            "time_scope": "Rolling last-24-hour snapshot captured 2026-11-03; source time tags retained",
            "rights": "Reuse terms not independently reviewed; original NOAA SWPC source URL retained.",
            "review_status": "dated operational data snapshot included",
            "added_at": "2026-11-03",
            "topics": ["solar wind", "plasma", "space weather", "observations", "time series"],
            "snapshot_status": "dataset-snapshot-included",
            "language": "en",
            "checked_at": "2026-11-03",
            "research_batch": "2026-11-03-B",
        },
        {
            "id": "SRC-146",
            "title": "NOAA SWPC real-time solar-wind magnetic field, one-minute product",
            "publisher": "NOAA Space Weather Prediction Center",
            "country": "International",
            "domain": "science",
            "url": MAG_URL,
            "summary": "One-minute in-situ interplanetary magnetic-field components from available upstream spacecraft; source and active-selection fields are preserved in a dated snapshot.",
            "source_type": "official observation product",
            "time_scope": "Rolling last-24-hour snapshot captured 2026-11-03; source time tags retained",
            "rights": "Reuse terms not independently reviewed; original NOAA SWPC source URL retained.",
            "review_status": "dated operational data snapshot included",
            "added_at": "2026-11-03",
            "topics": ["solar wind", "interplanetary magnetic field", "space weather", "observations", "time series"],
            "snapshot_status": "dataset-snapshot-included",
            "language": "en",
            "checked_at": "2026-11-03",
            "research_batch": "2026-11-03-B",
        },
    ]


def ensure_source_catalog(sources: list[dict]) -> None:
    existing = [json.loads(line) for line in SOURCE_JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]
    by_id = {item["id"]: item for item in existing}
    if len(by_id) != len(existing):
        raise ValueError("The source JSONL already contains duplicate IDs")
    for source in sources:
        old = by_id.get(source["id"])
        if old is not None and old != source:
            raise ValueError(f"{source['id']} exists with different content")
        if old is None:
            existing.append(source)
    existing.sort(key=lambda item: int(item["id"].split("-")[1]))
    SOURCE_JSONL.write_text(
        "".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in existing),
        encoding="utf-8",
    )

    with SOURCE_CSV.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    if not fields or "id" not in fields:
        raise ValueError("sources.csv has no recognized header")
    csv_ids = {row.get("id") for row in rows}
    for source in sources:
        if source["id"] in csv_ids:
            continue
        row = dict(source)
        row["topics"] = json.dumps(source.get("topics", []), ensure_ascii=False)
        rows.append({key: str(row.get(key, "")) for key in fields})
        csv_ids.add(source["id"])
    with SOURCE_CSV.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_snapshot(path: Path, metadata: dict, key: str) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing frozen input {path.relative_to(ROOT)}; run tools/fetch_rtsw_snapshot_v08.py first")
    expected = metadata["files"][key]
    actual_hash = sha256_file(path)
    if actual_hash != expected["sha256"]:
        raise ValueError(f"Snapshot hash differs from capture metadata: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, list) or not value or not all(isinstance(row, dict) for row in value):
        raise ValueError(f"Invalid object-array snapshot: {path.name}")
    return value


def select_active(records: list[dict]) -> list[dict]:
    active = [row for row in records if row.get("active") is True]
    keys = [(row.get("time_tag"), row.get("source")) for row in active]
    if any(not time_tag or not source for time_tag, source in keys):
        raise ValueError("Active records must contain a timestamp and source")
    if len(keys) != len(set(keys)):
        raise ValueError("Active records contain duplicate timestamp/source keys")
    active.sort(key=lambda row: (row["time_tag"], row["source"]))
    return active


def pair_active_rows(wind_rows: list[dict], mag_rows: list[dict]) -> list[dict]:
    """Join selected primary records exactly on source and the unchanged time_tag."""
    wind = {(row["time_tag"], row["source"]): row for row in wind_rows if row.get("active") is True}
    mag = {(row["time_tag"], row["source"]): row for row in mag_rows if row.get("active") is True}
    if len(wind) != sum(row.get("active") is True for row in wind_rows):
        raise ValueError("Active plasma rows have duplicate source/time keys")
    if len(mag) != sum(row.get("active") is True for row in mag_rows):
        raise ValueError("Active magnetometer rows have duplicate source/time keys")
    rows = []
    for time_tag, source in sorted(set(wind) & set(mag)):
        w, m = wind[(time_tag, source)], mag[(time_tag, source)]
        rows.append({
            "time_tag": time_tag,
            "source": source,
            "active": True,
            "proton_speed_km_s": w.get("proton_speed"),
            "proton_density_cm3": w.get("proton_density"),
            "proton_temperature_K": w.get("proton_temperature"),
            "bt_nT": m.get("bt"),
            "bx_gsm_nT": m.get("bx_gsm"),
            "by_gsm_nT": m.get("by_gsm"),
            "bz_gsm_nT": m.get("bz_gsm"),
            "wind_sample_size": w.get("proton_sample_size"),
            "mag_sample_size": m.get("sample_size"),
            "wind_overall_quality": w.get("overall_quality"),
            "mag_overall_quality": m.get("overall_quality"),
        })
    return rows


def _numbers(rows: list[dict], field: str) -> dict:
    values = [float(row[field]) for row in rows if isinstance(row.get(field), (int, float)) and math.isfinite(float(row[field]))]
    if not values:
        return {"valid_count": 0, "mean": None, "median": None, "min": None, "max": None}
    return {
        "valid_count": len(values),
        "mean": round(statistics.fmean(values), 5),
        "median": round(statistics.median(values), 5),
        "min": round(min(values), 5),
        "max": round(max(values), 5),
    }


def daily_context(rows: list[dict], geomag: dict) -> list[dict]:
    by_date: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_date[row["time_tag"][:10]].append(row)
    kp_by_date = {row["date"]: row for row in geomag.get("records", [])}
    result = []
    for date, day_rows in sorted(by_date.items()):
        kp_row = kp_by_date.get(date)
        kp_values = [] if not kp_row else [v for v in kp_row.get("estimated_planetary_kp_3h", []) if isinstance(v, (int, float))]
        complete_kp = bool(kp_row and kp_row.get("complete_day") and len(kp_values) == 8)
        bz_values = [float(row["bz_gsm_nT"]) for row in day_rows if isinstance(row.get("bz_gsm_nT"), (int, float))]
        result.append({
            "date_utc": date,
            "time_tag_timezone": "UTC",
            "matched_active_minutes": len(day_rows),
            "expected_minutes_in_utc_day": 1440,
            "coverage_fraction_of_utc_day": round(len(day_rows) / 1440, 5),
            "coverage_status": "partial_utc_day",
            "start_time_tag": min(row["time_tag"] for row in day_rows),
            "end_time_tag": max(row["time_tag"] for row in day_rows),
            "source_sample_counts": dict(sorted(Counter(row["source"] for row in day_rows).items())),
            "statistics": {
                "proton_speed_km_s": _numbers(day_rows, "proton_speed_km_s"),
                "proton_density_cm3": _numbers(day_rows, "proton_density_cm3"),
                "proton_temperature_K": _numbers(day_rows, "proton_temperature_K"),
                "bz_gsm_nT": _numbers(day_rows, "bz_gsm_nT"),
            },
            "bz_gsm_southward_fraction": round(sum(value < 0 for value in bz_values) / len(bz_values), 5) if bz_values else None,
            "planetary_kp_context": {
                "source_id": "SRC-144",
                "estimated": True,
                "complete_day": complete_kp,
                "available_3h_intervals": len(kp_values),
                "max": round(max(kp_values), 3) if complete_kp else None,
                "mean": round(statistics.fmean(kp_values), 5) if complete_kp else None,
            },
        })
    return result


def _f(value: object, digits: int = 3) -> str:
    if not isinstance(value, (int, float)):
        return "—"
    return f"{value:.{digits}f}"


def create_chart(rows: list[dict]) -> None:
    width, height = 1080, 670
    left, right = 94, 34
    plot_width = width - left - right
    source_colors = {"ACE": "#ffad68", "SOLAR1": "#57d9cf", "IMAP": "#bca4e8", "DSCOVR": "#8db4ff"}
    for source in sorted({row["source"] for row in rows}):
        source_colors.setdefault(source, "#f178a7")
    dates = [datetime.fromisoformat(row["time_tag"]) for row in rows]
    start, end = min(dates), max(dates)
    span = max((end - start).total_seconds(), 1.0)
    panels = [
        ("proton_speed_km_s", "Solar-wind proton speed (km/s)", 135, 205, "proton_speed_km_s"),
        ("bz_gsm_nT", "IMF Bz GSM (nT)", 395, 205, "bz_gsm_nT"),
    ]
    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">NOAA SWPC active solar-wind and IMF measurements</title>',
        '<desc id="desc">One-minute selected-source plasma speed and GSM Bz from the dated v0.8 snapshot. The active spacecraft switches during the sample; gaps are not interpolated.</desc>',
        '<rect width="100%" height="100%" fill="#071322"/>',
        '<style>text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#edf1eb}.muted{fill:#9aaebc}.grid{stroke:#294256;stroke-width:1}.axis{stroke:#69869a;stroke-width:1.2}.speed{font-size:17px;font-weight:700}.small{font-size:12px}</style>',
        '<text x="94" y="38" font-size="23" font-weight="800">Solar-wind conditions upstream of Earth</text>',
        '<text x="94" y="62" class="muted small">NOAA SWPC selected active spacecraft · source time tags · 2026-11-02 to 2026-11-03</text>',
    ]
    for field, label, top, panel_height, _ in panels:
        values = [float(row[field]) for row in rows if isinstance(row.get(field), (int, float))]
        if not values:
            continue
        lo, hi = min(values), max(values)
        if math.isclose(lo, hi):
            hi = lo + 1
        pad = (hi - lo) * 0.08
        lo -= pad
        hi += pad
        bottom = top + panel_height
        pieces.append(f'<text x="{left}" y="{top-16}" class="speed">{html.escape(label)}</text>')
        for step in range(5):
            y = top + panel_height * step / 4
            v = hi - (hi - lo) * step / 4
            pieces.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width-right}" y2="{y:.1f}" class="grid"/>')
            pieces.append(f'<text x="{left-10}" y="{y+4:.1f}" text-anchor="end" class="muted small">{v:.1f}</text>')
        pieces.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" class="axis"/>')
        pieces.append(f'<line x1="{left}" y1="{bottom}" x2="{width-right}" y2="{bottom}" class="axis"/>')
        for source in sorted(source_colors):
            selected = [row for row in rows if row["source"] == source and isinstance(row.get(field), (int, float))]
            if not selected:
                continue
            segments: list[list[tuple[float, float]]] = []
            segment: list[tuple[float, float]] = []
            prior: datetime | None = None
            for row in selected:
                stamp = datetime.fromisoformat(row["time_tag"])
                if prior is not None and (stamp - prior).total_seconds() > 120:
                    if segment:
                        segments.append(segment)
                    segment = []
                x = left + (stamp - start).total_seconds() / span * plot_width
                y = top + (hi - float(row[field])) / (hi - lo) * panel_height
                segment.append((x, y))
                prior = stamp
            if segment:
                segments.append(segment)
            for segment in segments:
                if len(segment) < 2:
                    continue
                path_data = " ".join(("M" if index == 0 else "L") + f"{x:.1f},{y:.1f}" for index, (x, y) in enumerate(segment))
                pieces.append(f'<path d="{path_data}" fill="none" stroke="{source_colors[source]}" stroke-width="1.8"/>')
    tick_times = [start, start + (end - start) / 2, end]
    for tick in tick_times:
        x = left + (tick - start).total_seconds() / span * plot_width
        pieces.append(f'<line x1="{x:.1f}" y1="600" x2="{x:.1f}" y2="606" class="axis"/>')
        pieces.append(f'<text x="{x:.1f}" y="623" text-anchor="middle" class="muted small">{tick.strftime("%b %d %H:%M")} UTC</text>')
    legend_y = 653
    x0 = left
    for source, color in sorted(source_colors.items()):
        if source not in {row["source"] for row in rows}:
            continue
        pieces.append(f'<line x1="{x0}" y1="{legend_y-4}" x2="{x0+22}" y2="{legend_y-4}" stroke="{color}" stroke-width="3"/>')
        pieces.append(f'<text x="{x0+28}" y="{legend_y}" class="small">{html.escape(source)}</text>')
        x0 += 135
    pieces.append('<text x="740" y="653" class="muted small">No interpolation · partial dates · no propagation lag applied</text>')
    pieces.append("</svg>")
    CHART.write_text("\n".join(pieces) + "\n", encoding="utf-8")


def create_explorer(daily_rows: list[dict], pair_count: int, wind_meta: dict, mag_meta: dict) -> None:
    table_rows = []
    for row in daily_rows:
        stats = row["statistics"]
        kp = row["planetary_kp_context"]
        table_rows.append(
            "<tr>"
            f"<td>{html.escape(row['date_utc'])}</td>"
            f"<td>{row['matched_active_minutes']:,} / 1,440 ({row['coverage_fraction_of_utc_day']*100:.1f}%)</td>"
            f"<td>{html.escape(', '.join(f'{k}: {v}' for k,v in row['source_sample_counts'].items()))}</td>"
            f"<td>{_f(stats['proton_speed_km_s']['median'])}</td>"
            f"<td>{_f(stats['proton_density_cm3']['median'])}</td>"
            f"<td>{_f(stats['bz_gsm_nT']['min'])}</td>"
            f"<td>{_f(kp['max']) if kp['complete_day'] else 'partial/withheld'}</td>"
            "</tr>"
        )
    file_links = [
        ("Raw plasma snapshot", "../data/datasets/noaa_rtsw_wind_1m_2026-11-03.json"),
        ("Raw magnetic-field snapshot", "../data/datasets/noaa_rtsw_mag_1m_2026-11-03.json"),
        ("Snapshot metadata and raw-file hashes", "../data/datasets/noaa_rtsw_snapshot_metadata_2026-11-03.json"),
        ("Active plasma records", "../data/datasets/noaa_rtsw_wind_1m_active_2026-11-03.json"),
        ("Active magnetic records", "../data/datasets/noaa_rtsw_mag_1m_active_2026-11-03.json"),
        ("Paired one-minute CSV", "../data/datasets/noaa_rtsw_active_paired_1m_2026-11-03.csv"),
        ("Paired one-minute JSON", "../data/datasets/noaa_rtsw_active_paired_1m_2026-11-03.json"),
        ("Daily context CSV", "../data/datasets/noaa_rtsw_daily_context_2026-11-03.csv"),
        ("Dataset registry", "../data/dataset_registry.json"),
        ("AI-readable packet", "../data/packets/examples/solar-wind-noaa-2026-11-03.v0.8.packet.json"),
        ("Science guide", "../docs/science/09_solar_wind_observations.md"),
        ("Lesson 28", "../courses/28_solar_wind_time_alignment.md"),
    ]
    links = "\n".join(f'<a href="{url}">{html.escape(label)}</a>' for label, url in file_links)
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Signal Atlas — Solar-wind Explorer</title>
<style>
:root{{color-scheme:dark;--bg:#071322;--panel:#102336;--line:#325067;--teal:#57d9cf;--orange:#ffad68;--ink:#edf1eb;--muted:#9aaebc}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Segoe UI,Arial,sans-serif}}main{{max-width:1120px;margin:auto;padding:28px}}a{{color:var(--teal)}}header,.card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:22px;margin:18px 0}}header{{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}}h1{{margin:.15rem 0;font-size:clamp(2rem,5vw,3.2rem)}}p{{max-width:85ch;color:var(--muted)}}.kicker{{color:var(--orange);letter-spacing:.12em;text-transform:uppercase;font-size:.8rem}}.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}}.stat{{background:#0b1a28;padding:14px;border-radius:10px}}.stat strong{{display:block;color:var(--teal);font-size:1.3rem}}img{{width:100%;height:auto;border-radius:10px}}.table-wrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;min-width:800px}}th,td{{padding:9px;border-bottom:1px solid var(--line);text-align:left}}th{{color:var(--teal)}}.links{{display:flex;flex-wrap:wrap;gap:12px 20px}}.note{{border-left:3px solid var(--orange);padding-left:14px}}
</style></head><body><main>
<header><div><div class="kicker">Signal Atlas · observed data collection · v0.8</div><h1>Solar-wind Explorer</h1><p>One-minute NOAA SWPC plasma and magnetic-field measurements, paired only when the selected primary spacecraft and unchanged source time tag match.</p></div><a href="index.html">Back to the Atlas</a></header>
<section class="card stats" aria-label="Snapshot summary"><div class="stat"><strong>{pair_count:,}</strong>matched active one-minute records</div><div class="stat"><strong>{html.escape(wind_meta['time_tag_start'])}</strong>first plasma time tag</div><div class="stat"><strong>{html.escape(wind_meta['time_tag_end'])}</strong>last plasma time tag</div><div class="stat"><strong>2</strong>selected spacecraft in paired data</div></section>
<section class="card"><h2>Measured upstream conditions</h2><p>NOAA SWPC uses in-situ solar-wind measurements from spacecraft upstream of Earth. The sample crosses an active-spacecraft switch; color identifies spacecraft. Data gaps remain visible and are not interpolated.</p><img src="../assets/solar_wind_rtsw_v08.svg" alt="One-minute solar-wind proton speed and interplanetary magnetic field Bz measurements by active spacecraft"></section>
<section class="card"><h2>Partial UTC-day summaries</h2><p>Daily bins below count paired minutes against 1,440 possible minutes. The rolling source window does not cover whole UTC days. Kp is shown only when the archived daily source has all eight estimated three-hour intervals; it is day-level context and has not been time-shifted to match solar-wind arrival at Earth.</p><div class="table-wrap"><table><thead><tr><th>UTC date</th><th>Paired coverage</th><th>Active source samples</th><th>Median speed (km/s)</th><th>Median density (cm⁻³)</th><th>Minimum Bz GSM (nT)</th><th>Estimated Kp daily max</th></tr></thead><tbody>{''.join(table_rows)}</tbody></table></div></section>
<section class="card note"><h2>How to read this sample</h2><p>The plasma and magnetic-field feeds are separate files and may select spacecraft independently. This release pairs records only when <code>time_tag</code> and <code>source</code> are identical and both are marked <code>active: true</code>. Other spacecraft records stay available in the raw snapshots. Quality fields remain present; this descriptive compilation does not assign undocumented quality thresholds.</p><p>The records are measured upstream, at spacecraft locations near the Sun–Earth line. No propagation delay is applied. A same-time or same-date association with geomagnetic Kp is not a causal test or forecast.</p></section>
<section class="card"><h2>Open the collection</h2><nav class="links">{links}</nav></section>
</main></body></html>'''
    EXPLORER.write_text(page, encoding="utf-8")


def update_text(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise ValueError(f"Cannot update expected text in {path.relative_to(ROOT)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def append_once(path: Path, marker: str, addition: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    path.write_text(text.rstrip() + "\n\n" + addition.strip() + "\n", encoding="utf-8")


def update_docs(sources: list[dict], pair_count: int, daily_rows: list[dict], metadata: dict) -> None:
    readme = ROOT / "README.md"
    update_text(readme, "## Current work: v0.7 toward v1.0", "## Current work: v0.8 toward v1.0")
    update_text(readme,
        "The current development release connects NOAA solar radio-flux and geomagnetic observations into a browsable, downloadable data collection. Start with the [Data Explorer](site/datasets.html), review the [dataset registry](data/dataset_registry.json), or follow the [data collection guide](docs/research/DATA_COLLECTION_GUIDE_v07.md) and [roadmap to v1.0](docs/research/ROADMAP_TO_1.0.md). The evergreen logo above remains version independent.",
        "The current release links NOAA solar radio flux and geomagnetic observations with one-minute solar-wind plasma and magnetic-field measurements. Start with the [solar-wind explorer](site/solar_wind.html), the [dataset registry](data/dataset_registry.json), the [data collection guide](docs/research/DATA_COLLECTION_GUIDE_v08.md), or the [roadmap to v1.0](docs/research/ROADMAP_TO_1.0.md). The evergreen logo above remains version independent.")
    update_text(readme, "**Edition:** v0.6 · **Source cards:** 142", "**Edition:** v0.8 · **Source cards:** 145")
    update_text(readme, "**v0.6 roadmap:**", "**Roadmap to v1.0:**")
    marker = "**What v0.6 adds:**"
    if "**What v0.8 adds:**" not in readme.read_text(encoding="utf-8"):
        update_text(readme, marker,
            "**What v0.8 adds:** a frozen one-minute plasma and magnetic-field snapshot, source-aware active-record selection, an exact timestamp/source paired data set, partial-day summaries, a new Solar-wind Explorer, a teaching graphic, a science guide, Lesson 28, and an AI-readable packet.\n\n**What v0.6 adds:**")
    update_text(readme, "[**v0.6 release audit**]", "[**v0.8 release audit**]")
    update_text(readme, "[**v0.8 release audit**](docs/research/RELEASE_AUDIT_v06.md)", "[**v0.8 release audit**](docs/research/RELEASE_AUDIT_v08.md)")
    append_once(readme, "- **v0.8:**", "- **v0.8:** adds the one-minute NOAA SWPC solar-wind collection, preserved raw snapshots, source-aware pairing, partial-day context tables, a registry extension, a human explorer, a teaching graphic, a reusable packet, and focused offline checks. The active spacecraft changes during the sample; this is described rather than hidden. The evergreen logo and all earlier release archives remain preserved.")

    guide = """# v0.8 NOAA solar-wind data collection guide

## What was captured

Two frozen NOAA SWPC JSON inputs retain the one-minute solar-wind plasma and magnetic-field values available during the 2026-11-03 capture. Raw inputs include records from all spacecraft in the service response. The common snapshot metadata file records retrieval time, endpoint, row count, time-tag bounds, and SHA-256 for each input.

## How the local collection is built

1. Keep raw endpoint files unchanged.
2. Create separate `active: true` files because NOAA's active flag identifies the spacecraft currently selected by forecasters for that measurement type.
3. Pair plasma and magnetometer rows only when both `time_tag` and `source` are exactly equal. Do not cross-pair spacecraft or silently round timestamps.
4. Preserve quality fields and missing values. No undocumented quality threshold is applied.
5. Group paired values by the source time-tag date for a coverage-aware daily view. Mark every incomplete UTC day as partial.
6. Display complete daily estimated Kp only as day-level context. Apply no propagation delay and make no causal claim.

## Reproduce offline

The acquisition step is separate: `python -B tools/fetch_rtsw_snapshot_v08.py` fetches NOAA's current rolling files and refuses to overwrite an existing snapshot unless `--force` is supplied. Do not use it when reproducing this release.

The builder and checks are offline and use the dated files already in the package:

```text
python -B tools/build_rtsw_v08.py
python -B -m unittest discover -s tests -p "test_v08_solar_wind.py"
python -B tools/validate_v08.py
```

The full package release command also runs the general and science/document validators and writes a manifest before creating the ZIP.
"""
    path = ROOT / "docs" / "research" / "DATA_COLLECTION_GUIDE_v08.md"
    path.write_text(guide, encoding="utf-8")
    append_once(ROOT / "docs" / "INDEX.md", "## v0.8 solar-wind data", "## v0.8 solar-wind data\n\n- [Solar-wind Explorer](../site/solar_wind.html)\n- [NOAA in-situ solar-wind science guide](science/09_solar_wind_observations.md)\n- [Lesson 28: time-aligned solar-wind data](../courses/28_solar_wind_time_alignment.md)\n- [AI research packet](../data/packets/examples/solar-wind-noaa-2026-11-03.v0.8.packet.json)\n- [Reusable data collection guide](research/DATA_COLLECTION_GUIDE_v08.md)\n- [v0.8 release audit](research/RELEASE_AUDIT_v08.md)")
    append_once(ROOT / "docs" / "science" / "README.md", "## v0.8 solar-wind measurements", "## v0.8 solar-wind measurements\n\n[NOAA in-situ solar-wind observations](09_solar_wind_observations.md) connects one-minute plasma speed, proton density, proton temperature, and IMF GSM components to the existing geomagnetic collection. The source-aware pairing keeps active spacecraft switches visible and applies no propagation lag.")
    append_once(ROOT / "courses" / "README.md", "## v0.8 learning route", "## v0.8 learning route\n\n- **Measured upstream context:** [Lesson 28](28_solar_wind_time_alignment.md) → [Solar-wind Explorer](../site/solar_wind.html) → [dataset registry](../data/dataset_registry.json) → [AI packet](../data/packets/examples/solar-wind-noaa-2026-11-03.v0.8.packet.json).")
    append_once(ROOT / "data" / "README.md", "## v0.8 solar-wind data", "## v0.8 solar-wind data\n\nThe registry adds the two frozen real-time SWPC in-situ inputs, active-selected views, exact source/time paired records, and partial UTC-day summaries. Begin with the [Solar-wind Explorer](../site/solar_wind.html) and [v0.8 collection guide](../docs/research/DATA_COLLECTION_GUIDE_v08.md).")
    append_once(ROOT / "data" / "datasets" / "README.md", "## v0.8 NOAA RTSW snapshots", f"## v0.8 NOAA RTSW snapshots\n\n- Raw plasma: `{RAW_WIND.relative_to(ROOT).as_posix()}` ({metadata['files']['plasma']['record_count']} records).\n- Raw magnetic field: `{RAW_MAG.relative_to(ROOT).as_posix()}` ({metadata['files']['magnetometer']['record_count']} records).\n- Source-aware paired view: {pair_count} rows from matching active `time_tag` and `source` values.\n- The daily context spans {daily_rows[0]['date_utc']} through {daily_rows[-1]['date_utc']}; all buckets are partial and carry their own coverage counts.\n- Raw records and upstream metadata are retained in full; rebuild the derived view offline with `python tools/build_rtsw_v08.py`.")

    update_text(ROOT / "docs" / "research" / "ROADMAP_TO_1.0.md",
        "### v0.7 — Turn collections into linked data\n\nCurrent step. Add the NOAA daily geomagnetic snapshot, pair its complete dates with the retained F10.7 series, catalog observed versus derived versus synthetic data, and connect the outputs through a viewer, lesson, provenance records, and an AI packet.\n\n### v0.8 — Broaden real data coverage\n\nAdd data families that close the clearest gaps in the coverage map: additional measured signal and spectrum collections, longer time windows, and public historical or military SIGINT records. Use a shared dataset entry format so new collections can be compared and found without being mistaken for one another.",
        "### v0.7 — Turn collections into linked data\n\nCompleted. The NOAA daily geomagnetic snapshot is paired by date with the retained F10.7 series and connected through the registry, viewer, lesson, provenance, and AI packet.\n\n### v0.8 — Broaden real data coverage\n\nCurrent step. Add a direct measured solar-wind layer—plasma and magnetic field—to the solar-radio-flux and geomagnetic records. Preserve raw 1-minute inputs, spacecraft identity and active-source changes, then link exact paired measurements and coverage-aware summaries through one registry, explorer, science guide, lesson, and packet. Longer historical windows and additional signal/spectrum and public-history material remain open coverage priorities.")

    append_once(ROOT / "CHANGELOG.md", "## v0.8 — 2026-11-03", "## v0.8 — 2026-11-03\n\n- Added captured one-minute NOAA SWPC solar-wind plasma and magnetic-field records, retaining all source spacecraft records and the source metadata.\n- Added active-selected views and an exact timestamp/source paired series; no cross-spacecraft pairing or timestamp rounding.\n- Added partial-day coverage summaries with full-day estimated Kp only when all eight source intervals are present.\n- Added registry, provenance, Solar-wind Explorer, accessible SVG, science guide, Lesson 28, data collection guide, and AI-readable packet.\n- Added source-aware integration checks and v0.7-to-v0.8 inheritance verification.\n- Preserved the evergreen README logo and all versioned archives. The user requested a public repository named `SIGNAL-ATLAS`.")

    handoff = ROOT / "THREAD-RESUME-HANDOFF.md"
    handoff_text = handoff.read_text(encoding="utf-8")
    if "## v0.8 current state" not in handoff_text:
        marker = "# Signal Atlas thread-resume handoff\n"
        block = "\n## v0.8 current state\n\n- Current development release: v0.8, continuing toward v1.0.\n- This release adds source-aware NOAA one-minute solar-wind plasma and magnetic-field data to the existing F10.7 and geomagnetic collections.\n- Start with `site/solar_wind.html`, `data/dataset_registry.json`, `docs/research/RELEASE_SUMMARY_v08.md`, and `docs/research/RELEASE_AUDIT_v08.md`.\n- Preserve the evergreen README logo and the separate v0.5, v0.6, v0.7, and v0.8 packages.\n- User priority: collect more data, make the system coherent and useful, and compile data into reusable material.\n- User approved a public GitHub repository with the clean name `SIGNAL-ATLAS`; keep it version-neutral and carry the version in releases/tags.\n"
        if marker not in handoff_text:
            raise ValueError("Thread handoff title not found")
        handoff.write_text(handoff_text.replace(marker, marker + block, 1), encoding="utf-8")

    nav = ROOT / "site" / "index.html"
    old_nav = '<a href="datasets.html" class="navbtn" style="text-decoration:none">DATA / OBSERVATIONS</a>'
    new_nav = old_nav + '<a href="solar_wind.html" class="navbtn" style="text-decoration:none">SOLAR WIND</a>'
    update_text(nav, old_nav, new_nav)
    html_text = (ROOT / "site" / "datasets.html").read_text(encoding="utf-8")
    marker = '<section class="card" id="v08-solar-wind">'
    if marker not in html_text:
        section = marker + '<h2>One-minute solar-wind observations</h2><p>Open the <a href="solar_wind.html">v0.8 Solar-wind Explorer</a> for paired plasma and magnetic-field measurements, source switching, and partial-day coverage.</p></section>\n'
        if "</main>" not in html_text:
            raise ValueError("Could not locate the Data Explorer insertion point")
        (ROOT / "site" / "datasets.html").write_text(html_text.replace("</main>", section + "</main>", 1), encoding="utf-8")

    site = nav.read_text(encoding="utf-8")
    start = site.find("const SOURCES=")
    if start < 0:
        raise ValueError("Could not locate the source-card array in site/index.html")
    start += len("const SOURCES=")
    try:
        site_sources, array_length = json.JSONDecoder().raw_decode(site[start:])
    except json.JSONDecodeError as exc:
        raise ValueError("Could not parse the source-card array in site/index.html") from exc
    if not isinstance(site_sources, list):
        raise ValueError("The site source-card value is not an array")
    end = start + array_length
    for source in sources:
        projected = {key: source.get(key) for key in ("id", "title", "publisher", "country", "domain", "url", "summary", "source_type", "time_scope", "rights", "review_status", "added_at", "topics", "snapshot_status")}
        prior = next((item for item in site_sources if item.get("id") == source["id"]), None)
        if prior is not None and prior != projected:
            raise ValueError(f"The site source card differs from {source['id']}")
        if prior is None:
            site_sources.append(projected)
    site_sources.sort(key=lambda item: int(item["id"].split("-")[1]))
    site = site[:start] + json.dumps(site_sources, ensure_ascii=False, separators=(",", ":")) + site[end:]
    nav.write_text(site, encoding="utf-8")


def build() -> dict:
    ensure_lineage()
    for path in (RAW_WIND, RAW_MAG, SNAPSHOT_META, GEOMAG):
        if not path.is_file():
            raise FileNotFoundError(f"Required frozen input is missing: {path.relative_to(ROOT)}")
    metadata = json.loads(SNAPSHOT_META.read_text(encoding="utf-8"))
    if metadata.get("snapshot_id") != "NOAA-RTSW-2026-11-03":
        raise ValueError("Unexpected NOAA RTSW snapshot ID")
    wind_raw = load_snapshot(RAW_WIND, metadata, "plasma")
    mag_raw = load_snapshot(RAW_MAG, metadata, "magnetometer")
    wind_active = select_active(wind_raw)
    mag_active = select_active(mag_raw)
    pairs = pair_active_rows(wind_active, mag_active)
    if not pairs:
        raise ValueError("No exact active source/time matches were found")

    write_json(WIND_ACTIVE, {
        "schema": "signal-atlas.normalized-observations.v1",
        "dataset_id": "DS-RTSW-PLASMA-2026-11-03",
        "source_id": "SRC-145",
        "source_url": WIND_URL,
        "capture_utc": metadata["captured_after_utc"],
        "selection": "Only unchanged source records with active=true; raw response remains preserved separately.",
        "record_count": len(wind_active),
        "records": wind_active,
    })
    write_json(MAG_ACTIVE, {
        "schema": "signal-atlas.normalized-observations.v1",
        "dataset_id": "DS-RTSW-MAG-2026-11-03",
        "source_id": "SRC-146",
        "source_url": MAG_URL,
        "capture_utc": metadata["captured_after_utc"],
        "selection": "Only unchanged source records with active=true; raw response remains preserved separately.",
        "record_count": len(mag_active),
        "records": mag_active,
    })

    joined = {
        "schema": "signal-atlas.derived-observations.v1",
        "atlas_version": "0.8",
        "dataset_id": "DS-RTSW-PAIRED-2026-11-03",
        "source_ids": ["SRC-145", "SRC-146"],
        "time_tag_timezone": "UTC",
        "record_count": len(pairs),
        "window": {"start": pairs[0]["time_tag"], "end": pairs[-1]["time_tag"], "matched_records": len(pairs)},
        "join_method": "Exact join on unchanged time_tag and source; both source records must have active=true.",
        "quality_handling": "Quality fields are retained as reported. This release does not apply undocumented quality thresholds.",
        "records": pairs,
        "limitations": [
            "The frozen endpoint files represent a rolling last-24-hour view, not a long historical archive.",
            "The active spacecraft changes during the sample; spacecraft identity remains visible in every paired row.",
            "The measurements are upstream of Earth. No propagation delay is applied when they are compared with daily geomagnetic context.",
            "The paired records are a descriptive compilation, not a causal analysis, storm forecast, or instrument validation.",
            "Daily summaries cover only the sampled minutes and are explicitly marked partial when they do not contain all 1,440 UTC minutes.",
            "Estimated planetary Kp is a separate three-hour/day product and is included only as completed daily context.",
            "Missing input values remain null; source quality fields are preserved without a new interpretation.",
        ],
    }
    write_json(JOIN_JSON, joined)
    csv_fields = ["time_tag", "source", "active", "proton_speed_km_s", "proton_density_cm3", "proton_temperature_K", "bt_nT", "bx_gsm_nT", "by_gsm_nT", "bz_gsm_nT", "wind_sample_size", "mag_sample_size", "wind_overall_quality", "mag_overall_quality"]
    with JOIN_CSV.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=csv_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(pairs)

    daily_rows = daily_context(pairs, json.loads(GEOMAG.read_text(encoding="utf-8")))
    daily_payload = {
        "schema": "signal-atlas.daily-context.v1",
        "atlas_version": "0.8",
        "dataset_id": "DS-RTSW-DAILY-CONTEXT-2026-11-03",
        "source_ids": ["SRC-145", "SRC-146", "SRC-144"],
        "record_count": len(daily_rows),
        "grouping": "Prefix date of unchanged NOAA time_tag; dates are not shifted.",
        "records": daily_rows,
        "limitations": joined["limitations"],
    }
    write_json(DAILY_JSON, daily_payload)
    daily_fields = ["date_utc", "matched_active_minutes", "expected_minutes_in_utc_day", "coverage_fraction_of_utc_day", "coverage_status", "start_time_tag", "end_time_tag", "active_sources", "median_proton_speed_km_s", "median_proton_density_cm3", "minimum_bz_gsm_nT", "bz_gsm_southward_fraction", "kp_complete_day", "estimated_kp_max"]
    with DAILY_CSV.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=daily_fields, lineterminator="\n")
        writer.writeheader()
        for row in daily_rows:
            stats = row["statistics"]
            kp = row["planetary_kp_context"]
            writer.writerow({
                "date_utc": row["date_utc"],
                "matched_active_minutes": row["matched_active_minutes"],
                "expected_minutes_in_utc_day": row["expected_minutes_in_utc_day"],
                "coverage_fraction_of_utc_day": row["coverage_fraction_of_utc_day"],
                "coverage_status": row["coverage_status"],
                "start_time_tag": row["start_time_tag"],
                "end_time_tag": row["end_time_tag"],
                "active_sources": json.dumps(row["source_sample_counts"], sort_keys=True),
                "median_proton_speed_km_s": stats["proton_speed_km_s"]["median"],
                "median_proton_density_cm3": stats["proton_density_cm3"]["median"],
                "minimum_bz_gsm_nT": stats["bz_gsm_nT"]["min"],
                "bz_gsm_southward_fraction": row["bz_gsm_southward_fraction"],
                "kp_complete_day": kp["complete_day"],
                "estimated_kp_max": kp["max"],
            })

    create_chart(pairs)
    create_explorer(daily_rows, len(pairs), metadata["files"]["plasma"], metadata["files"]["magnetometer"])

    sources = source_records()
    ensure_source_catalog(sources)
    update_docs(sources, len(pairs), daily_rows, metadata)

    provenance_records = [
        {
            "record_id": "PROV-003", "record_type": "captured_source_snapshot", "source_id": "SRC-145", "source_url": WIND_URL,
            "captured_utc": metadata["captured_after_utc"], "raw_file": RAW_WIND.relative_to(ROOT).as_posix(), "raw_sha256": sha256_file(RAW_WIND),
            "record_count": len(wind_raw), "time_tag_start": metadata["files"]["plasma"]["time_tag_start"], "time_tag_end": metadata["files"]["plasma"]["time_tag_end"],
            "active_file": WIND_ACTIVE.relative_to(ROOT).as_posix(), "active_sha256": sha256_file(WIND_ACTIVE), "handling": "Raw response retained byte-for-byte; active=true rows copied without field changes.",
        },
        {
            "record_id": "PROV-004", "record_type": "captured_source_snapshot", "source_id": "SRC-146", "source_url": MAG_URL,
            "captured_utc": metadata["captured_after_utc"], "raw_file": RAW_MAG.relative_to(ROOT).as_posix(), "raw_sha256": sha256_file(RAW_MAG),
            "record_count": len(mag_raw), "time_tag_start": metadata["files"]["magnetometer"]["time_tag_start"], "time_tag_end": metadata["files"]["magnetometer"]["time_tag_end"],
            "active_file": MAG_ACTIVE.relative_to(ROOT).as_posix(), "active_sha256": sha256_file(MAG_ACTIVE), "handling": "Raw response retained byte-for-byte; active=true rows copied without field changes.",
        },
        {
            "record_id": "PROV-005", "record_type": "derived_dataset", "dataset_id": "DS-RTSW-PAIRED-2026-11-03",
            "source_ids": ["SRC-145", "SRC-146"], "input_files": [
                {"path": RAW_WIND.relative_to(ROOT).as_posix(), "sha256": sha256_file(RAW_WIND)},
                {"path": RAW_MAG.relative_to(ROOT).as_posix(), "sha256": sha256_file(RAW_MAG)},
            ], "generator": "tools/build_rtsw_v08.py", "method": joined["join_method"],
            "output_files": [{"path": JOIN_JSON.relative_to(ROOT).as_posix(), "sha256": sha256_file(JOIN_JSON)}, {"path": JOIN_CSV.relative_to(ROOT).as_posix(), "sha256": sha256_file(JOIN_CSV)}, {"path": CHART.relative_to(ROOT).as_posix(), "sha256": sha256_file(CHART)}],
        },
        {
            "record_id": "PROV-006", "record_type": "derived_dataset", "dataset_id": "DS-RTSW-DAILY-CONTEXT-2026-11-03",
            "source_ids": ["SRC-145", "SRC-146", "SRC-144"], "input_files": [
                {"path": JOIN_JSON.relative_to(ROOT).as_posix(), "sha256": sha256_file(JOIN_JSON)},
                {"path": GEOMAG.relative_to(ROOT).as_posix(), "sha256": sha256_file(GEOMAG)},
            ], "generator": "tools/build_rtsw_v08.py", "method": "Group paired active records by the unchanged source date prefix; count coverage against 1,440 UTC minutes; include full-day estimated Kp only when all eight Kp intervals are present.",
            "output_files": [{"path": DAILY_JSON.relative_to(ROOT).as_posix(), "sha256": sha256_file(DAILY_JSON)}, {"path": DAILY_CSV.relative_to(ROOT).as_posix(), "sha256": sha256_file(DAILY_CSV)}],
        },
    ]
    PROVENANCE.parent.mkdir(parents=True, exist_ok=True)
    PROVENANCE.write_text("".join(json.dumps(item, ensure_ascii=False, separators=(",", ":")) + "\n" for item in provenance_records), encoding="utf-8")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if registry.get("atlas_version") not in {"0.7", "0.8"}:
        raise ValueError("Unexpected dataset registry version")
    prior = [item for item in registry.get("datasets", []) if item.get("dataset_id") not in {
        "DS-RTSW-PLASMA-2026-11-03", "DS-RTSW-MAG-2026-11-03", "DS-RTSW-PAIRED-2026-11-03", "DS-RTSW-DAILY-CONTEXT-2026-11-03"
    }]
    def file_ref(path: Path, fmt: str) -> dict:
        return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256_file(path), "format": fmt}
    registry["atlas_version"] = "0.8"
    registry["datasets"] = prior + [
        {
            "dataset_id": "DS-RTSW-PLASMA-2026-11-03", "title": "NOAA SWPC real-time solar-wind proton plasma snapshot", "kind": "observed",
            "data_character": "One-minute in-situ proton speed, density, and temperature; the raw endpoint response includes all available spacecraft.",
            "source_ids": ["SRC-145"], "record_count": len(wind_raw), "active_record_count": len(wind_active),
            "date_start": min(row["time_tag"][:10] for row in wind_raw), "date_end": max(row["time_tag"][:10] for row in wind_raw),
            "units": {"proton_speed": "km/s", "proton_density": "cm^-3", "proton_temperature": "K"},
            "files": [file_ref(RAW_WIND, "json"), file_ref(WIND_ACTIVE, "json"), file_ref(SNAPSHOT_META, "json")], "provenance_record": "PROV-003",
        },
        {
            "dataset_id": "DS-RTSW-MAG-2026-11-03", "title": "NOAA SWPC real-time solar-wind magnetic-field snapshot", "kind": "observed",
            "data_character": "One-minute in-situ interplanetary magnetic-field components; the raw endpoint response includes all available spacecraft.",
            "source_ids": ["SRC-146"], "record_count": len(mag_raw), "active_record_count": len(mag_active),
            "date_start": min(row["time_tag"][:10] for row in mag_raw), "date_end": max(row["time_tag"][:10] for row in mag_raw),
            "units": {"bt": "nT", "bx_gsm": "nT", "by_gsm": "nT", "bz_gsm": "nT"},
            "files": [file_ref(RAW_MAG, "json"), file_ref(MAG_ACTIVE, "json"), file_ref(SNAPSHOT_META, "json")], "provenance_record": "PROV-004",
        },
        {
            "dataset_id": "DS-RTSW-PAIRED-2026-11-03", "title": "NOAA SWPC active-source paired solar-wind series", "kind": "derived",
            "data_character": "Paired 1-minute plasma and magnetic-field records, joined by exact source and time tag.",
            "source_ids": ["SRC-145", "SRC-146"], "record_count": len(pairs),
            "date_start": pairs[0]["time_tag"][:10], "date_end": pairs[-1]["time_tag"][:10],
            "units": {"speed": "km/s", "density": "cm^-3", "temperature": "K", "magnetic_field": "nT"},
            "files": [file_ref(JOIN_JSON, "json"), file_ref(JOIN_CSV, "csv"), file_ref(CHART, "svg")],
            "provenance_record": "PROV-005", "limitations": joined["limitations"],
        },
        {
            "dataset_id": "DS-RTSW-DAILY-CONTEXT-2026-11-03", "title": "Partial UTC-day solar-wind and geomagnetic context", "kind": "derived",
            "data_character": "Coverage-counted daily summaries of the paired series with completed daily Kp shown only as separate context.",
            "source_ids": ["SRC-145", "SRC-146", "SRC-144"], "record_count": len(daily_rows),
            "date_start": daily_rows[0]["date_utc"], "date_end": daily_rows[-1]["date_utc"],
            "units": {"Kp": "estimated dimensionless index; 3-hour intervals"},
            "files": [file_ref(DAILY_JSON, "json"), file_ref(DAILY_CSV, "csv")], "provenance_record": "PROV-006",
            "limitations": ["Every UTC-day bucket in this rolling 24-hour capture is partial.", "Kp is a separate daily context product with a different cadence; no propagation lag is applied."],
        },
    ]
    write_json(REGISTRY, registry)

    # Add the two source cards to the offline FTS index.
    subprocess.check_call([sys.executable, "-B", str(ROOT / "tools" / "build_atlas_index.py")])

    packet = {
        "schema": "signal-atlas-research-packet.v0.8",
        "atlas_version": "0.8",
        "packet_id": "PACKET-NOAA-RTSW-2026-11-03",
        "created_on": "2026-11-03",
        "topic": "NOAA real-time solar-wind plasma and IMF measurements",
        "summary": f"The dated snapshots contain {len(wind_raw)} plasma and {len(mag_raw)} magnetometer records; {len(pairs)} rows pair the selected active spacecraft on exact source and time-tag matches.",
        "dataset_registry": {"path": REGISTRY.relative_to(ROOT).as_posix(), "sha256": sha256_file(REGISTRY)},
        "datasets": [
            {"dataset_id": "DS-RTSW-PLASMA-2026-11-03", "source_ids": ["SRC-145"], "raw_file": RAW_WIND.relative_to(ROOT).as_posix(), "raw_rows": len(wind_raw), "active_rows": len(wind_active)},
            {"dataset_id": "DS-RTSW-MAG-2026-11-03", "source_ids": ["SRC-146"], "raw_file": RAW_MAG.relative_to(ROOT).as_posix(), "raw_rows": len(mag_raw), "active_rows": len(mag_active)},
            {"dataset_id": "DS-RTSW-PAIRED-2026-11-03", "source_ids": ["SRC-145", "SRC-146"], "file": JOIN_JSON.relative_to(ROOT).as_posix(), "rows": len(pairs)},
            {"dataset_id": "DS-RTSW-DAILY-CONTEXT-2026-11-03", "source_ids": ["SRC-145", "SRC-146", "SRC-144"], "file": DAILY_JSON.relative_to(ROOT).as_posix(), "rows": len(daily_rows)},
        ],
        "snapshot": {"captured_before_utc": metadata["captured_before_utc"], "captured_after_utc": metadata["captured_after_utc"], "records": [metadata["files"]["plasma"], metadata["files"]["magnetometer"]]},
        "window": {"start": pairs[0]["time_tag"], "end": pairs[-1]["time_tag"], "paired_records": len(pairs), "daily_context_rows": len(daily_rows)},
        "method": {"selection": "active must be the JSON boolean true", "pairing": "Exact match on source and unchanged time_tag", "daily_grouping": "The source time-tag date prefix; report coverage out of 1,440 minutes and preserve partial days", "kp_context": "Show only complete daily Kp summaries; do not time-shift or interpret as simultaneous causal response"},
        "source_records": [{"id": "SRC-145", "url": WIND_URL}, {"id": "SRC-146", "url": MAG_URL}, {"id": "SRC-144", "url": "https://services.swpc.noaa.gov/text/daily-geomagnetic-indices.txt"}],
        "provenance": {"path": PROVENANCE.relative_to(ROOT).as_posix(), "sha256": sha256_file(PROVENANCE), "records": ["PROV-003", "PROV-004", "PROV-005", "PROV-006"]},
        "interpretation_limits": joined["limitations"],
        "reuse_notes": ["Raw all-spacecraft records are preserved separately from active-selected views.", "Keep measured upstream plasma and field values distinct from estimated Kp and daily derived summaries.", "The one-day capture is a small teaching and exploration sample, not a long historical study."],
    }
    packet["packet_sha256"] = canonical_sha256(packet)
    write_json(PACKET, packet)

    return {
        "plasma_raw_rows": len(wind_raw), "mag_raw_rows": len(mag_raw),
        "plasma_active_rows": len(wind_active), "mag_active_rows": len(mag_active),
        "paired_rows": len(pairs), "daily_context_rows": len(daily_rows),
        "daily_coverage": [row["matched_active_minutes"] for row in daily_rows],
        "source_ids": [source["id"] for source in sources],
        "lineage_baseline_entries": len(json.loads((DATA / "release_v08_lineage.json").read_text(encoding="utf-8"))["baseline_manifest_entries"]),
    }


if __name__ == "__main__":
    print("v0.8 offline data build:", json.dumps(build(), sort_keys=True))
