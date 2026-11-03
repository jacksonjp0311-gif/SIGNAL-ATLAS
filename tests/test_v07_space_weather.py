import json
import hashlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_space_weather_v07 as builder


class SpaceWeatherBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw_text = (ROOT / "data" / "datasets" / "noaa_daily_geomagnetic_2026-11-03.txt").read_text(encoding="utf-8")
        cls.geomag = builder.parse_daily_geomagnetic(cls.raw_text)
        cls.f107 = builder.read_f107()

    def test_daily_parser_preserves_complete_and_partial_rows(self):
        self.assertEqual(self.geomag["issued_utc"], "2026-11-03T03:30:00Z")
        self.assertEqual(self.geomag["record_count"], 30)
        self.assertEqual(self.geomag["complete_day_count"], 29)
        self.assertEqual(self.geomag["partial_day_count"], 1)
        self.assertEqual(self.geomag["records"][-1]["date"], "2026-11-03")
        self.assertFalse(self.geomag["records"][-1]["complete_day"])
        self.assertEqual(self.geomag["records"][-1]["estimated_planetary_kp_3h"], [0.67, None, None, None, None, None, None, None])

    def test_daily_parser_rejects_a_truncated_record(self):
        first_data = next(line for line in self.raw_text.splitlines() if line.startswith("2026 "))
        malformed = self.raw_text.replace(first_data, " ".join(first_data.split()[:-1]), 1)
        with self.assertRaisesRegex(ValueError, "expected 30 columns"):
            builder.parse_daily_geomagnetic(malformed)

    def test_join_uses_date_labels_and_excludes_partial_day(self):
        joined, summary = builder.join_daily_data(self.geomag, self.f107)
        self.assertEqual(summary["record_count"], 29)
        self.assertEqual(joined[0]["date"], "2026-10-05")
        self.assertEqual(joined[-1]["date"], "2026-11-02")
        self.assertNotIn("2026-11-03", [row["date"] for row in joined])
        self.assertTrue(all(row["complete_kp_intervals"] == 8 for row in joined))
        self.assertEqual(joined[0]["f107_sfu"], 100)

    def test_missing_overlap_is_not_filled_or_interpolated(self):
        reduced_f107 = [row for row in self.f107 if row["date"] != "2026-10-10"]
        joined, _ = builder.join_daily_data(self.geomag, reduced_f107)
        self.assertNotIn("2026-10-10", [row["date"] for row in joined])
        self.assertEqual(len(joined), 28)

    def test_chart_uses_distinct_panel_labels_and_window(self):
        joined, summary = builder.join_daily_data(self.geomag, self.f107)
        chart = builder.render_chart(joined, summary)
        self.assertIn("F10.7 solar radio flux (sfu)", chart)
        self.assertIn("Estimated planetary Kp daily maximum (0–9)", chart)
        self.assertIn("partial 2026-11-03 excluded", chart)

    def test_offline_build_is_idempotent(self):
        paths = [
            ROOT / "data" / "sources.jsonl",
            ROOT / "data" / "sources.csv",
            ROOT / "data" / "dataset_registry.json",
            ROOT / "data" / "provenance" / "release_v07_sources.jsonl",
            ROOT / "data" / "datasets" / "noaa_daily_geomagnetic_2026-11-03.json",
            ROOT / "data" / "datasets" / "noaa_f107_kp_daily_join_2026-11-03.json",
            ROOT / "data" / "datasets" / "noaa_f107_kp_daily_join_2026-11-03.csv",
            ROOT / "data" / "packets" / "examples" / "space-weather-noaa-2026-11-03.v0.7.packet.json",
            ROOT / "assets" / "space_weather_f107_kp_v07.svg",
            ROOT / "site" / "datasets.html",
            ROOT / "site" / "index.html",
            ROOT / "data" / "release_v07_lineage.json",
        ]
        before = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        builder.build()
        after = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
        self.assertEqual(before, after)

    def test_registry_distinguishes_observed_derived_and_synthetic(self):
        registry = json.loads((ROOT / "data" / "dataset_registry.json").read_text(encoding="utf-8"))
        kinds = {item["dataset_id"]: item["kind"] for item in registry["datasets"]}
        self.assertEqual(kinds["DS-F107-2026-11-02"], "observed")
        self.assertEqual(kinds["DS-GEOMAG-2026-11-03"], "observed")
        self.assertEqual(kinds["DS-SPACEWEATHER-JOIN-2026-11-03"], "derived")
        self.assertEqual(kinds["DS-SYNTHETIC-FREQUENCY-STABILITY-V06"], "synthetic")


if __name__ == "__main__":
    unittest.main()
