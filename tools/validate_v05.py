#!/usr/bin/env python3
"""Edition 0.5 integrity checks, executed before packaging."""
import argparse,csv,hashlib,json,subprocess,sys,sqlite3,re,xml.etree.ElementTree as ET
from pathlib import Path
parser=argparse.ArgumentParser(description='Audit an extracted Signal Atlas v0.5 repository')
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1],help='repository root; defaults to this tool\'s parent')
R=parser.parse_args().root.resolve();D=R/'data';problems=[]
def read(name):return [json.loads(x) for x in (D/name).read_text().splitlines() if x.strip()]
S=read('sources.jsonl');C=read('claims.jsonl');P=read('publications.jsonl');E=read('entities.jsonl');N=read('research_notes.jsonl');Doc=read('documents.jsonl')
expected={'sources':134,'claims':69,'publications':23,'entities':18,'notes':18}
for name,arr in [('sources',S),('claims',C),('publications',P),('entities',E),('notes',N)]:
 if len(arr)!=expected[name]:problems.append(f'{name}: expected {expected[name]}, got {len(arr)}')
 for record in arr:
  if not record.get('id'):problems.append(f'{name}: no id')
 if len({row['id'] for row in arr})!=len(arr):problems.append(f'{name}: duplicate ids')
urls={s['url'] for s in S};sid={s['id'] for s in S};cid={c['id'] for c in C}
if len(urls)!=len(S):problems.append('duplicate source URLs')
with (D/'sources.csv').open(newline='',encoding='utf-8') as f:
 dr=csv.DictReader(f);rows=list(dr)
 if len(dr.fieldnames)!=len(set(dr.fieldnames)):problems.append('duplicate CSV columns')
 if {x['id'] for x in rows}!=sid:problems.append('CSV/JSON source ID mismatch')
 if len(rows)!=len(S):problems.append('CSV row count')
for entry in P:
 if entry['source_id'] not in sid:problems.append('missing pub source '+entry['id'])
 if entry['local_pdf'] is not None:problems.append('claimed third-party PDF mirror '+entry['id'])
 if not (R/f'documents/publications/reference-cards/{entry["id"]}.md').exists():problems.append('missing pub ref card '+entry['id'])
for e in E:
 if any(x not in sid for x in e['source_ids']):problems.append('dangling entity references '+e['id'])
for c in C:
 if any(x not in sid for x in c['source_ids']):problems.append('dangling evidence '+c['id'])
for n in N:
 if any(x not in sid for x in n['source_ids']):problems.append('dangling candidate '+n['id'])
for doc in Doc:
 if doc.get('source_id') and doc['source_id'] not in sid:problems.append('dangling document '+doc['document_id'])
 if doc.get('local_pdf_present'):
  f=R/doc['local_pdf_path'];
  if not f.is_file():problems.append('missing local PDF '+str(f))
  elif hashlib.sha256(f.read_bytes()).hexdigest()!=doc.get('sha256'):problems.append('hash mismatch local PDF '+str(f))
for svg in (R/'assets').glob('*.svg'):
 try:
  root=ET.parse(svg).getroot()
  if svg.name.endswith('_v05.svg') or svg.name=='README_HERO.svg':
   if root.find('{http://www.w3.org/2000/svg}title') is None:problems.append('SVG title missing '+svg.name)
   if root.find('{http://www.w3.org/2000/svg}desc') is None:problems.append('SVG desc missing '+svg.name)
 except Exception as ex:problems.append(f'XML broken {svg.name}: {ex}')
if len(list((R/'assets').glob('*.svg')))!=25:problems.append('expected 25 SVG figures')
if len(list((R/'courses').glob('[0-9]*.md')))!=24:problems.append('expected 24 lesson files')
graph=json.loads((D/'topic_graph.json').read_text())
for t in graph['nodes']:
 if any(x not in sid for x in t['sources']):problems.append('topic source missing '+t['id'])
 for l in t['lessons']:
  if not (R/'courses'/l).is_file():problems.append('topic lesson missing '+l)
alltopic={x['id'] for x in graph['nodes']}
for r in graph['edges']:
 if r['from'] not in alltopic or r['to'] not in alltopic:problems.append('dangling topic edge')
obs=json.loads((D/'experiments/noaa_f107_v05.json').read_text())
if obs['sample_count']!=30 or obs['mean']!=109.9:problems.append('NOAA observation regression')
if hashlib.sha256((D/'datasets/noaa_f107_30day_2026-11-02.json').read_bytes()).hexdigest()!=obs['content_sha256']:problems.append('NOAA source sha')
benchmark=json.loads((D/'experiments/packet_probe_v05.json').read_text())
if benchmark['total']!=20 or benchmark['hit_at_5']!=13 or benchmark['citation_integrity_count']!=20:problems.append('packet evaluation regression')
# JSON packet consistency against current canonical catalog
p=R/'data/packets/examples/solar-flux.v0.5.packet.json';example=json.loads(p.read_text())
if example['index_sha256']!=hashlib.sha256((D/'sources.jsonl').read_bytes()).hexdigest():problems.append('fresh example index sha')
raw=example.copy();sig=raw.pop('packet_sha256')
if sig!=hashlib.sha256(json.dumps(raw,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest():problems.append('packet sha')
if example['atlas_version']!='0.5':problems.append('packet version')
# SQLite manifest should represent canonical file hashes
with sqlite3.connect(D/'atlas_index.sqlite') as db:
 for filename,digest,count in db.execute('SELECT filename,sha256,item_count FROM index_manifest'):
  if hashlib.sha256((D/filename).read_bytes()).hexdigest()!=digest:problems.append('stale unified index '+filename)
site=(R/'site/index.html').read_text(encoding='utf-8')
for fragment in ['const CLAIM_COUNT=69;','TOPIC MAP</a>','topic-map.html','const SOURCES=','const PUBS=','const LESSONS=']:
 if fragment not in site:problems.append('missing site feature: '+fragment)
for l in re.findall(r'\]\(([^)]+)\)',(R/'README.md').read_text()):
 if l.startswith(('http','mailto:','#')):continue
 if not (R/l.split('#')[0]).exists():problems.append('README broken path '+l)
print('v0.5 AUDIT:',len(S),'sources;',len(C),'claims;',len(P),'publications;',len(E),'profiles; 24 lessons; 25 SVGs')
if problems:
 for p in problems:print('FAIL:',p)
 sys.exit(1)
print('PASS: source ID/URL uniqueness, citations, PDF hashes, topic graph, NOAA data, packet QA, visual accessibility, SQLite manifest, README paths')
