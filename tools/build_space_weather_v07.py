#!/usr/bin/env python3
"""Build the v0.7 NOAA space-weather collection from frozen local inputs."""
from __future__ import annotations

import csv
import hashlib
import html
import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATASETS = DATA / "datasets"
RAW_GEOMAG = DATASETS / "noaa_daily_geomagnetic_2026-11-03.txt"
F107_PATH = DATASETS / "noaa_f107_30day_2026-11-02.json"
SOURCE_PATH = DATA / "sources.jsonl"
SOURCE_CSV = DATA / "sources.csv"
LINEAGE_PATH = DATA / "release_v07_lineage.json"
GEOMAG_JSON = DATASETS / "noaa_daily_geomagnetic_2026-11-03.json"
JOIN_JSON = DATASETS / "noaa_f107_kp_daily_join_2026-11-03.json"
JOIN_CSV = DATASETS / "noaa_f107_kp_daily_join_2026-11-03.csv"
REGISTRY_JSON = DATA / "dataset_registry.json"
PROVENANCE_JSONL = DATA / "provenance" / "release_v07_sources.jsonl"
PACKET_JSON = DATA / "packets" / "examples" / "space-weather-noaa-2026-11-03.v0.7.packet.json"
CHART_SVG = ROOT / "assets" / "space_weather_f107_kp_v07.svg"
DATA_PAGE = ROOT / "site" / "datasets.html"

NOAA_GEOMAG_URL = "https://services.swpc.noaa.gov/text/daily-geomagnetic-indices.txt"
NOAA_F107_URL = "https://services.swpc.noaa.gov/products/10cm-flux-30-day.json"

