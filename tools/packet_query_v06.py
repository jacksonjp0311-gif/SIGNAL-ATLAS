#!/usr/bin/env python3
"""Deterministic, offline, provenance-first packet generation for Signal Atlas 0.6."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
STOP = {"a", "an", "the", "of", "for", "in", "to", "and", "on", "from", "by", "how", "what", "does", "with", "is", "are", "do", "can", "about"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return " ".join(re.findall(r"[a-z0-9]+", text))


def load_jsonl(name: str):
    return [json.loads(line) for line in (DATA / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def packet(query: str, limit: int = 5, include_candidates: bool = False) -> dict:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("Query must contain text")
    if not 1 <= limit <= 20:
        raise ValueError("limit must be 1..20")
    sources = load_jsonl("sources.jsonl")
    claims = load_jsonl("claims.jsonl")
    alias_path = DATA / "query_aliases_v06.json"
    aliases = json.loads(alias_path.read_text(encoding="utf-8"))
    qnorm = normalized(query)
    query_terms = [t for t in qnorm.split() if len(t) > 1 and t not in STOP]
    if not query_terms:
        raise ValueError("Query must contain one or more meaningful terms")

    concept_hits = []
    concept_source_matches: dict[str, list[dict]] = {}
    for concept in aliases["concepts"]:
        matched_phrases = [phrase for phrase in concept["query_phrases"] if f" {normalized(phrase)} " in f" {qnorm} "]
        if matched_phrases:
            concept_hits.append({"concept_id": concept["id"], "matched_phrases": matched_phrases, "mapping_basis": concept["mapping_basis"]})
            for sid in concept["source_ids"]:
                concept_source_matches.setdefault(sid, []).append({"type": "curated_alias", "concept_id": concept["id"], "matched_phrases": matched_phrases})

    ranked = []
    for source in sources:
        corpus = normalized(" ".join([
            source.get("title", ""), source.get("summary", ""), source.get("publisher", ""),
            source.get("country", ""), source.get("domain", ""), " ".join(source.get("topics", []))
        ]))
        lexical_hits = [term for term in query_terms if term in corpus.split()]
        strict_match = bool(query_terms) and len(lexical_hits) == len(query_terms)
        reasons = list(concept_source_matches.get(source["id"], []))
        if strict_match:
            reasons.append({"type": "exact_metadata_terms", "matched_terms": lexical_hits})
        if reasons:
            score = 100 * len(concept_source_matches.get(source["id"], [])) + (16 * sum(t in normalized(source.get("title", "")).split() for t in lexical_hits)) + 3 * len(lexical_hits)
            ranked.append((score, source["id"], source, reasons))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    chosen = ranked[:limit]
    chosen_ids = {item[2]["id"] for item in chosen}

    cards = []
    for score, _, source, reasons in chosen:
        cards.append({
            "id": source["id"], "title": source["title"], "publisher": source["publisher"],
            "country": source["country"], "domain": source["domain"], "url": source["url"],
            "summary": source["summary"], "rights": source.get("rights"),
            "review_status": source.get("review_status"), "review_scope": source.get("review_scope"),
            "time_scope": source.get("time_scope"), "checked_at": source.get("checked_at"),
            "match_reasons": reasons, "retrieval_score": score
        })

    bounded_claims = []
    for claim in claims:
        overlap = sorted(chosen_ids.intersection(claim.get("source_ids", [])))
        if overlap:
            bounded_claims.append({
                "id": claim["id"], "claim": claim["claim"], "claim_type": claim.get("claim_type"),
                "evidence_status": claim.get("evidence_status"), "review_date": claim.get("review_date"),
                "matched_source_ids": overlap, "all_claim_source_ids": claim.get("source_ids", []),
                "partial_evidence_selection": len(overlap) < len(claim.get("source_ids", [])),
                "notes": claim.get("notes")
            })

    candidates = []
    if include_candidates:
        for note in load_jsonl("research_notes.jsonl"):
            matched = sorted(chosen_ids.intersection(note.get("source_ids", [])))
            if matched:
                candidates.append({"id": note["id"], "title": note["title"], "limitation": note.get("limitation"), "matched_source_ids": matched, "status": "candidate-not-validated"})

    unresolved = []
    if not cards:
        unresolved.append({"query": query, "reason": "No matching source card in local metadata or curated alias table; research gap or query mismatch."})
    elif concept_hits:
        matched_phrases = {normalized(p) for hit in concept_hits for p in hit["matched_phrases"]}
        unresolved_tokens = [t for t in query_terms if not any(t in phrase.split() for phrase in matched_phrases)]
        if unresolved_tokens:
            unresolved.append({"query_terms": unresolved_tokens, "reason": "These terms were not independently resolved by the curated aliases; selected cards cover only the matched concepts."})

    result = {
        "schema": "signal-atlas-research-packet/0.6", "atlas_version": "0.6", "created_at": "2026-11-02",
        "query": query,
        "retrieval_method": "deterministic local metadata terms plus inspectable curator-authored phrase-to-source mappings; no network, full-text search, embedding, or model",
        "alias_lexicon_version": aliases["schema"], "matched_alias_concepts": concept_hits,
        "input_sha256": {"sources.jsonl": digest(DATA / "sources.jsonl"), "claims.jsonl": digest(DATA / "claims.jsonl"), "query_aliases_v06.json": digest(alias_path)},
        "sources": cards, "claims_attributed_to_sources": bounded_claims,
        "candidate_notes_excluded_by_default": not include_candidates, "candidate_notes": candidates,
        "unresolved": unresolved,
        "caveats": [
            "Source cards summarize external material and can be incomplete or stale; open the original URL.",
            "Source self-description and archive descriptions are attributed evidence, not independent corroboration.",
            "A claim can have only a subset of its cited sources in this bounded packet; inspect the partial-selection flag.",
            "Aliases are editorial retrieval hints, not semantic equivalence or calibrated confidence.",
            "A checksum establishes byte identity, not source truth, freshness, license, answer quality, or inference cost."
        ]
    }
    canonical = json.dumps(result, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    result["packet_sha256"] = hashlib.sha256(canonical).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description="Generate a bounded, read-only Signal Atlas v0.6 metadata packet")
    parser.add_argument("query", nargs="+", help="question or metadata terms")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--include-candidates", action="store_true", help="include separately labeled provisional research notes")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = json.dumps(packet(" ".join(args.query), args.limit, args.include_candidates), ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(output.replace("\r\n", "\n").encode("utf-8"))
    else:
        sys.stdout.write(output)


if __name__ == "__main__":
    main()
