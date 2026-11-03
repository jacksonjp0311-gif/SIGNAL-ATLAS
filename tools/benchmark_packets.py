#!/usr/bin/env python3
"""Fixed metadata smoke-test benchmark, not proof of LLM compute savings."""
import json,sys,datetime,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from packet_query import packet
S=[json.loads(s) for s in (R/'data/sources.jsonl').read_text().splitlines() if s.strip()]
by_title={s['title']:s['id'] for s in S}
CASES=[
 ('radio regulations','ITU Radio Regulations, 2024 edition'),
 ('radio astronomy','NRAO General Introduction to Radio Astronomy'),
 ('remote sensing','NASA Earth Observatory: Remote Sensing'),
 ('Sweden history','FRA public history (Swedish)'),
 ('sampling Fourier','MIT Signals and Systems lecture notes'),
 ('radar phase','Get to Know Synthetic Aperture Radar — Overview'),
 ('cryptologic records','NARA record group 457: NSA/CSS and predecessors'),
 ('speech dataset','MLCommons Unsupervised People’s Speech dataset'),
 ('Japan white paper','Defense of Japan 2026 white-paper portal'),
 ('interferometry calibration','NRAO General Introduction to Radio Astronomy')
]
full=len((R/'data/sources.jsonl').read_bytes())
records=[]
for query,title in CASES:
    if title not in by_title:raise ValueError('Unknown expected title: '+title)
    response=packet(query,5)
    payload=len(json.dumps(response,ensure_ascii=False,separators=(',',':')).encode())
    hit=by_title[title] in [s['id'] for s in response['sources']]
    records.append({'query':query,'expected_source_id':by_title[title],'hit_at_5':hit,'returned':len(response['sources']),'packet_bytes':payload,'full_catalog_metadata_bytes':full,'payload_fraction':round(payload/full,6)})
result={'benchmark':'fixed ten-query offline catalog smoke test','version':'0.4','interpretation':'Measures source-id coverage and bytes transferred, not inference compute, retrieval correctness at scale, source quality, or answer fidelity. Gold IDs were selected in advance from the same catalog; this is an in-sample check.',
        'cases':records,'pass_at_5':sum(r['hit_at_5'] for r in records),'total':len(records),'mean_packet_bytes':round(sum(r['packet_bytes'] for r in records)/len(records)),'full_catalog_metadata_bytes':full,'mean_reduction_in_metadata_payload_pct':round(100*(1-(sum(r['packet_bytes'] for r in records)/len(records))/full),2)}
folder=R/'data/experiments';folder.mkdir(exist_ok=True)
(folder/'packet_benchmark_v04.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
if result['pass_at_5']<len(CASES):
    print('Missed:',[(r['query'],r['expected_source_id']) for r in records if not r['hit_at_5']]);sys.exit(1)
