# Unified search and collection coverage

## Search behavior

The v1.0 index combines source cards, scoped claims, research notes, publication records, dataset registrations, numbered lessons, selected research Markdown, and project navigation. The index is data/unified_search_index_v10.json; its input paths and SHA-256 values are in data/unified_search_manifest_v10.json.

Queries use case-insensitive lexical matching. All typed terms must occur. Title matches rank above topic matches, then summaries; ties are stable by title and ID. Filters include item kind, domain, country, data kind, and inclusive date-window overlap. The CLI reads only the bundled JSON index. The browser page embeds the same catalog and makes no search network requests.

## Coverage behavior

The coverage report summarizes records and registered files in this release, with date bounds and known gaps. It describes the package contents, not global sensor footprints or field-wide completeness.

## Reproducibility and limits

Run tools/build_v10.py to rebuild from frozen local ledgers, documents, registry, and raw snapshot. Input hashes are recalculated. Search does not fetch web pages, read PDF bodies, use embeddings, assess truth, or generate answers. It is a navigational index for finding and reusing material.

The example packet binds result records to the search index and input manifest with SHA-256. This supports integrity checking, not the correctness of external sources.
