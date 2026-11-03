#!/usr/bin/env python3
"""Create the deterministic example query packet from the frozen search index."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
from atlas_search_core_v10 import search_entries

ROOT = Path(__file__).resolve().parents[1]

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical_sha(value) -> str:
    return sha(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))

def main() -> None:
    ip=ROOT/"data/unified_search_index_v10.json";mp=ROOT/"data/unified_search_manifest_v10.json"
    index=json.loads(ip.read_text(encoding="utf-8"));manifest=json.loads(mp.read_text(encoding="utf-8"))
    hits=search_entries(index,"GOES X-ray flux",kind="dataset",limit=8)
    packet={"schema_version":"1.0","packet_id":"ATLAS-QUERY-GOES-XRAY-2026-11-03","release_version":"1.0","query":"GOES X-ray flux","filters":{"kind":"dataset"},"method":index["method"],"inputs":{"index_path":"data/unified_search_index_v10.json","index_sha256":sha(ip.read_bytes()),"manifest_path":"data/unified_search_manifest_v10.json","manifest_sha256":manifest["manifest_sha256"]},"results":[{k:h.get(k) for k in ["id","kind","title","summary","path","url","domain","country","date_start","date_end","data_kind","source_ids","dataset_ids","score"]} for h in hits],"limitations":["Lexical metadata retrieval, not full-text or semantic search.","A matching record does not independently verify its source.","Snapshot windows are short and cross-product matches do not establish causality."]}
    packet["packet_sha256"]=canonical_sha(packet)
    target=ROOT/"data/packets/examples/atlas-cross-domain-research.v1.0.packet.json"
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(packet,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(f"PACKET {target.relative_to(ROOT)} sha256={packet['packet_sha256']} results={len(hits)}")

if __name__=="__main__":main()
