from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from atlas_search_core_v10 import search_entries
from build_v10 import build_search, canon


class UnifiedSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = json.loads((ROOT / "data/unified_search_index_v10.json").read_text(encoding="utf-8"))

    def test_all_terms_and_title_weighting(self):
        hits = search_entries(self.index, "GOES X-ray flux")
        self.assertTrue(hits)
        self.assertIn("GOES", hits[0]["title"])
        self.assertEqual([], search_entries(self.index, "GOES term-that-does-not-exist"))

    def test_kind_data_kind_and_date_filters(self):
        hits = search_entries(self.index, "GOES X-ray flux", kind="dataset", data_kind="observed", date_from="2026-11-03", date_to="2026-11-03")
        self.assertEqual(["DS-GOES-XRS-PRIMARY-6H-2026-11-03"], [hit["id"] for hit in hits])
        self.assertEqual([], search_entries(self.index, "GOES X-ray flux", kind="dataset", date_to="2026-11-02"))

    def test_domain_country_filters(self):
        hits = search_entries(self.index, "Australian Signals Directorate", kind="source", domain="military-history", country="Australia")
        self.assertIn("SRC-150", [hit["id"] for hit in hits])
        self.assertTrue(all(hit["country"] == "Australia" and hit["domain"] == "military-history" for hit in hits))

    def test_results_have_stable_order(self):
        first = [hit["id"] for hit in search_entries(self.index, "solar wind", limit=15)]
        second = [hit["id"] for hit in search_entries(self.index, "solar wind", limit=15)]
        self.assertEqual(first, second)

    def test_rebuilding_index_is_byte_deterministic(self):
        index_path = ROOT / "data/unified_search_index_v10.json"
        manifest_path = ROOT / "data/unified_search_manifest_v10.json"
        before = (hashlib.sha256(index_path.read_bytes()).hexdigest(), hashlib.sha256(manifest_path.read_bytes()).hexdigest())
        build_search()
        after = (hashlib.sha256(index_path.read_bytes()).hexdigest(), hashlib.sha256(manifest_path.read_bytes()).hexdigest())
        self.assertEqual(before, after)

    def test_packet_digest_and_frozen_index_binding(self):
        packet = json.loads((ROOT / "data/packets/examples/atlas-cross-domain-research.v1.0.packet.json").read_text(encoding="utf-8"))
        expected = packet.pop("packet_sha256")
        self.assertEqual(expected, canon(packet))
        index_hash = hashlib.sha256((ROOT / "data/unified_search_index_v10.json").read_bytes()).hexdigest()
        self.assertEqual(index_hash, packet["inputs"]["index_sha256"])


if __name__ == "__main__":
    unittest.main()
