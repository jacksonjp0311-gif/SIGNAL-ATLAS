"""Focused, offline tests for the v0.8 NOAA solar-wind data integration."""
from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_rtsw_v08 as builder


class SolarWindBuildTests(unittest.TestCase):
    def test_active_filter_requires_json_boolean_true_and_rejects_duplicate_keys(self):
        rows = [
            {"time_tag": "2026-01-01T00:00:00", "source": "ACE", "active": True},
            {"time_tag": "2026-01-01T00:01:00", "source": "ACE", "active": False},
            {"time_tag": "2026-01-01T00:02:00", "source": "ACE", "active": "true"},
        ]
        self.assertEqual(builder.select_active(rows), [rows[0]])
        with self.assertRaisesRegex(ValueError, "duplicate timestamp/source"):
            builder.select_active([rows[0], dict(rows[0])])

    def test_pairing_requires_exact_time_tag_and_same_spacecraft(self):
        wind = [
            {"time_tag": "2026-01-01T00:00:00", "source": "ACE", "active": True, "proton_speed": 400},
            {"time_tag": "2026-01-01T00:01:00", "source": "ACE", "active": True, "proton_speed": 401},
            {"time_tag": "2026-01-01T00:02:00", "source": "ACE", "active": True, "proton_speed": 402},
        ]
        mag = [
            {"time_tag": "2026-01-01T00:00:00", "source": "ACE", "active": True, "bz_gsm": -2},
            {"time_tag": "2026-01-01T00:01:00", "source": "SOLAR1", "active": True, "bz_gsm": -3},
            {"time_tag": "2026-01-01T00:02:01", "source": "ACE", "active": True, "bz_gsm": -4},
        ]
        paired = builder.pair_active_rows(wind, mag)
        self.assertEqual(len(paired), 1)
        self.assertEqual(paired[0]["time_tag"], "2026-01-01T00:00:00")
        self.assertEqual(paired[0]["source"], "ACE")
        self.assertEqual(paired[0]["proton_speed_km_s"], 400)
        self.assertEqual(paired[0]["bz_gsm_nT"], -2)

    def test_incomplete_daily_kp_is_not_summarized_or_filled(self):
        rows = [{
            "time_tag": "2026-01-01T23:59:00", "source": "ACE", "active": True,
            "proton_speed_km_s": None, "proton_density_cm3": 3.0,
            "proton_temperature_K": 1000, "bz_gsm_nT": -1.0,
        }]
        geomag = {"records": [{
            "date": "2026-01-01", "complete_day": False,
            "estimated_planetary_kp_3h": [1.0, None, None, None, None, None, None, None],
        }]}
        daily = builder.daily_context(rows, geomag)[0]
        self.assertEqual(daily["coverage_status"], "partial_utc_day")
        self.assertEqual(daily["matched_active_minutes"], 1)
        self.assertIsNone(daily["statistics"]["proton_speed_km_s"]["mean"])
        self.assertFalse(daily["planetary_kp_context"]["complete_day"])
        self.assertIsNone(daily["planetary_kp_context"]["max"])

    def test_snapshot_loader_rejects_changed_frozen_bytes(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "snapshot.json"
            path.write_text("[]", encoding="utf-8")
            metadata = {"files": {"plasma": {"sha256": "0" * 64}}}
            with self.assertRaisesRegex(ValueError, "hash differs"):
                builder.load_snapshot(path, metadata, "plasma")

    def test_packet_checksum_matches_canonical_packet_content(self):
        path = ROOT / "data" / "packets" / "examples" / "solar-wind-noaa-2026-11-03.v0.8.packet.json"
        packet = json.loads(path.read_text(encoding="utf-8"))
        claimed = packet.pop("packet_sha256")
        self.assertEqual(claimed, builder.canonical_sha256(packet))

    def test_offline_build_is_idempotent_for_release_products(self):
        paths = [
            ROOT / "data" / "sources.jsonl",
            ROOT / "data" / "sources.csv",
            ROOT / "data" / "dataset_registry.json",
            ROOT / "data" / "provenance" / "release_v08_sources.jsonl",
            ROOT / "data" / "datasets" / "noaa_rtsw_active_paired_1m_2026-11-03.json",
            ROOT / "data" / "datasets" / "noaa_rtsw_active_paired_1m_2026-11-03.csv",
            ROOT / "data" / "datasets" / "noaa_rtsw_daily_context_2026-11-03.json",
            ROOT / "data" / "packets" / "examples" / "solar-wind-noaa-2026-11-03.v0.8.packet.json",
            ROOT / "assets" / "solar_wind_rtsw_v08.svg",
            ROOT / "site" / "solar_wind.html",
            ROOT / "site" / "index.html",
            ROOT / "data" / "release_v08_lineage.json",
        ]
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        builder.build()
        after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