EXPECTED_BASELINE_CHANGES = sorted([
    "CHANGELOG.md",
    "README.md",
    "START-HERE.md",
    "THREAD-RESUME-HANDOFF.md",
    "courses/README.md",
    "data/README.md",
    "data/datasets/README.md",
    "data/sources.csv",
    "data/sources.jsonl",
    "docs/INDEX.md",
    "docs/science/README.md",
    "site/index.html",
    "tools/release.py",
    "tools/validate.py",
])


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_sha256(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256_bytes(payload.encode("utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def ensure_lineage() -> dict:
    """Snapshot the complete v0.6 manifest once, before the release script replaces it."""
    if LINEAGE_PATH.exists():
        lineage = json.loads(LINEAGE_PATH.read_text(encoding="utf-8"))
        if lineage.get("baseline_release") != "v0.6":
            raise ValueError("Existing v0.7 lineage does not identify v0.6 as its baseline")
        if lineage.get("expected_modified_baseline_paths") != EXPECTED_BASELINE_CHANGES:
            lineage["expected_modified_baseline_paths"] = EXPECTED_BASELINE_CHANGES
            write_json(LINEAGE_PATH, lineage)
        return lineage
    manifest_path = ROOT / "MANIFEST.sha256"
    if not manifest_path.is_file():
        raise FileNotFoundError("The v0.6 MANIFEST.sha256 baseline is required")
    entries = []
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        entries.append({"path": relative.replace("\\", "/"), "sha256": digest})
    if not entries:
        raise ValueError("The v0.6 baseline manifest is empty")
    lineage = {
        "schema": "signal-atlas.release-lineage.v1",
        "baseline_release": "v0.6",
        "baseline_manifest_sha256": sha256_file(manifest_path),
        "baseline_manifest_entries": entries,
        "expected_modified_baseline_paths": EXPECTED_BASELINE_CHANGES,
        "preservation_rule": "Every baseline path remains in v0.7. Baseline file hashes stay unchanged except for the explicitly listed integration files.",
    }
    write_json(LINEAGE_PATH, lineage)
    return lineage


def v07_source_record() -> dict:
    return {
        "id": "SRC-144",
        "title": "NOAA SWPC daily geomagnetic indices, 30-day product",
        "publisher": "NOAA Space Weather Prediction Center",
        "country": "International",
        "domain": "science",
        "url": NOAA_GEOMAG_URL,
        "summary": "Rolling daily geomagnetic data with middle-latitude and high-latitude observatory values plus estimated planetary A and eight three-hour Kp values. A dated text snapshot is retained with this release.",
        "source_type": "official observation product",
        "time_scope": "2026-10-05 through 2026-11-03; 2026-11-03 is partial",
        "rights": "No separate reuse assessment was made for this data addition; original NOAA SWPC URL is retained.",
        "review_status": "operational data snapshot included",
        "added_at": "2026-11-03",
        "topics": ["space weather", "geomagnetic activity", "planetary Kp", "observations", "time series"],
        "snapshot_status": "dataset-snapshot-included",
        "language": "en",
        "checked_at": "2026-11-03",
        "research_batch": "2026-11-03-A",
    }


def load_source_records() -> list[dict]:
    return [
        json.loads(line)
        for line in SOURCE_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def ensure_source_record() -> dict:
    rows = load_source_records()
    target = v07_source_record()
    matches = [row for row in rows if row.get("id") == target["id"]]
    if matches:
        if matches[0] != target:
            lines = SOURCE_PATH.read_text(encoding="utf-8").splitlines(keepends=True)
            for index, line in enumerate(lines):
                if line.strip() and json.loads(line).get("id") == target["id"]:
                    newline = "\r\n" if line.endswith("\r\n") else "\n"
                    lines[index] = json.dumps(target, ensure_ascii=False, separators=(",", ":")) + newline
                    break
            SOURCE_PATH.write_text("".join(lines), encoding="utf-8")
        return target
    numeric_ids = [
        int(row["id"].split("-")[1])
        for row in rows
        if re.fullmatch(r"SRC-\d+", row.get("id", ""))
    ]
    if numeric_ids and max(numeric_ids) != 143:
        raise ValueError(f"Expected the catalog to end at SRC-143; found SRC-{max(numeric_ids):03d}")
    with SOURCE_PATH.open("a", encoding="utf-8", newline="") as stream:
        stream.write(json.dumps(target, ensure_ascii=False, separators=(",", ":")) + "\n")
    return target


def ensure_source_csv_record(source: dict) -> None:
    with SOURCE_CSV.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        existing_rows = list(reader)
    if not fields or "id" not in fields:
        raise ValueError("sources.csv has no recognized header")
    row = dict(source)
    row["topics"] = json.dumps(source.get("topics", []), ensure_ascii=False)
    existing = next((item for item in existing_rows if item.get("id") == source["id"]), None)
    if existing and all(existing.get(key, "") == str(row.get(key, "")) for key in fields):
        return
    if existing:
        if not existing_rows or existing_rows[-1].get("id") != source["id"]:
            raise ValueError("SRC-144 is not the final row in sources.csv; refusing to rewrite unrelated rows")
        import io
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writerow(row)
        lines = SOURCE_CSV.read_text(encoding="utf-8").splitlines(keepends=True)
        lines[-1] = buffer.getvalue()
        SOURCE_CSV.write_text("".join(lines), encoding="utf-8")
        return
    with SOURCE_CSV.open("a", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writerow(row)


def _missing_as_none(value: str, converter):
    parsed = converter(value)
    return None if parsed == -1 else parsed


def parse_daily_geomagnetic(text: str) -> dict:
    issue_match = re.search(r":Issued:\s*(\d{4}) UT (\d{2} \w{3} \d{4})", text)
    if not issue_match:
        raise ValueError("Missing NOAA issue timestamp")
    issue_dt = datetime.strptime(issue_match.group(1) + " " + issue_match.group(2), "%H%M %d %b %Y")
    records = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        tokens = []
        for token in line.split():
            if re.fullmatch(r"(?:-1){2,}", token):
                tokens.extend(["-1"] * (len(token) // 2))
            else:
                tokens.append(token)
        if not tokens or not re.fullmatch(r"\d{4}", tokens[0]):
            continue
        if len(tokens) != 30:
            raise ValueError(f"Line {line_number}: expected 30 columns, found {len(tokens)}")
        year, month, day = map(int, tokens[:3])
        date = f"{year:04d}-{month:02d}-{day:02d}"
        middle_a = _missing_as_none(tokens[3], int)
        middle_k = [_missing_as_none(value, int) for value in tokens[4:12]]
        high_a = _missing_as_none(tokens[12], int)
        high_k = [_missing_as_none(value, int) for value in tokens[13:21]]
        planetary_a = _missing_as_none(tokens[21], int)
        planetary_kp = [_missing_as_none(value, float) for value in tokens[22:30]]
        valid_kp = [value for value in planetary_kp if value is not None]
        complete = len(valid_kp) == 8
        records.append({
            "date": date,
            "middle_latitude_a": middle_a,
            "middle_latitude_k_3h": middle_k,
            "high_latitude_a": high_a,
            "high_latitude_k_3h": high_k,
            "estimated_planetary_a": planetary_a,
            "estimated_planetary_kp_3h": planetary_kp,
            "valid_kp_intervals": len(valid_kp),
            "complete_day": complete,
            "daily_kp_max": max(valid_kp) if complete else None,
            "daily_kp_mean": round(sum(valid_kp) / 8, 4) if complete else None,
        })
    if not records:
        raise ValueError("No daily geomagnetic records found")
    if len({row["date"] for row in records}) != len(records):
        raise ValueError("Duplicate geomagnetic dates")
    return {
        "schema": "signal-atlas.noaa-daily-geomagnetic.v1",
        "source_id": "SRC-144",
        "source_url": NOAA_GEOMAG_URL,
        "issued_utc": issue_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "captured_on": "2026-11-03",
        "input_snapshot": RAW_GEOMAG.relative_to(ROOT).as_posix(),
        "input_sha256": sha256_bytes(text.encode("utf-8")),
        "missing_value_rule": "The source sentinel -1 is represented as JSON null; it is not a measured negative index.",
        "interval_count_per_day": 8,
        "records": records,
        "record_count": len(records),
        "complete_day_count": sum(1 for row in records if row["complete_day"]),
        "partial_day_count": sum(1 for row in records if not row["complete_day"]),
    }


def read_f107() -> list[dict]:
    value = json.loads(F107_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError("F10.7 snapshot must be a JSON list")
    points = []
    for row in value:
        if "time_tag" not in row or "flux" not in row:
            raise ValueError("F10.7 row is missing time_tag or flux")
        date = str(row["time_tag"])[:10]
        flux = float(row["flux"])
        points.append({
            "date": date,
            "time_tag": row["time_tag"],
            "value_sfu": int(flux) if flux.is_integer() else flux,
        })
    if len({row["date"] for row in points}) != len(points):
        raise ValueError("Duplicate F10.7 dates")
    return sorted(points, key=lambda row: row["date"])


def join_daily_data(geomag: dict, f107_points: list[dict]) -> tuple[list[dict], dict]:
    solar_by_date = {row["date"]: row for row in f107_points}
    joined = []
    for row in geomag["records"]:
        if not row["complete_day"] or row["date"] not in solar_by_date:
            continue
        solar = solar_by_date[row["date"]]
        kp_values = row["estimated_planetary_kp_3h"]
        kp_max = max(kp_values)
        kp_mean = round(sum(kp_values) / 8, 4)
        joined.append({
            "date": row["date"],
            "f107_time_tag": solar["time_tag"],
            "f107_sfu": solar["value_sfu"],
            "planetary_a": row["estimated_planetary_a"],
            "planetary_kp_3h": kp_values,
            "planetary_kp_mean": kp_mean,
            "planetary_kp_max": kp_max,
            "complete_kp_intervals": 8,
            "kp_ge_5": kp_max >= 5.0,
        })
    joined.sort(key=lambda row: row["date"])
    if not joined:
        raise ValueError("No complete date-matched records found")
    if len({row["date"] for row in joined}) != len(joined):
        raise ValueError("Duplicate join dates")
    stats = {
        "date_start": joined[0]["date"],
        "date_end": joined[-1]["date"],
        "record_count": len(joined),
        "f107_min_sfu": min(row["f107_sfu"] for row in joined),
        "f107_max_sfu": max(row["f107_sfu"] for row in joined),
        "planetary_kp_max": max(row["planetary_kp_max"] for row in joined),
        "planetary_kp_peak_dates": [
            row["date"] for row in joined
            if row["planetary_kp_max"] == max(item["planetary_kp_max"] for item in joined)
        ],
        "days_kp_ge_5": sum(1 for row in joined if row["kp_ge_5"]),
    }
    return joined, stats


def _x(index: int, count: int, left: float, right: float) -> float:
    return left if count <= 1 else left + index * (right - left) / (count - 1)


def render_chart(joined: list[dict], stats: dict) -> str:
    width, height = 1120, 560
    left, right = 100.0, 1050.0
    top1, bottom1 = 110.0, 235.0
    top2, bottom2 = 325.0, 455.0
    flux_values = [float(row["f107_sfu"]) for row in joined]
    flux_min, flux_max = min(flux_values), max(flux_values)
    pad = max((flux_max - flux_min) * 0.12, 2.0)
    f_low, f_high = flux_min - pad, flux_max + pad

    def y_flux(value: float) -> float:
        return bottom1 - (value - f_low) * (bottom1 - top1) / (f_high - f_low)

    def y_kp(value: float) -> float:
        return bottom2 - value * (bottom2 - top2) / 9.0

    points_flux = [
        (_x(i, len(joined), left, right), y_flux(float(row["f107_sfu"])))
        for i, row in enumerate(joined)
    ]
    points_kp = [
        (_x(i, len(joined), left, right), y_kp(float(row["planetary_kp_max"])))
        for i, row in enumerate(joined)
    ]

    def path(points: list[tuple[float, float]]) -> str:
        return " ".join(("M" if index == 0 else "L") + f" {x:.1f} {y:.1f}" for index, (x, y) in enumerate(points))

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Solar radio flux and estimated planetary Kp, daily join</title>',
        '<desc id="desc">Two separate panels show NOAA F10.7 solar radio flux in solar flux units and the daily maximum estimated planetary Kp over 29 complete matched dates. Separate scales prevent the units from being conflated.</desc>',
        '<rect width="100%" height="100%" rx="24" fill="#0b1220"/>',
        '<text x="54" y="47" fill="#f5f7fb" font-size="24" font-family="Segoe UI, sans-serif" font-weight="700">NOAA space-weather observations · 29 matched days</text>',
        '<text x="54" y="75" fill="#9eb1c9" font-size="14" font-family="Segoe UI, sans-serif">Date-keyed comparison · descriptive only · not a causal model</text>',
        '<text x="56" y="104" fill="#48d9e8" font-size="16" font-family="Segoe UI, sans-serif" font-weight="700">F10.7 solar radio flux (sfu)</text>',
        '<text x="56" y="305" fill="#ffbd59" font-size="16" font-family="Segoe UI, sans-serif" font-weight="700">Estimated planetary Kp daily maximum (0–9)</text>',
    ]
    for tick in range(4):
        value = f_low + (f_high - f_low) * tick / 3
        y = y_flux(value)
        lines.append(f'<line x1="{left:.1f}" x2="{right:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="#233047" stroke-width="1"/>')
        lines.append(f'<text x="{left - 12:.1f}" y="{y + 4:.1f}" fill="#9eb1c9" font-size="12" text-anchor="end" font-family="Segoe UI, sans-serif">{value:.0f}</text>')
    for tick in (0, 3, 5, 7, 9):
        y = y_kp(tick)
        lines.append(f'<line x1="{left:.1f}" x2="{right:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="#233047" stroke-width="1"/>')
        lines.append(f'<text x="{left - 12:.1f}" y="{y + 4:.1f}" fill="#9eb1c9" font-size="12" text-anchor="end" font-family="Segoe UI, sans-serif">{tick}</text>')
    threshold_y = y_kp(5)
    lines.append(f'<line x1="{left:.1f}" x2="{right:.1f}" y1="{threshold_y:.1f}" y2="{threshold_y:.1f}" stroke="#ff7b72" stroke-width="1.5" stroke-dasharray="7 6"/>')
    lines.append(f'<text x="{right - 3:.1f}" y="{threshold_y - 7:.1f}" fill="#ff9d95" font-size="12" text-anchor="end" font-family="Segoe UI, sans-serif">Kp 5 reference</text>')
    lines.append(f'<path d="{path(points_flux)}" fill="none" stroke="#48d9e8" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
    lines.append(f'<path d="{path(points_kp)}" fill="none" stroke="#ffbd59" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
    for x, y in points_flux:
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="#48d9e8"/>')
    for x, y in points_kp:
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="#ffbd59"/>')
    tick_indices = sorted({0, len(joined) // 4, len(joined) // 2, (3 * len(joined)) // 4, len(joined) - 1})
    for index in tick_indices:
        x = _x(index, len(joined), left, right)
        label = joined[index]["date"][5:]
        lines.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{bottom2:.1f}" y2="{bottom2 + 5:.1f}" stroke="#74869e"/>')
        lines.append(f'<text x="{x:.1f}" y="{bottom2 + 24:.1f}" fill="#9eb1c9" font-size="12" text-anchor="middle" font-family="Segoe UI, sans-serif">{label}</text>')
    lines.append(f'<text x="54" y="520" fill="#9eb1c9" font-size="12" font-family="Segoe UI, sans-serif">Window: {stats["date_start"]} to {stats["date_end"]} · source Kp values are estimated three-hour indices · partial 2026-11-03 excluded</text>')
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def render_data_page(joined: list[dict], stats: dict) -> str:
    table_rows = []
    for row in joined:
        event_label = "Kp 5+ reached" if row["kp_ge_5"] else "below 5"
        table_rows.append(
            '<tr data-date="' + html.escape(row["date"]) + '">'
            f'<td>{html.escape(row["date"])}</td>'
            f'<td>{row["f107_sfu"]}</td>'
            f'<td>{row["planetary_kp_mean"]:.2f}</td>'
            f'<td>{row["planetary_kp_max"]:.2f}</td>'
            f'<td>{event_label}</td></tr>'
        )
    rows_html = "\n".join(table_rows)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Signal Atlas — Data Explorer</title>
<style>
:root{{--bg:#0b1220;--panel:#131e30;--ink:#f5f7fb;--muted:#a6b7cc;--cyan:#48d9e8;--gold:#ffbd59;--line:#27364b}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Segoe UI,Arial,sans-serif}}
main{{max-width:1180px;margin:auto;padding:28px}}a{{color:var(--cyan)}}header{{display:flex;gap:20px;align-items:center;justify-content:space-between;flex-wrap:wrap}}
.kicker{{color:var(--gold);text-transform:uppercase;letter-spacing:.12em;font-size:.8rem}}h1{{font-size:clamp(2rem,5vw,3.2rem);line-height:1.1;margin:.25rem 0}}p{{max-width:80ch;color:var(--muted)}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px;margin:18px 0}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}}.stat{{padding:14px;background:#0e1726;border-radius:12px}}.stat strong{{display:block;color:var(--cyan);font-size:1.3rem}}
img{{display:block;width:100%;height:auto;border-radius:12px}}.table-wrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;min-width:620px}}th,td{{padding:9px 12px;border-bottom:1px solid var(--line);text-align:left}}th{{color:var(--cyan);position:sticky;top:0;background:var(--panel)}}input{{max-width:420px;width:100%;padding:10px 12px;border-radius:8px;border:1px solid var(--line);background:#0e1726;color:var(--ink)}}
.links{{display:flex;gap:12px;flex-wrap:wrap}}.note{{border-left:3px solid var(--gold);padding:10px 14px;color:var(--muted)}}.back{{white-space:nowrap}}
</style>
</head>
<body>
<main>
<header><div><div class="kicker">Signal Atlas · observed data collection · v0.7</div><h1>Data Explorer</h1><p>Follow two public NOAA measurement feeds from frozen input files through a date-keyed table, a teaching chart, and a machine-readable research packet.</p></div><a class="back" href="index.html">Back to the Atlas</a></header>
<section class="card stats" aria-label="Dataset summary">
<div class="stat"><strong>{stats["record_count"]}</strong>complete matched dates</div>
<div class="stat"><strong>{stats["date_start"]}</strong>first joined date</div>
<div class="stat"><strong>{stats["date_end"]}</strong>last joined date</div>
<div class="stat"><strong>{stats["days_kp_ge_5"]}</strong>days with estimated daily Kp maximum at or above 5</div>
</section>
<section class="card"><h2>Compare without mixing scales</h2><p>F10.7 is shown in solar flux units; planetary Kp is an estimated geomagnetic index. Separate panels retain their different units and meanings.</p><img src="../assets/space_weather_f107_kp_v07.svg" alt="Two-panel chart comparing daily NOAA F10.7 solar flux and estimated planetary Kp maximum for matched dates."></section>
<section class="card"><h2>Daily joined values</h2><label for="filter">Filter rows by date or event</label><p><input id="filter" type="search" placeholder="For example: 2026-10-10 or Kp 5+"></p>
<div class="table-wrap"><table><caption>Daily date-keyed NOAA SWPC F10.7 and estimated planetary Kp summary</caption><thead><tr><th scope="col">Date label</th><th scope="col">F10.7 (sfu)</th><th scope="col">Kp mean</th><th scope="col">Kp max</th><th scope="col">Threshold summary</th></tr></thead><tbody>{rows_html}</tbody></table></div></section>
<section class="card"><h2>Open the underlying collection</h2><div class="links">
<a href="../data/dataset_registry.json">Dataset registry (JSON)</a>
<a href="../data/datasets/noaa_f107_30day_2026-11-02.json">F10.7 raw snapshot (JSON)</a>
<a href="../data/datasets/noaa_daily_geomagnetic_2026-11-03.txt">Geomagnetic raw snapshot (TXT)</a>
<a href="../data/datasets/noaa_daily_geomagnetic_2026-11-03.json">Geomagnetic normalized rows (JSON)</a>
<a href="../data/datasets/noaa_f107_kp_daily_join_2026-11-03.json">Joined values (JSON)</a>
<a href="../data/datasets/noaa_f107_kp_daily_join_2026-11-03.csv">Joined values (CSV)</a>
<a href="../data/packets/examples/space-weather-noaa-2026-11-03.v0.7.packet.json">AI research packet</a>
<a href="../docs/science/08_space_weather_observations.md">Method and interpretation guide</a>
<a href="../courses/27_space_weather_data_join.md">Guided lesson</a>
</div></section>
<section class="card note"><strong>How to read this page.</strong> The joined window uses the date prefix from each F10.7 time tag and the date printed in the geomagnetic file. It does not shift timestamps or imply the two measurements occurred at the same instant. The current-day geomagnetic row is partial and excluded from the complete daily join. Co-variation is descriptive; this package does not claim that solar radio flux caused a geomagnetic change.</section>
<footer><p>Original data products: <a href="https://services.swpc.noaa.gov/products/10cm-flux-30-day.json">NOAA SWPC F10.7 feed</a> and <a href="https://services.swpc.noaa.gov/text/daily-geomagnetic-indices.txt">NOAA SWPC daily geomagnetic feed</a>. This page is generated offline by the v0.7 build tool.</p></footer>
</main>
<script>
const filter=document.getElementById("filter");
filter.addEventListener("input",()=>{{const q=filter.value.toLowerCase();for(const row of document.querySelectorAll("tbody tr"))row.hidden=!row.textContent.toLowerCase().includes(q)}});
</script>
</body>
</html>
"""


def _write_csv(joined: list[dict]) -> None:
    fields = ["date", "f107_sfu", "planetary_a", "planetary_kp_mean", "planetary_kp_max", "complete_kp_intervals", "kp_ge_5"]
    with JOIN_CSV.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in joined:
            writer.writerow({key: row[key] for key in fields})


def _write_provenance(raw_sha: str, parsed_sha: str, join_sha: str, csv_sha: str, chart_sha: str) -> None:
    source_record = {
        "record_id": "PROV-001",
        "record_type": "captured_source_snapshot",
        "source_id": "SRC-144",
        "source_url": NOAA_GEOMAG_URL,
        "issued_utc": "2026-11-03T03:30:00Z",
        "captured_on": "2026-11-03",
        "raw_file": RAW_GEOMAG.relative_to(ROOT).as_posix(),
        "raw_sha256": raw_sha,
        "normalized_file": GEOMAG_JSON.relative_to(ROOT).as_posix(),
        "normalized_sha256": parsed_sha,
        "handling": "Raw NOAA text is preserved. The -1 source sentinel is null in normalized JSON; the final current-day row remains partial.",
    }
    derived_record = {
        "record_id": "PROV-002",
        "record_type": "derived_dataset",
        "dataset_id": "DS-SPACEWEATHER-JOIN-2026-11-03",
        "source_ids": ["SRC-116", "SRC-144"],
        "input_files": [
            {"path": F107_PATH.relative_to(ROOT).as_posix(), "sha256": sha256_file(F107_PATH)},
            {"path": RAW_GEOMAG.relative_to(ROOT).as_posix(), "sha256": raw_sha},
        ],
        "generator": "tools/build_space_weather_v07.py",
        "method": "Match the F10.7 time_tag date prefix to the geomagnetic row date; retain only days with a flux value and all eight planetary Kp intervals; compute daily Kp max and arithmetic mean; do not time-shift or infer causality.",
        "output_files": [
            {"path": JOIN_JSON.relative_to(ROOT).as_posix(), "sha256": join_sha},
            {"path": JOIN_CSV.relative_to(ROOT).as_posix(), "sha256": csv_sha},
            {"path": CHART_SVG.relative_to(ROOT).as_posix(), "sha256": chart_sha},
        ],
    }
    PROVENANCE_JSONL.parent.mkdir(parents=True, exist_ok=True)
    PROVENANCE_JSONL.write_text(
        json.dumps(source_record, ensure_ascii=False, separators=(",", ":")) + "\n"
        + json.dumps(derived_record, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def _record_count(value: object):
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        for key in ("records", "samples", "observations", "data"):
            if isinstance(value.get(key), list):
                return len(value[key])
    return None


def build() -> dict:
    ensure_lineage()
    source = ensure_source_record()
    ensure_source_csv_record(source)
    raw_text = RAW_GEOMAG.read_text(encoding="utf-8")
    raw_sha = sha256_bytes(raw_text.encode("utf-8"))
    geomag = parse_daily_geomagnetic(raw_text)
    write_json(GEOMAG_JSON, geomag)
    f107_points = read_f107()
    joined, stats = join_daily_data(geomag, f107_points)

    join_payload = {
        "schema": "signal-atlas.daily-space-weather-join.v1",
        "atlas_version": "0.7",
        "dataset_id": "DS-SPACEWEATHER-JOIN-2026-11-03",
        "source_ids": ["SRC-116", "SRC-144"],
        "match_rule": "Exact YYYY-MM-DD date-label join: first ten characters of F10.7 time_tag matched to geomagnetic row date; no timestamp shifting.",
        "aggregation": "For complete geomagnetic days, compute max and arithmetic mean of the eight estimated planetary Kp values. Keep the original eight values.",
        "units": {"f107_sfu": "solar flux unit (sfu)", "planetary_kp": "estimated planetary Kp index, dimensionless scale"},
        "window": {"start": stats["date_start"], "end": stats["date_end"], "row_count": stats["record_count"]},
        "summary": stats,
        "limitations": [
            "This is a date-label join, not an assertion that daily measurements occurred at the same instant.",
            "The F10.7 time tags do not include a timezone suffix in the retained v0.6 snapshot; no timezone conversion is applied.",
            "The 2026-11-03 geomagnetic row is incomplete and is not included in the daily comparison.",
            "Planetary Kp is estimated and each daily maximum summarizes eight three-hour values.",
            "The short observational window supports descriptive exploration only, not causal attribution or a solar-activity forecast.",
        ],
        "records": joined,
    }
    write_json(JOIN_JSON, join_payload)
    _write_csv(joined)
    chart = render_chart(joined, stats)
    CHART_SVG.write_text(chart, encoding="utf-8")
    page = render_data_page(joined, stats)
    DATA_PAGE.write_text(page, encoding="utf-8")

    site_index_path = ROOT / "site" / "index.html"
    site_index = site_index_path.read_text(encoding="utf-8")
    nav_anchor = '<a href="topic-map.html" class="navbtn" style="text-decoration:none">'
    data_link = '<a href="datasets.html" class="navbtn" style="text-decoration:none">DATA / OBSERVATIONS</a>'
    if 'href="datasets.html"' not in site_index:
        if nav_anchor not in site_index:
            raise ValueError("Could not find the topic map navigation link")
        site_index = site_index.replace(nav_anchor, data_link + nav_anchor, 1)
        site_index_path.write_text(site_index, encoding="utf-8")

    parsed_sha = sha256_file(GEOMAG_JSON)
    join_sha = sha256_file(JOIN_JSON)
    csv_sha = sha256_file(JOIN_CSV)
    chart_sha = sha256_file(CHART_SVG)
    _write_provenance(raw_sha, parsed_sha, join_sha, csv_sha, chart_sha)
    synthetic_path = DATA / "experiments" / "frequency_stability_v06.json"
    synthetic_value = json.loads(synthetic_path.read_text(encoding="utf-8"))
    registry = {
        "schema": "signal-atlas.dataset-registry.v1",
        "atlas_version": "0.7",
        "scope": "Canonical observed, derived, and synthetic series highlighted in the Atlas data pipeline; this does not reclassify the source catalog as a dataset list.",
        "datasets": [
            {
                "dataset_id": "DS-F107-2026-11-02",
                "title": "NOAA 10.7 cm solar radio flux, dated 30-day snapshot",
                "kind": "observed",
                "source_ids": ["SRC-116"],
                "date_start": min(row["date"] for row in f107_points),
                "date_end": max(row["date"] for row in f107_points),
                "record_count": len(f107_points),
                "value": "F10.7 flux",
                "units": "solar flux units (sfu)",
                "files": [{"path": F107_PATH.relative_to(ROOT).as_posix(), "sha256": sha256_file(F107_PATH), "format": "json"}],
                "provenance_record": "Retained in v0.6; see the v0.6 dataset notes.",
            },
            {
                "dataset_id": "DS-GEOMAG-2026-11-03",
                "title": "NOAA SWPC daily geomagnetic indices, dated 30-day snapshot",
                "kind": "observed",
                "data_character": "The planetary Kp values are NOAA estimates computed from ground-magnetometer data.",
                "source_ids": ["SRC-144"],
                "date_start": geomag["records"][0]["date"],
                "date_end": geomag["records"][-1]["date"],
                "record_count": geomag["record_count"],
                "complete_day_count": geomag["complete_day_count"],
                "partial_day_count": geomag["partial_day_count"],
                "value": "middle/high latitude A and K, estimated planetary A and eight Kp values per date",
                "units": "indices; Kp is dimensionless",
                "files": [
                    {"path": RAW_GEOMAG.relative_to(ROOT).as_posix(), "sha256": raw_sha, "format": "text"},
                    {"path": GEOMAG_JSON.relative_to(ROOT).as_posix(), "sha256": parsed_sha, "format": "json"},
                ],
                "provenance_record": "PROV-001",
            },
            {
                "dataset_id": "DS-SPACEWEATHER-JOIN-2026-11-03",
                "title": "Date-keyed F10.7 and estimated planetary Kp daily comparison",
                "kind": "derived",
                "data_character": "Date-keyed combination and daily summaries derived from the two observed inputs.",
                "source_ids": ["SRC-116", "SRC-144"],
                "date_start": stats["date_start"],
                "date_end": stats["date_end"],
                "record_count": stats["record_count"],
                "value": "F10.7, planetary A, eight three-hour estimated planetary Kp values, daily Kp mean and max",
                "units": {"F10.7": "sfu", "Kp": "dimensionless index"},
                "files": [
                    {"path": JOIN_JSON.relative_to(ROOT).as_posix(), "sha256": join_sha, "format": "json"},
                    {"path": JOIN_CSV.relative_to(ROOT).as_posix(), "sha256": csv_sha, "format": "csv"},
                    {"path": CHART_SVG.relative_to(ROOT).as_posix(), "sha256": chart_sha, "format": "svg"},
                ],
                "provenance_record": "PROV-002",
                "limitations": join_payload["limitations"],
            },
            {
                "dataset_id": "DS-SYNTHETIC-FREQUENCY-STABILITY-V06",
                "title": "Frequency stability teaching series",
                "kind": "synthetic",
                "data_character": "Teaching series only; not field measurements.",
                "source_ids": [],
                "record_count": _record_count(synthetic_value),
                "units": "fractional frequency",
                "files": [{
                    "path": synthetic_path.relative_to(ROOT).as_posix(),
                    "sha256": sha256_file(synthetic_path),
                    "format": "json",
                }],
                "provenance_record": "Authored teaching data retained from v0.6.",
            },
        ],
    }
    write_json(REGISTRY_JSON, registry)
    _write_provenance(raw_sha, parsed_sha, join_sha, csv_sha, chart_sha)
    provenance_sha = sha256_file(PROVENANCE_JSONL)
    packet = {
        "schema": "signal-atlas-research-packet.v0.7",
        "atlas_version": "0.7",
        "packet_id": "PACKET-SWPC-SPACEWEATHER-2026-11-03",
        "created_on": "2026-11-03",
        "topic": "NOAA F10.7 solar radio flux and estimated planetary Kp",
        "summary": f"A date-keyed descriptive join contains {stats['record_count']} complete daily matches from {stats['date_start']} through {stats['date_end']}.",
        "dataset_registry": {
            "path": REGISTRY_JSON.relative_to(ROOT).as_posix(),
            "sha256": sha256_file(REGISTRY_JSON),
        },
        "datasets": [
            {"dataset_id": "DS-F107-2026-11-02", "source_ids": ["SRC-116"], "file": F107_PATH.relative_to(ROOT).as_posix(), "rows": len(f107_points)},
            {"dataset_id": "DS-GEOMAG-2026-11-03", "source_ids": ["SRC-144"], "file": GEOMAG_JSON.relative_to(ROOT).as_posix(), "rows": geomag["record_count"]},
            {"dataset_id": "DS-SPACEWEATHER-JOIN-2026-11-03", "source_ids": ["SRC-116", "SRC-144"], "file": JOIN_JSON.relative_to(ROOT).as_posix(), "rows": stats["record_count"]},
        ],
        "window": {"start": stats["date_start"], "end": stats["date_end"], "matched_days": stats["record_count"]},
        "computed_observations": {
            "f107_min_sfu": stats["f107_min_sfu"],
            "f107_max_sfu": stats["f107_max_sfu"],
            "planetary_kp_daily_max": stats["planetary_kp_max"],
            "dates_at_planetary_kp_max": stats["planetary_kp_peak_dates"],
            "days_with_planetary_kp_max_at_least_5": stats["days_kp_ge_5"],
        },
        "method": {
            "join_key": "F10.7 time_tag date prefix (YYYY-MM-DD) equals geomagnetic row date.",
            "incomplete_rows": "Excluded from the complete daily join; retained in normalized raw geomagnetic data.",
            "daily_summary": "Maximum and arithmetic mean of the eight estimated planetary Kp values.",
        },
        "source_records": [
            {"id": "SRC-116", "url": NOAA_F107_URL},
            {"id": "SRC-144", "url": NOAA_GEOMAG_URL},
        ],
        "provenance": {
            "path": PROVENANCE_JSONL.relative_to(ROOT).as_posix(),
            "sha256": provenance_sha,
            "records": ["PROV-001", "PROV-002"],
        },
        "interpretation_limits": join_payload["limitations"],
        "reuse_notes": [
            "Keep estimated planetary Kp distinct from the F10.7 radio-flux value; their scales and physical meanings differ.",
            "Describe this short window; do not infer causal effects or make a forecast from this packet.",
            "This collection is a dated sample, not the complete NOAA historical archive.",
        ],
    }
    packet["packet_sha256"] = canonical_sha256(packet)
    write_json(PACKET_JSON, packet)
    return {
        "geomagnetic_rows": geomag["record_count"],
        "complete_geomagnetic_days": geomag["complete_day_count"],
        "partial_geomagnetic_days": geomag["partial_day_count"],
        "joined_rows": stats["record_count"],
        "window": f"{stats['date_start']}..{stats['date_end']}",
        "days_kp_ge_5": stats["days_kp_ge_5"],
        "source_id": source["id"],
    }


if __name__ == "__main__":
    print("v0.7 offline data build:", json.dumps(build(), sort_keys=True))
