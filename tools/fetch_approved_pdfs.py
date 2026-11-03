#!/usr/bin/env python3
"""Optional manual, rights-filtered PDF fetcher. Default dry run; does not run in CI."""
import argparse,hashlib,json,sys,urllib.request,urllib.error,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'data'/'publications.jsonl'
def main():
 ap=argparse.ArgumentParser(description='Fetch only individually CC BY 4.0 approved public PDFs')
 ap.add_argument('--download',action='store_true',help='actually fetch eligible PDFs (network required)')
 ap.add_argument('--id',action='append',help='publication ID; repeatable; defaults to all eligible')
 ap.add_argument('--max-mb',type=float,default=24,help='max PDF size per item, MB')
 a=ap.parse_args();pubs=[json.loads(x) for x in MANIFEST.read_text().splitlines() if x.strip()]
 found={p['id'] for p in pubs};requested=set(a.id or []);unknown=requested-found
 if unknown:raise SystemExit('Unknown IDs: '+', '.join(sorted(unknown)))
 selected=[p for p in pubs if (not requested or p['id'] in requested)]
 allowed=[p for p in selected if p.get('redistribution_class')=='eligible-after-download' and p.get('license')=='CC BY 4.0' and p.get('license_url')=='https://creativecommons.org/licenses/by/4.0/' and p.get('pdf_url','').startswith('https://')]
 print('License-allowlisted:',*[p['id'] for p in allowed],sep=' ')
 omitted=[p['id'] for p in selected if p not in allowed]
 if omitted:print('LINK ONLY / excluded:',', '.join(omitted))
 if not a.download:
  print('DRY RUN. Nothing fetched. Use --download when online, after confirming publisher reuse terms.');return 0
 target=ROOT/'documents/publications/third-party';target.mkdir(exist_ok=True,parents=True)
 for p in allowed:
  dest=target/(p['id']+'.pdf'); req=urllib.request.Request(p['pdf_url'],headers={'User-Agent':'SignalAtlasResearchLibrary/0.3 (public scholarly fetch)'})
  try:
   with urllib.request.urlopen(req,timeout=30) as response:
    payload=response.read(int(a.max_mb*1024*1024)+1)
   if len(payload)>a.max_mb*1024*1024:raise ValueError('PDF exceeds size limit')
   if not payload.startswith(b'%PDF-'):raise ValueError('Response is not a PDF')
   dest.write_bytes(payload);p['local_pdf']=str(dest.relative_to(ROOT));p['fulltext_status']='mirrored-license-reviewed';p['sha256']=hashlib.sha256(payload).hexdigest();p['retrieved_at_utc']='generated-by-local-fetch';print(p['id'],p['sha256'])
  except (OSError,urllib.error.URLError,ValueError) as e:
   print('SKIPPED',p['id'],str(e),file=sys.stderr)
  time.sleep(1.5)
 MANIFEST.write_text('\n'.join(json.dumps(p,ensure_ascii=False) for p in pubs)+'\n',encoding='utf-8')
 print('Review actual PDF/embedded third-party rights, then rerun validator and regenerate release manifest.')
 return 0
if __name__=='__main__':raise SystemExit(main())
