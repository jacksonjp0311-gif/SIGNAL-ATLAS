#!/usr/bin/env python3
"""Build reproducible local SQLite FTS5 index from original MD and cited metadata."""
from pathlib import Path
import json,sqlite3
R=Path(__file__).resolve().parents[1]
rows=[]
for line in (R/'data/publications.jsonl').read_text(encoding='utf-8').splitlines():
 if not line.strip():continue
 p=json.loads(line)
 rows.append((p['id'],'publication',p['title'],p['summary']+'\nTopics: '+', '.join(p['topics']),p['source'],p['source_id'],p['license'],'source-attributed-metadata'))
for p in sorted((R/'docs/science').glob('*.md')):
 rows.append(('SCI-'+p.stem,'original-teaching',p.stem.replace('_',' ').replace('-',' ').title(),p.read_text(encoding='utf-8'),p.relative_to(R).as_posix(),'', 'original-atlas','atlas-authored-explanation'))
for line in (R/'data/research_notes.jsonl').read_text(encoding='utf-8').splitlines():
 if not line.strip():continue
 p=json.loads(line)
 if p.get('category','').lower().startswith('science'):
  rows.append((p['id'],'candidate-research',p['title'],p['abstract']+'\n'+p['limitation'],'data/research_notes.jsonl',','.join(p['source_ids']),'original-atlas','candidate-not-established'))
path=R/'data/science_index.sqlite'
if path.exists():path.unlink()
db=sqlite3.connect(path)
db.executescript('CREATE TABLE entries (id TEXT PRIMARY KEY, kind TEXT NOT NULL, title TEXT NOT NULL, body TEXT NOT NULL, locator TEXT NOT NULL, source_ids TEXT, license TEXT, evidence_status TEXT); CREATE VIRTUAL TABLE entries_fts USING fts5(id UNINDEXED, title, body, tokenize="unicode61");')
with db:
 for row in rows:
  db.execute('INSERT INTO entries VALUES (?,?,?,?,?,?,?,?)',row)
  db.execute('INSERT INTO entries_fts (id,title,body) VALUES (?,?,?)',(row[0],row[2],row[3]))
db.close()
print('Indexed',len(rows),'metadata/chapter/candidate records in',path)
