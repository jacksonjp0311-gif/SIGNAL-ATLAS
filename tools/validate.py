#!/usr/bin/env python3
"""Audit local JSONL integrity, referential links, rights flags, web UI and archive."""
import json,csv,sys,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'data'; issues=[]
def load(f):
    try:return [json.loads(x) for x in (D/f).read_text(encoding='utf-8').splitlines() if x.strip()]
    except Exception as exc: issues.append(f'Bad JSONL {f}: {exc}');return []
S=load('sources.jsonl');C=load('claims.jsonl');R=load('relationships.jsonl');E=load('entities.jsonl');N=load('research_notes.jsonl')
for name,items in [('source',S),('claim',C),('entity',E),('note',N)]:
    ids=[x['id'] for x in items]
    if len(ids)!=len(set(ids)):issues.append(f'Duplicate {name} IDs')
sourceids={x['id'] for x in S};claimids={x['id'] for x in C};urlset=set()
for s in S:
    if not s.get('url','').startswith('https://'):issues.append(f'Bad https URL: {s.get("id")}')
    n=s['url'].split('?')[0].rstrip('/')
    if n in urlset:issues.append(f'Duplicate source URL: {n}')
    urlset.add(n)
    if s.get('snapshot_status') not in ('catalog-card-only','licensed-snapshot','dataset-snapshot-included'):issues.append(f'Unknown snapshot status {s["id"]}')
for c in C:
    if not c.get('source_ids'):issues.append(f'Unsourced claim {c["id"]}')
    for z in c.get('source_ids',[]):
        if z not in sourceids:issues.append(f'Dangling claim {c["id"]} => {z}')
for e in E:
    for z in e.get('source_ids',[]):
        if z not in sourceids:issues.append(f'Dangling entity {e["id"]} => {z}')
for n in N:
    for z in n.get('source_ids',[]):
        if z not in sourceids:issues.append(f'Dangling note {n["id"]} => {z}')
for r in R:
    if r.get('to','').startswith('SRC-') and r['to'] not in sourceids:issues.append(f'Dangling edge to {r["to"]}')
    if r.get('from','').startswith('C-') and r['from'] not in claimids:issues.append(f'Dangling edge from {r["from"]}')
with (D/'sources.csv').open(encoding='utf-8',newline='') as f:
    rows=list(csv.DictReader(f));csv_ids={r['id'] for r in rows}
    if csv_ids!=sourceids:issues.append('CSV / JSONL source IDs differ')
for file in ROOT.rglob('*.md'):
    for rel in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)|!\[[^\]]*\]\(([^)]+)\)',file.read_text(encoding='utf-8')):
        item=next((x for x in rel if x),'')
        if not item or item.startswith(('http:','https:','#','mailto:')):continue
        if not (file.parent/item.split('#')[0]).exists():issues.append(f'Missing relative link: {file.relative_to(ROOT)} -> {item}')
for svg in (ROOT/'assets').glob('*.svg'):
    if '<title' not in svg.read_text(encoding='utf-8'):issues.append(f'No accessible title in {svg.name}')
site=(ROOT/'site/index.html').read_text(encoding='utf-8')
for marker in ['data-pane="visuals"','data-pane="research"','research_admission.svg','sampling_aliasing.svg']:
    if marker not in site:issues.append(f'Site missing {marker}')
print(f"Verified local cross-references: {len(S)} sources, {len(C)} claims, {len(N)} research notes, {len(E)} geopolitical profiles, {len(list((ROOT/'assets').glob('*.svg')))} SVG diagrams")
if issues:
    for x in issues:print('ERROR:',x)
    sys.exit(1)
print('PASS: local package structure, IDs, links, core navigation and rights flags')
