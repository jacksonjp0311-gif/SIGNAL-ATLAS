#!/usr/bin/env python3
"""Re-score the preserved v0.5 diagnostic queries with v0.6 packets, without overwriting history."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from packet_query_v06 import packet


def main():
    old_path = ROOT / "data" / "experiments" / "packet_probe_v05.json"
    old = json.loads(old_path.read_text(encoding="utf-8"))
    rows = []
    for row in old["queries"]:
        current = packet(row["query"], limit=5)
        ids = [source["id"] for source in current["sources"]]
        rows.append({"query": row["query"], "expected_id": row["expected_id"], "v05_hit_at_5": row["hit_at_5"], "v06_hit_at_5": row["expected_id"] in ids, "v06_returned_ids": ids, "v06_packet_sha256": current["packet_sha256"], "unresolved": current["unresolved"]})
    payload = {
        "schema": "signal-atlas-retrieval-compatibility-diagnostic/0.6",
        "comparison": "same 20 curator-authored queries and expected IDs as the stored v0.5 diagnostic",
        "v05_receipt_sha256": hashlib.sha256(old_path.read_bytes()).hexdigest(),
        "v05_hit_at_5": sum(bool(r["v05_hit_at_5"]) for r in rows), "v06_hit_at_5": sum(bool(r["v06_hit_at_5"]) for r in rows), "query_count": len(rows),
        "citation_integrity": "source IDs resolve to the current canonical source catalog; packet checksums are produced by packet_query_v06.py",
        "independence_limit": "Not a held-out evaluation. Seven v0.6 phrase mappings were authored against the exact seven known v0.5 misses and their stored expected IDs. The higher compatibility score therefore measures targeted repair on a known curator set, not generalization, answer quality, or agent improvement.",
        "compute_limit": "No model executed. Packet byte size and retrieval hit rate do not measure end-to-end inference cost, latency, or answer faithfulness.",
        "queries": rows
    }
    out = ROOT / "data" / "experiments" / "packet_probe_v06.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"v0.5 stored baseline: {payload['v05_hit_at_5']}/{len(rows)}; v0.6 targeted compatibility: {payload['v06_hit_at_5']}/{len(rows)}")
    print("LIMIT: retrospective repair set; not held out and not a model or compute experiment")


if __name__ == "__main__":
    main()
