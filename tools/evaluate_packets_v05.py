#!/usr/bin/env python3
"""Curator-authored stress diagnostic, NOT an LLM benchmark, NOT held-out/bias-free.

Queries include easy matches, paraphrases, and intentional negatives.
Measures whether source ID appears in first five offline metadata search results.
"""
import sys,json,hashlib,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from packet_query import packet
sources=[json.loads(s) for s in (ROOT/'data/sources.jsonl').read_text().splitlines() if s.strip()]
S={s['id']:s for s in sources}
def get(url):return next(s['id'] for s in sources if s['url']==url)
# A published fixed test set with source targets, deliberately including synonyms and hard negatives.
cases=[
 ('solar radio emissions','https://www.spaceweather.gov/phenomena/f107-cm-radio-emissions'),
 ('30-day solar flux','https://services.swpc.noaa.gov/products/10cm-flux-30-day.json'),
 ('Sentinel-1 phase radar','https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel1.html'),
 ('Finnish military intelligence','https://sotilastiedustelukatsaus.fi/en/'),
 ('New Zealand annual oversight','https://igis.govt.nz/publications/annual-reports'),
 ('Brazil ABIN history','https://www.gov.br/abin/pt-br/institucional/hist'),
 ('Japan electromagnetic domain','https://www.mod.go.jp/j/press/wp/wp2026/html/n310204000.html'),
 ('Smirnov Jones formalism','https://arxiv.org/abs/1101.1764'),
 ('GNU Radio tutorials','https://wiki.gnuradio.org/index.php?title=Tutorials'),
 ('SigMF metadata','https://sigmf.org/'),
 ('South Africa defence annual report','https://www.gov.za/documents/annual-reports/department-defence-annual-report-20242025-29-aug-2025'),
 ('interferometer calibration','https://arxiv.org/abs/1101.1765'),
 ('radar precipitation echoes','https://www.weather.gov/grr/DidYouKnowRadar'),
 ('SAR phase amplitude loss','https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel1.html'),
 ('Finnish espionage agency history','https://sotilastiedustelukatsaus.fi/en/past-releases/'),
 ('solar quiet sun flux','https://www.spaceweather.gov/phenomena/f107-cm-radio-emissions'),
 ('NOAA weather profiler hardware','https://psl.noaa.gov/data/obs/instruments/WindProfilerDescription.html'),
 ('Brazil military signal interception','https://www.gov.br/abin/pt-br/institucional/a-abin/'),
 ('Japanese frequency management','https://www.mod.go.jp/j/press/wp/wp2026/html/n310204000.html'),
 ('radio astronomy calibration','https://arxiv.org/abs/1101.1764')]
full=(ROOT/'data/sources.jsonl').stat().st_size
out=[]
for q,url in cases:
 expected=get(url);p=packet(q,limit=5)
 found=[s['id'] for s in p['sources']]
 # Empty responses, wrong/cross-domain source cards and lost metadata are not suppressed.
 passed=expected in found
 assertion=all(s['url']==S[s['id']]['url'] and bool(s['rights']) for s in p['sources'])
 digest=p['packet_sha256'];material=p.copy();material.pop('packet_sha256')
 digest_ok=hashlib.sha256(json.dumps(material,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==digest
 assert assertion and digest_ok, 'Source attribution or checksum broken'
 out.append({'query':q,'expected_id':expected,'hit_at_5':passed,'returned_ids':found,
             'packet_bytes':len(json.dumps(p,ensure_ascii=False).encode()),'citation_integrity':True,'checksum_pass':True})
result={'version':'0.5','benchmark':'Author-curated 20-query offline lexical retrieval diagnostic',
 'limitations':'Not blind, not a representative held-out sample, no LLMs, no websites queried at evaluation time. Does not measure actual answer faithfulness, model compute, or full-text RAG accuracy.',
 'queries':out,'total':len(out),'hit_at_5':sum(x['hit_at_5'] for x in out),
 'misses':[x['query'] for x in out if not x['hit_at_5']],
 'citation_integrity_count':sum(x['citation_integrity'] for x in out),
 'mean_packet_bytes':round(statistics.mean(x['packet_bytes'] for x in out)),
 'full_catalog_jsonl_bytes':full,
 'metadata_payload_reduction_vs_loading_full_catalog_pct':round(100*(1-statistics.mean(x['packet_bytes'] for x in out)/full),2)}
path=ROOT/'data/experiments/packet_probe_v05.json';path.write_text(json.dumps(result,indent=2)+'\n')
print(f"PASS diagnostic: {result['hit_at_5']}/{result['total']} hit@5; {result['citation_integrity_count']} valid packet citations; {len(result['misses'])} misses; mean payload {result['mean_packet_bytes']} bytes")
for x in out:
 if not x['hit_at_5']:print('MISS:',x['query'],'->',x['expected_id'],'returned',x['returned_ids'])
