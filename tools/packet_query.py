#!/usr/bin/env python3
"""Read-only, bounded, provenance-first packet generation over local catalog metadata.

This is NOT an LLM or source verification, and does not download external pages.
"""
from pathlib import Path
import json, re, sys, hashlib, argparse
R=Path(__file__).resolve().parents[1]
D=R/'data'
def load(name):
    return [json.loads(s) for s in (D/name).read_text(encoding='utf-8').splitlines() if s.strip()]
def rank_source(s,terms):
    title=s['title'].casefold(); summary=s.get('summary','').casefold(); topics=str(s.get('topics','')).casefold()
    tail=(str(s.get('publisher',''))+' '+str(s.get('country',''))+' '+s.get('domain','')).casefold()
    full=' '.join([title,summary,topics,tail]);
    if any(t not in full for t in terms):return 0
    return 16*sum(t in title for t in terms)+6*sum(t in topics for t in terms)+3*sum(t in summary for t in terms)+sum(t in tail for t in terms)
def packet(query,limit=5,include_candidates=False):
    terms=[t.casefold() for t in re.findall(r'[\w]+',query,flags=re.UNICODE) if len(t)>1]
    if not terms:raise ValueError('Query must contain one or more meaningful terms')
    if not 1<=limit<=20:raise ValueError('limit must be 1..20')
    src=load('sources.jsonl'); claims=load('claims.jsonl')
    ranked=sorted((s for s in src if rank_source(s,terms)>0),key=lambda s:(-rank_source(s,terms),s['id']))[:limit]
    ids={s['id'] for s in ranked}
    cards=[{k:s.get(k) for k in ['id','title','publisher','country','domain','url','summary','rights','review_status','time_scope','checked_at','review_scope']} for s in ranked]
    bounded=[]
    for c in claims:
        overlap=ids.intersection(c['source_ids'])
        if overlap:
            bounded.append({'id':c['id'],'claim':c['claim'],'evidence_status':c['evidence_status'],'matched_source_ids':sorted(overlap),'all_claim_source_ids':c['source_ids'],'partial_evidence_selection':len(overlap)<len(c['source_ids'])})
    candidates=[]
    if include_candidates:
        for n in load('research_notes.jsonl'):
            if ids.intersection(n.get('source_ids',[])):
                candidates.append({'id':n['id'],'title':n['title'],'limitation':n.get('limitation'),'status':'candidate-not-validated'})
    output={'schema':'signal-atlas-research-packet/0.5','atlas_version':'0.5','query':query,'retrieval_method':'bounded title/topic/summary metadata rank; not web or PDF full text',
       'index_sha256':hashlib.sha256((D/'sources.jsonl').read_bytes()).hexdigest(),
       'sources':cards,'claims_attributed_to_sources':bounded,'candidate_notes_excluded_by_default':not include_candidates,
       'candidate_notes':candidates,'unresolved':[] if cards else ['No matching metadata card; research gap or query mismatch'],
       'caveats':['Source URLs may be stale since their last review.','Source cards summarize externally hosted material and do not contain that material.','Source self-description is not independent verification.','Payload size is not an inference cost measurement.']}
    material=json.dumps(output,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
    output['packet_sha256']=hashlib.sha256(material).hexdigest()
    return output
def main():
    p=argparse.ArgumentParser(description='Emit read-only, provenance-preserving research packet from curated metadata')
    p.add_argument('query',nargs='+');p.add_argument('--limit',type=int,default=5)
    p.add_argument('--include-candidates',action='store_true',help='include separately flagged provisional research notes')
    p.add_argument('--output',type=Path,help='optional explicit output destination')
    a=p.parse_args()
    out=packet(' '.join(a.query),a.limit,a.include_candidates)
    data=json.dumps(out,indent=2,ensure_ascii=False)+'\n'
    if a.output:a.output.write_text(data,encoding='utf-8')
    else:sys.stdout.write(data)
if __name__=='__main__':main()
