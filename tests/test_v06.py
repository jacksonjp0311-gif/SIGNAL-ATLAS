import hashlib
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from packet_query_v06 import packet, DATA
from frequency_stability_lab import allan_deviation, result, synthetic_series


class PacketTests(unittest.TestCase):
    def test_curated_alias_retrieves_expected_card_with_reason(self):
        packet_data = packet("quiet sun radio flux")
        ids = [s["id"] for s in packet_data["sources"]]
        self.assertIn("SRC-114", ids)
        card = next(s for s in packet_data["sources"] if s["id"] == "SRC-114")
        self.assertTrue(any(reason["type"] == "curated_alias" for reason in card["match_reasons"]))

    def test_alias_packet_exposes_input_hashes_and_canonical_packet_digest(self):
        packet_data = packet("frequency stability", limit=5)
        self.assertEqual(packet_data["input_sha256"]["sources.jsonl"], hashlib.sha256((DATA / "sources.jsonl").read_bytes()).hexdigest())
        unsigned = dict(packet_data)
        checksum = unsigned.pop("packet_sha256")
        canonical = json.dumps(unsigned, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.assertEqual(checksum, hashlib.sha256(canonical).hexdigest())
        self.assertTrue(all("url" in s and "review_scope" in s for s in packet_data["sources"]))

    def test_unmatched_query_is_explicitly_unresolved(self):
        packet_data = packet("quasar wind tunnel chronology")
        self.assertEqual(packet_data["sources"], [])
        self.assertTrue(packet_data["unresolved"])

    def test_candidates_excluded_unless_requested(self):
        self.assertTrue(packet("spectrum monitoring", include_candidates=False)["candidate_notes_excluded_by_default"])
        included = packet("spectrum monitoring", include_candidates=True)
        self.assertFalse(included["candidate_notes_excluded_by_default"])
        self.assertTrue(all(item["status"] == "candidate-not-validated" for item in included["candidate_notes"]))

    def test_limit_is_bounded(self):
        with self.assertRaises(ValueError):
            packet("radio", limit=21)


class StabilityLabTests(unittest.TestCase):
    def test_fixed_seed_series_and_output_are_reproducible(self):
        self.assertEqual(synthetic_series(), synthetic_series())
        self.assertEqual(result(), result())

    def test_allan_deviation_known_two_block_case(self):
        measurement = allan_deviation([0.0, 0.0, 2.0, 2.0], 2)
        self.assertEqual(measurement["block_average_count"], 2)
        self.assertEqual(measurement["allan_variance"], 2.0)
        self.assertEqual(measurement["allan_deviation"], 2 ** 0.5)

    def test_requires_two_blocks(self):
        with self.assertRaises(ValueError):
            allan_deviation([1.0, 2.0, 3.0], 2)


if __name__ == "__main__":
    unittest.main()
