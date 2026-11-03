#!/usr/bin/env python3
"""Offline Signal Atlas metadata search; no network, dependencies or model execution."""
import argparse, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
    return [json.loads(line) for line in (ROOT/'data'/name).read_text(encoding='utf-8').splitlines() if line.strip()]
def main():
    p=argparse.ArgumentParser(description='Search Signal Atlas source metadata and attributed claims (offline)')
    p.add_argument('terms',nargs='+',help='words to find in the curated index')
    p.add_argument('--limit',type=int,default=12,help='max source cards (default 12)')
    p.add_argument('--publications',action='store_true',help='search scholarly publication metadata rather than general source cards')
    p.add_argument('-j','--json',action='store_true',help='machine-readable JSON output')
    a=p.parse_args();query=' '.join(a.terms).casefold()
    source=load('sources.jsonl');claim=load('claims.jsonl');notes=load('research_notes.jsonl');pubs=load('publications.jsonl')
    def rank(s):
        title=str(s.get('title','')).casefold();sub=str(s.get('summary',s.get('claim',s.get('abstract','')))).casefold()
        full=json.dumps(s,ensure_ascii=False).casefold();terms=query.split()
        if not all(t in full for t in terms):return 0
        return 12*sum(t in title for t in terms)+4*sum(t in sub for t in terms)+1
    ss=sorted((s for s in source if rank(s)),key=rank,reverse=True)[:max(0,a.limit)]
    if a.publications:
        pubhits=sorted((p for p in pubs if rank(p)),key=rank,reverse=True)[:max(0,a.limit)]
        obj={'query':' '.join(a.terms),'method':'offline bibliographic metadata','publications':pubhits,'limitations':['PDF links are not mirrored PDF files. local_pdf null means no local copy.','Publication claims are source-attributed; preprint findings need independent review.']}
        if a.json: print(json.dumps(obj,ensure_ascii=False,indent=2))
        else:
            for p in pubhits:print(f"{p['id']} / {p['title']}\n  {p['source']}\n  {p['pdf_url']}\n  License: {p['license']} / Local file: {p['local_pdf']}")
        return 0
    source_ids={s['id'] for s in ss}
    cs=[c for c in claim if any(z in source_ids for z in c['source_ids']) or rank(c)]
    ns=[n for n in notes if any(z in source_ids for z in n['source_ids']) or rank(n)]
    obj={'query':' '.join(a.terms),'method':'offline curated metadata only','sources':ss,'claims':cs,'research_notes_candidates':ns,'limitations':['This command does not check external URLs or verify source accuracy.','Research notes are first-pass editorial analysis.','A source self-report is not independently verified operational capability.']}
    if a.json:print(json.dumps(obj,ensure_ascii=False,indent=2))
    else:
        print(f'SIGNAL ATLAS · offline sources {len(ss)} · claims {len(cs)} · candidate notes {len(ns)}')
        for s in ss:print(f"\n{s['id']} · {s['title']}\n  {s['summary']}\n  {s['url']}")
        for c in cs[:8]:print(f"\n  CLAIM {c['id']} [{c.get('evidence_status','')}]: {c['claim']} ({', '.join(c['source_ids'])})")
    return 0
if __name__=='__main__':raise SystemExit(main())
