"""Deterministic local search over a versioned Signal Atlas index."""
from __future__ import annotations

from typing import Any, Iterable


def _terms(query: str) -> list[str]:
    return [term.casefold() for term in query.split() if term.strip()]


def search_entries(
    index: dict[str, Any] | Iterable[dict[str, Any]],
    query: str = "",
    *,
    kind: str = "",
    domain: str = "",
    data_kind: str = "",
    country: str = "",
    date_from: str = "",
    date_to: str = "",
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Search all terms with stable ranking and optional exact filters.

    Date filters select datasets whose declared interval overlaps the inclusive
    requested range. Items without dates do not match an active date filter.
    """
    if limit < 1:
        raise ValueError("limit must be positive")
    entries = index["entries"] if isinstance(index, dict) else list(index)
    terms = _terms(query)
    hits: list[dict[str, Any]] = []
    for entry in entries:
        if kind and entry.get("kind") != kind:
            continue
        if domain and entry.get("domain") != domain:
            continue
        if data_kind and entry.get("data_kind") != data_kind:
            continue
        if country and entry.get("country") != country:
            continue
        start, end = entry.get("date_start"), entry.get("date_end")
        if date_from and (not end or end < date_from):
            continue
        if date_to and (not start or start > date_to):
            continue
        searchable = entry.get("search_text", "").casefold()
        if not all(term in searchable for term in terms):
            continue
        title = entry.get("title", "").casefold()
        summary = entry.get("summary", "").casefold()
        topics = [value.casefold() for value in entry.get("topics", [])]
        score = sum(
            5 * (term in title)
            + 3 * any(term in topic for topic in topics)
            + 2 * (term in summary)
            + 1
            for term in terms
        )
        hits.append({**entry, "score": score})
    hits.sort(key=lambda hit: (-hit["score"], hit.get("title", "").casefold(), hit.get("id", "")))
    return hits[:limit]
