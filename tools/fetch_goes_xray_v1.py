#!/usr/bin/env python3
"""Capture a dated NOAA SWPC GOES X-ray snapshot without transforming raw bytes."""
from __future__ import annotations
import hashlib, json, urllib.request
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
URL = "https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json"
OUT = ROOT / "data" / "datasets"
raw_path = OUT / "noaa_goes_primary_xrays_6hour_2026-11-03.json"
meta_path = OUT / "noaa_goes_primary_xrays_6hour_2026-11-03.metadata.json"
if raw_path.exists() or meta_path.exists():
    raise SystemExit("Snapshot outputs already exist; refusing to overwrite frozen evidence.")
before = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
request = urllib.request.Request(URL, headers={"User-Agent": "Signal-Atlas/1.0 research archive"})
with urllib.request.urlopen(request, timeout=45) as response:
    raw = response.read()
    headers = dict(response.headers.items())
after = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
rows = json.loads(raw.decode("utf-8"))
if not isinstance(rows, list) or not rows:
    raise SystemExit("NOAA endpoint did not return a non-empty JSON list.")
tags = [row.get("time_tag") for row in rows]
if not all(isinstance(tag, str) for tag in tags):
    raise SystemExit("A record is missing a string time_tag.")
raw_path.write_bytes(raw)
meta = {
  "capture_id": "NOAA-GOES-XRS-6H-2026-11-03",
  "source_url": URL,
  "captured_before_utc": before,
  "captured_after_utc": after,
  "http_last_modified": headers.get("Last-Modified"),
  "http_etag": headers.get("ETag"),
  "raw_file": raw_path.relative_to(ROOT).as_posix(),
  "raw_sha256": hashlib.sha256(raw).hexdigest(),
  "byte_count": len(raw),
  "record_count": len(rows),
  "time_tag_start": min(tags),
  "time_tag_end": max(tags),
  "satellites": sorted({row.get("satellite") for row in rows}),
  "energy_channels": sorted({row.get("energy") for row in rows}),
  "record_schema_keys": sorted({key for row in rows for key in row}),
  "transformation": "Raw bytes preserved; JSON parsed only for metadata and validation."
}
meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(meta, indent=2, sort_keys=True))
