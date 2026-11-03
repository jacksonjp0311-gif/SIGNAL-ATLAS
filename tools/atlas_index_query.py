#!/usr/bin/env python3
"""Unified FTS read-only query for canonical Signal Atlas metadata. Never a live scraper."""
import argparse,sqlite3,json,re
from pathlib import Path
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description='Search bounded source, scientific reference, claim and research-note metadata')
p.add_argument('query',nargs='+');p.add_argument('--limit',type=int,default=10);p.add_argument('--kind',default='')
a=p.parse_args();assert 1<=a.limit<=100
terms=re.findall(r'[^\W_]+', ' '.join(a.query),re.UNICODE)
if not terms:raise SystemExit('No search terms')
# Quote each lexical term to make FTS syntax safe and require all terms (no implicit web/semantic expansion).
q=' AND '.join('"'+t.replace('"','')+'"' for t in terms)
with sqlite3.connect(f'file:{R / "data/atlas_index.sqlite"}?mode=ro',uri=True) as db:
 rows=db.execute('''SELECT r.id,r.kind,r.title,r.source_ids,r.locator,r.rights,r.evidence_status,bm25(records_fts) AS score
 FROM records_fts JOIN records r USING(id) WHERE records_fts MATCH ? AND (?='' OR kind=?) ORDER BY score LIMIT ?''',(q,a.kind,a.kind,a.limit)).fetchall()
print(json.dumps({'method':'local FTS5 metadata only, not remote full-text', 'query':' '.join(a.query),
 'results':[dict(zip(('id','kind','title','source_ids','locator','rights','evidence_status','score'),row)) for row in rows]},indent=2,ensure_ascii=False))
