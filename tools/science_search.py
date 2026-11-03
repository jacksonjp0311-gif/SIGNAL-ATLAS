#!/usr/bin/env python3
"""Offline science citation search (derivative index, not original source verification)."""
from pathlib import Path
import argparse,sqlite3,json,re
R=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser(description='Search local Signal Atlas science citations/chapters')
 p.add_argument('terms',nargs='+');p.add_argument('-j','--json',action='store_true');p.add_argument('--limit',type=int,default=12)
 args=p.parse_args(); q=' '.join(args.terms)
 tokens=re.findall(r'[\w]+',q,flags=re.UNICODE)
 if not tokens:raise SystemExit('Specify alphabetic search terms')
 fts=' AND '.join('"'+token.replace('"','')+'"' for token in tokens)
 conn=sqlite3.connect(R/'data/science_index.sqlite');conn.row_factory=sqlite3.Row
 rows=[dict(x) for x in conn.execute('SELECT e.* FROM entries_fts f JOIN entries e ON e.id=f.id WHERE entries_fts MATCH ? ORDER BY bm25(entries_fts) LIMIT ?', (fts,max(0,args.limit)))]
 result={'query':q,'search_scope':'local original science chapter text, bibliographic metadata and unadmitted research notes only','items':rows,'warning':'This index does not contain linked third-party PDF full text and does not establish scientific correctness.'}
 if args.json:print(json.dumps(result,indent=2,ensure_ascii=False))
 else:
  for x in rows:print(f"{x['id']} [{x['kind']} | {x['evidence_status']}]: {x['title']}\n  {x['locator']}\n  Source: {x['source_ids']}\n")
 if not rows:print('No local matches. Try a broader term.')
 conn.close()
if __name__=='__main__':main()
