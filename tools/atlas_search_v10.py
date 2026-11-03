#!/usr/bin/env python3
"""Search the frozen v1.0 Signal Atlas index without network access."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from atlas_search_core_v10 import search_entries

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "unified_search_index_v10.json"
OUTPUT_FIELDS = (
    "id", "kind", "title", "summary", "path", "url", "domain", "country",
    "date_start", "date_end", "data_kind", "source_ids", "dataset_ids", "score",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", nargs="?", default="")
    parser.add_argument("--kind", default="")
    parser.add_argument("--domain", default="")
    parser.add_argument("--data-kind", default="", choices=("", "observed", "derived", "synthetic"))
    parser.add_argument("--country", default="")
    parser.add_argument("--from-date", default="")
    parser.add_argument("--to-date", default="")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    if not INDEX.is_file():
        parser.error("search index missing; run python tools/build_v10.py")
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    hits = search_entries(
        index,
        args.query,
        kind=args.kind,
        domain=args.domain,
        data_kind=args.data_kind,
        country=args.country,
        date_from=args.from_date,
        date_to=args.to_date,
        limit=args.limit,
    )
    if args.as_json:
        print(json.dumps([{key: hit.get(key) for key in OUTPUT_FIELDS} for hit in hits], ensure_ascii=False, indent=2))
    else:
        print(f"{len(hits)} result(s) from {index['entry_count']} indexed items")
        for hit in hits:
            dates = f" | {hit['date_start']} to {hit['date_end']}" if hit.get("date_start") else ""
            print(f"[{hit['kind']}] {hit['id']} | {hit['title']}{dates} | score {hit['score']}")
            print(f"  {hit['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
