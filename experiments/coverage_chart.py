#!/usr/bin/env python3
"""Build original source-domain coverage graphic from actual catalog counts."""
from pathlib import Path
import json,collections
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
s=[json.loads(x) for x in (R/'data/sources.jsonl').read_text().splitlines() if x.strip()]
counts=collections.Counter(x.get('domain','unknown') for x in s)
keys,vals=zip(*sorted(counts.items(),key=lambda t:t[1],reverse=True))
fig,ax=plt.subplots(figsize=(9,4.8),layout='constrained')
ax.barh(list(keys)[::-1],list(vals)[::-1]);ax.set_xlim(0,max(vals)*1.16);ax.set_xlabel('Indexed source cards (not independent documents verified in full)');ax.set_title('Signal Atlas v0.4: source-distribution audit')
for i,v in enumerate(vals[::-1]):ax.text(v+.4,i,str(v),va='center')
ax.grid(axis='x',alpha=.23);fig.savefig(R/'assets/coverage_domains.svg',bbox_inches='tight');fig.savefig(R/'assets/coverage_domains.png',dpi=145,bbox_inches='tight');plt.close(fig)
(R/'data/experiments/coverage_counts_v04.json').write_text(json.dumps({'source_count':len(s),'by_domain':counts},indent=2)+'\n')
print(counts)
