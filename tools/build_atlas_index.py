#!/usr/bin/env python3
"""Build a portable, derived read-only SQLite index from authoritative JSONL files.

The index contains citation-bearing source metadata, scoped claims, references,
research notes, and country context; it does not contain remote full-text documents.
"""
from pathlib import Path
import json,sqlite3,hashlib
R=Path(__file__).resolve().parents[1];D=R/'data'
def read(name):
 return [json.loads(line) for line in (D/name).read_text(encoding='utf-8').splitlines() if line.strip()]
collections={'source':'sources.jsonl','claim':'claims.jsonl','publication':'publications.jsonl','research_candidate':'research_notes.jsonl','world_profile':'entities.jsonl'}
path=D/'atlas_index.sqlite'
if path.exists():path.unlink()
con=sqlite3.connect(path)
con.executescript('''
CREATE TABLE records (id TEXT PRIMARY KEY, kind TEXT NOT NULL, title TEXT NOT NULL, body TEXT, source_ids TEXT NOT NULL, locator TEXT, rights TEXT, evidence_status TEXT, json_payload TEXT NOT NULL);
CREATE VIRTUAL TABLE records_fts USING fts5(id UNINDEXED, title, body, tokenize="unicode61 remove_diacritics 2");
CREATE TABLE index_manifest (filename TEXT PRIMARY KEY, sha256 TEXT NOT NULL, item_count INTEGER NOT NULL);
''')
with con:
 for kind,filename in collections.items():
  entries=read(filename)
  for row in entries:
   rid=row['id']
   title=row.get('title') or row.get('label') or row.get('claim') or row.get('abstract') or rid
   body=' '.join([row.get('summary',''),row.get('abstract',''),row.get('claim',''),row.get('institutions',''),
                  row.get('public_scope_note',''),row.get('limitation',''),
                  ' '.join(row.get('topics',[]) if isinstance(row.get('topics',[]),list) else [])])
   source_ids=row.get('source_ids',[]) + ([row['source_id']] if row.get('source_id') else [])
   if kind=='source':source_ids=[rid]
   con.execute('INSERT INTO records VALUES (?,?,?,?,?,?,?,?,?)',(rid,kind,title,body,json.dumps(source_ids),
    row.get('url') or row.get('source') or '',row.get('rights') or row.get('license') or 'N/A',
    row.get('evidence_status') or row.get('review_status') or 'source-metadata',json.dumps(row,ensure_ascii=False)))
   con.execute('INSERT INTO records_fts (id,title,body) VALUES (?,?,?)',(rid,title,body))
  con.execute('INSERT INTO index_manifest VALUES (?,?,?)',(filename,hashlib.sha256((D/filename).read_bytes()).hexdigest(),len(entries)))
con.execute('PRAGMA optimize');con.close()
print('Built',path,'with',sum(len(read(fn)) for fn in collections.values()),'records and complete per-file SHA-256 manifest')
