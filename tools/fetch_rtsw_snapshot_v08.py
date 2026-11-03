#!/usr/bin/env python3
"""Capture the NOAA SWPC real-time solar-wind JSON inputs for a dated release.

This is the only v0.8 step that uses the network. The offline builder and release
checks consume the captured files, not a live endpoint.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "data" / "datasets"
SOURCES = {
    "plasma": "https://services.swpc.noaa.gov/json/rtsw/rtsw_wind_1m.json",
    "magnetometer": "https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json",
}


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Signal-Atlas-research-collection/0.8"})
    with urlopen(request, timeout=60) as response:
        payload = response.read()
        if response.status != 200:
            raise RuntimeError(f"Unexpected HTTP status {response.status} from {url}")
        return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="replace an existing local snapshot")
    args = parser.parse_args()
    DATASETS.mkdir(parents=True, exist_ok=True)
    paths = {
        "plasma": DATASETS / "noaa_rtsw_wind_1m_2026-11-03.json",
        "magnetometer": DATASETS / "noaa_rtsw_mag_1m_2026-11-03.json",
    }
    if not args.force and any(path.exists() for path in paths.values()):
        raise SystemExit("Snapshot file already exists; use --force only when intentionally replacing this local capture")

    captured_before = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    downloaded: dict[str, tuple[bytes, list[dict]]] = {}
    for name, url in SOURCES.items():
        payload = fetch(url)
        records = json.loads(payload.decode("utf-8"))
        if not isinstance(records, list) or not records or not all(isinstance(row, dict) for row in records):
            raise ValueError(f"{name} endpoint did not return a non-empty JSON object array")
        if not all(isinstance(row.get("time_tag"), str) and isinstance(row.get("source"), str) for row in records):
            raise ValueError(f"{name} endpoint is missing time_tag or source values")
        downloaded[name] = (payload, records)

    file_records = {}
    for name, (payload, records) in downloaded.items():
        path = paths[name]
        path.write_bytes(payload)
        tags = [row["time_tag"] for row in records]
        file_records[name] = {
            "path": path.relative_to(ROOT).as_posix(),
            "source_url": SOURCES[name],
            "sha256": hashlib.sha256(payload).hexdigest(),
            "record_count": len(records),
            "time_tag_start": min(tags),
            "time_tag_end": max(tags),
        }

    captured_after = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    metadata = {
        "schema": "signal-atlas.snapshot-metadata.v1",
        "snapshot_id": "NOAA-RTSW-2026-11-03",
        "captured_before_utc": captured_before,
        "captured_after_utc": captured_after,
        "files": file_records,
        "handling": "Raw bytes are retained unchanged. Endpoint fields are not normalized by the fetch step.",
    }
    (DATASETS / "noaa_rtsw_snapshot_metadata_2026-11-03.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata, sort_keys=True))


if __name__ == "__main__":
    main()
