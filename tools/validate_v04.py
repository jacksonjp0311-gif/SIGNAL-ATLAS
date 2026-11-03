#!/usr/bin/env python3
"""Edition-0.4 extension checks beyond the inherited structure validators."""
import json,csv,hashlib,sys,re,xml.etree.ElementTree as ET
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=R/'data';problems=[]
def jlines(name):return [json.loads(line) for line in (D/name).read_text().splitlines() if line.strip()]
S=jlines('sources.jsonl');C=jlines('claims.jsonl');P=jlines('publications.jsonl');Q=jlines('research_notes.jsonl')
assert len(S)==112 and len(C)==56 and len(P)==17 and len(Q)==14
hdr=['id','title','publisher','country','domain','url','summary','source_type','time_scope','rights','review_status','added_at','topics','snapshot_status','language','checked_at','review_scope','research_batch']
with (D/'sources.csv').open(newline='',encoding='utf-8') as f:
 r=csv.DictReader(f)
 if r.fieldnames != hdr:problems.append('CSV fields not canonical and unique')
 rows=list(r)
 if len(rows)!=len(S):problems.append('CSV record count mismatch')
 if [x['id'] for x in rows] != [x['id'] for x in S]:problems.append('CSV IDs/order mismatch JSONL')
 if len(rows)==len(S):
  for a,b in zip(rows,S):
   if any(a[k]!=str(b.get(k,'')) for k in hdr):problems.append('CSV differs from JSONL at '+b['id']);break
for s in S:
 if not s.get('rights'):problems.append('Missing source rights '+s['id'])
 if s.get('research_batch')=='2026-11-02-D':
  if s['snapshot_status']!='catalog-card-only':problems.append('Misleading snapshot flag')
  if not s.get('checked_at'):problems.append('Missing added source review timestamp')
sourceids={s['id'] for s in S}
for p in P:
 if p['source_id'] not in sourceids:problems.append('Publication dangling source '+p['id'])
 if p['local_pdf'] is not None:problems.append('Unexpected local third-party PDF '+p['id'])
for f in (R/'assets').glob('*.svg'):
 try:root=ET.parse(f).getroot()
 except Exception as e:problems.append('SVG not parseable '+str(f)+str(e));continue
 if f.name in ('experiment_aliasing.svg','experiment_am_sidebands.svg','coverage_domains.svg','research_amortization.svg','evidence_boundary.svg'):
  if not root.findall('{http://www.w3.org/2000/svg}title'):problems.append('New SVG no title '+f.name)
  if not root.findall('{http://www.w3.org/2000/svg}desc'):problems.append('New SVG no description '+f.name)
results=json.loads((D/'experiments/signal_lab_v04.json').read_text())
for name,p in [('fs_20_Hz',3),('fs_100_Hz',17)]:
 if abs(results[name]['measured_peak_hz']-p)>1e-8 or not results[name]['passed']:problems.append('Synthetic measured peak failed '+name)
if any(abs(results['am_modulation']['measured_amplitudes'][k]-v)>1e-8 for k,v in {'17':.325,'20':1.,'23':.325}.items()):problems.append('AM spectrum fail')
b=json.loads((D/'experiments/packet_benchmark_v04.json').read_text())
if b['pass_at_5']!=10 or b['total']!=10:problems.append('In-sample packet source-id smoke test fail')
example=json.loads((D/'packets/examples/sampling.v0.4.packet.json').read_text())
if example['index_sha256']!=hashlib.sha256((D/'sources.jsonl').read_bytes()).hexdigest():problems.append('Example packet stale index sha')
t=example.copy();sha=t.pop('packet_sha256')
if sha!=hashlib.sha256(json.dumps(t,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest():problems.append('Example packet SHA inconsistent')
site=(R/'site/index.html').read_text()
for value in ['data-pane="packets"','id="packets"','experiment_aliasing.svg','research_amortization.svg','coverage_domains.svg','const CLAIM_COUNT=56;']:
 if value not in site:problems.append('Missing site feature '+value)
if len(list((R/'assets').glob('*.svg')))!=19:problems.append('Incorrect new SVG total')
if len(list((R/'courses').glob('[0-9]*.md')))!=20:problems.append('Unexpected lesson count')
for p in ['RESEARCH_AMORTIZATION.md','COVERAGE_AUDIT_v04.md','RELEASE_AUDIT_v04.md']:
 if not (R/'docs/research'/p).exists():problems.append('Missing audit '+p)
print('v0.4 audit:',len(S),'sources',len(C),'claims',len(P),'publication entries','19 diagrams')
if problems:
 for p in problems:print('FAIL:',p)
 sys.exit(1)
print('PASS: canonical CSV, rights, citations, source-packet checksums, experiments, offline navigation artifacts')
