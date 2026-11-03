#!/usr/bin/env python3
"""Science library referential integrity, rights and local PDF bytes checks. Stdlib only."""
from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parents[1];error=[]
load=lambda name:[json.loads(s) for s in (R/'data'/name).read_text(encoding='utf-8').splitlines() if s.strip()]
sources={s['id']:s for s in load('sources.jsonl')};pub=load('publications.jsonl');docs=load('documents.jsonl')
if len({p['id'] for p in pub})!=len(pub):error.append('Duplicate publication ID')
if len({d['document_id'] for d in docs})!=len(docs):error.append('Duplicate document ID')
for p in pub:
 if p['source_id'] not in sources:error.append(p['id']+': missing master source')
 if p['source']!=sources.get(p['source_id'],{}).get('url'):error.append(p['id']+': source URL differs from master')
 if p['redistribution_class']=='eligible-after-download' and p['license']!='CC BY 4.0':error.append(p['id']+': license allowlist mismatch')
 if p['local_pdf'] is not None and not (R/p['local_pdf']).is_file():error.append(p['id']+': claimed local PDF missing')
for d in docs:
 if d['kind']=='external-publication' and d['document_id'] not in {p['id'] for p in pub}:error.append(d['document_id']+': external doc absent from publication catalog')
 if d['local_pdf_present']:
  f=R/d['local_pdf_path'] if d.get('local_pdf_path') else None
  if f is None or not f.is_file():error.append(d['document_id']+': absent file')
  elif not f.read_bytes().startswith(b'%PDF-'):error.append(d['document_id']+': invalid PDF signature')
  elif hashlib.sha256(f.read_bytes()).hexdigest()!=d['sha256']:error.append(d['document_id']+': SHA256 mismatch')
 elif d.get('local_pdf_path') or d.get('sha256'):error.append(d['document_id']+': unmirrored but claims path/hash')
for d in docs:
 if d.get('source_id') and d['source_id'] not in sources:error.append(d['document_id']+': unresolvable source ID')
print('SCIENCE AUDIT:',len(pub),'publication records;',sum(bool(d['local_pdf_present']) for d in docs),'local PDFs;',len(docs),'document records')
if error:
 for e in error:print('ERROR',e)
 sys.exit(1)
print('PASS: no dangling documents, rights or incorrect local PDF state')
