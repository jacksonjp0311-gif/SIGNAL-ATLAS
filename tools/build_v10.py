#!/usr/bin/env python3
"""Deterministically build Signal Atlas v1.0 from frozen local evidence."""
from __future__ import annotations
import csv, hashlib, json, re, subprocess, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATE="2026-11-03"
RAW="data/datasets/noaa_goes_primary_xrays_6hour_2026-11-03.json"
META="data/datasets/noaa_goes_primary_xrays_6hour_2026-11-03.metadata.json"
PAIR="data/datasets/noaa_goes_primary_xrays_6hour_paired_2026-11-03.json"
CSVPAIR="data/datasets/noaa_goes_primary_xrays_6hour_paired_2026-11-03.csv"
FIELDS=["id","title","publisher","country","domain","url","summary","source_type","time_scope","rights","review_status","added_at","topics","snapshot_status","language","checked_at","research_batch"]

SOURCES=[
{"id":"SRC-148","title":"Voices from the Past","publisher":"National Security Agency / Central Security Service","country":"United States","domain":"military-history","url":"https://www.nsa.gov/History/Cryptologic-History/Voices-from-the-Past/","summary":"NSA public-history page presenting audio and transcripts of cryptologic-history recollections, including wartime accounts.","source_type":"official oral-history collection","time_scope":"historical recollections; page checked 2026-11-03","rights":"link-only; reuse terms not assessed","review_status":"indexed; recollection attribution retained","added_at":DATE,"topics":["oral history","cryptologic history","world war ii"],"snapshot_status":"catalog-card-only","language":"en","checked_at":DATE,"research_batch":"v1.0-public-history"},
{"id":"SRC-149","title":"Did Signals Intelligence predict the attack on Pearl Harbor?","publisher":"Government Communications Headquarters (GCHQ)","country":"United Kingdom","domain":"military-history","url":"https://www.gchq.gov.uk/information/did-signals-intelligence-predict-attack-pearl-harbor","summary":"GCHQ historian's public interpretation of the Pearl Harbor warning question; retained as an attributed interpretation, not independent adjudication.","source_type":"official historian interpretation","time_scope":"historical question; page checked 2026-11-03","rights":"link-only; reuse terms not assessed","review_status":"indexed; interpretation attributed","added_at":DATE,"topics":["pearl harbor","SIGINT history","historical interpretation"],"snapshot_status":"catalog-card-only","language":"en","checked_at":DATE,"research_batch":"v1.0-public-history"},
{"id":"SRC-150","title":"History","publisher":"Australian Signals Directorate","country":"Australia","domain":"military-history","url":"https://www.asd.gov.au/about/history","summary":"ASD institutional history traces wartime antecedents and describes the Defence Signals Bureau's establishment and later organizational changes.","source_type":"official institutional history","time_scope":"1939 onward as described by ASD; page checked 2026-11-03","rights":"link-only; reuse terms not assessed","review_status":"indexed; institutional account attributed","added_at":DATE,"topics":["australia","institutional history","SIGINT history"],"snapshot_status":"catalog-card-only","language":"en","checked_at":DATE,"research_batch":"v1.0-public-history"},
{"id":"SRC-151","title":"What happened next for the codebreakers at the end of WWII","publisher":"Government Communications Headquarters (GCHQ)","country":"United Kingdom","domain":"military-history","url":"https://www.gchq.gov.uk/news/gchq-shares-what-happened-next-for-the-codebreakers","summary":"GCHQ's public historical article describes letters and postwar experiences of Bletchley Park personnel.","source_type":"official historical account with reproduced correspondence","time_scope":"post-1945; page checked 2026-11-03","rights":"link-only; reuse terms not assessed","review_status":"indexed; hosted material context attributed","added_at":DATE,"topics":["bletchley park","world war ii","postwar history","correspondence"],"snapshot_status":"catalog-card-only","language":"en","checked_at":DATE,"research_batch":"v1.0-public-history"},
{"id":"SRC-152","title":"GOES primary satellite X-ray flux, six-hour JSON product","publisher":"NOAA Space Weather Prediction Center","country":"United States","domain":"science","url":"https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json","summary":"Rolling six-hour primary GOES X-ray flux product. The frozen payload preserves timestamps, satellite identifier, band label, flux fields, and provider quality flags.","source_type":"official observation product","time_scope":"rolling six-hour product captured 2026-11-03 UTC","rights":"raw link and provenance retained; reuse terms not independently reviewed","review_status":"dated dataset snapshot included","added_at":DATE,"topics":["GOES","solar x-ray","space weather","observations","time series"],"snapshot_status":"dataset-snapshot-included","language":"en","checked_at":DATE,"research_batch":"v1.0-observations"}]

CLAIMS=[
{"id":"C-077","claim":"NSA's public historical-publications catalog organizes cryptologic-history material across periods that include the world wars, Korea, Vietnam, and the Cold War.","source_ids":["SRC-061"],"claim_type":"catalog-description","evidence_status":"institutional-catalog-description","review_date":DATE,"notes":"Describes catalog organization, not completeness of the historical record."},
{"id":"C-078","claim":"NSA's Voices from the Past page presents audio and transcript material for cryptologic-history recollections, including wartime accounts.","source_ids":["SRC-148"],"claim_type":"oral-history-collection-description","evidence_status":"institutional-collection-description","review_date":DATE,"notes":"Recollections are attributed testimony; consult the recording/transcript and context for event-specific use."},
{"id":"C-079","claim":"GCHQ's historian argues that signals intelligence did not provide a usable warning of the Pearl Harbor attack and discusses the radio-silence context.","source_ids":["SRC-149"],"claim_type":"historical-interpretation","evidence_status":"institutional-historian-interpretation","review_date":DATE,"notes":"Retained as GCHQ's interpretation; not relabeled as independent adjudication."},
{"id":"C-080","claim":"ASD's published institutional history states that the Defence Signals Bureau began on 1 April 1947.","source_ids":["SRC-150"],"claim_type":"institutional-chronology","evidence_status":"institutional-self-description","review_date":DATE,"notes":"Attributed to ASD; no present-capability inference is made."},
{"id":"C-081","claim":"GCHQ's postwar-history article describes correspondence and experiences of Bletchley Park personnel after the Second World War.","source_ids":["SRC-151"],"claim_type":"historical-publication-description","evidence_status":"institutional-publication-description","review_date":DATE,"notes":"Use each reproduced letter's author, date, and editorial context for specific claims."},
{"id":"C-082","claim":"The frozen NOAA GOES X-ray capture contains two energy-band labels and can be paired by shared timestamp and satellite without dropping or duplicating any retained channel rows.","source_ids":["SRC-152"],"claim_type":"dataset-structure-and-derived-join","evidence_status":"artifact-derived","review_date":DATE,"notes":"Checked against this snapshot and deterministic pairing code; applies to this capture, not cadence or climatology."}]

NOTE={"id":"NOTE-023","title":"Cross-scale observations need explicit joins","category":"Data integration and measurement","source_ids":["SRC-145","SRC-146","SRC-152"],"abstract":"Daily solar-radio and geomagnetic products sit alongside one-minute solar-wind and GOES X-ray products. Their units, time supports, locations, processing, and sampling differ. A join requires a documented shared key and purpose; coincident timestamps alone do not establish common origin, propagation delay, causality, or forecasting power.","limitation":"Bundled snapshots cover short and non-matching windows. The GOES pair is a structural two-channel join, not multi-instrument event attribution.","created_at":DATE,"review_status":"editorial-first-pass"}

def digest(b): return hashlib.sha256(b).hexdigest()
def canon(v): return digest(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode())
def loadj(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
def loadl(p): return [json.loads(x) for x in (ROOT/p).read_text(encoding="utf-8").splitlines() if x.strip()]
def savej(p,v): (ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def savel(p,rows):
 (ROOT/p).parent.mkdir(parents=True,exist_ok=True)
 (ROOT/p).write_text("".join(json.dumps(x,ensure_ascii=False,separators=(",",":"))+"\n" for x in rows),encoding="utf-8")
def add_rows(path,adds):
 rows=loadl(path);by={x["id"]:x for x in rows}
 for x in adds:
  if x["id"] in by and by[x["id"]]!=x: raise ValueError("Conflicting record "+x["id"])
  if x["id"] not in by: rows.append(x);by[x["id"]]=x
 savel(path,rows)
def pair_rows(rows):
 grouped=defaultdict(dict);labels={"0.05-0.4nm","0.1-0.8nm"}
 for row in rows:
  key=(row.get("time_tag"),row.get("satellite"));band=row.get("energy")
  if not isinstance(key[0],str) or not isinstance(key[1],int) or band not in labels: raise ValueError("Bad GOES key or band")
  if band in grouped[key]: raise ValueError("Duplicate GOES channel key "+str(key))
  for field in ["flux","observed_flux","electron_correction"]:
   if not isinstance(row.get(field),(int,float)) or row[field]<0: raise ValueError("Invalid GOES field "+field)
  if not isinstance(row.get("electron_contaminaton"),bool): raise ValueError("Missing GOES quality flag")
  grouped[key][band]=row
 result=[]
 for (tag,sat),bands in sorted(grouped.items()):
  if set(bands)!=labels: continue
  a,b=bands["0.05-0.4nm"],bands["0.1-0.8nm"]
  result.append({"time_tag":tag,"satellite":sat,"flux_0_05_0_4_W_m2":a["flux"],"flux_0_1_0_8_W_m2":b["flux"],"observed_flux_0_05_0_4_W_m2":a["observed_flux"],"observed_flux_0_1_0_8_W_m2":b["observed_flux"],"electron_correction_0_05_0_4_W_m2":a["electron_correction"],"electron_correction_0_1_0_8_W_m2":b["electron_correction"],"electron_contaminaton_0_05_0_4":a["electron_contaminaton"],"electron_contaminaton_0_1_0_8":b["electron_contaminaton"]})
 return result
def savej(p,v): (ROOT/p).parent.mkdir(parents=True,exist_ok=True);(ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
def build():
 rawp=ROOT/RAW;metap=ROOT/META
 if not rawp.is_file() or not metap.is_file():raise FileNotFoundError("Frozen NOAA snapshot and metadata required.")
 rawbytes=rawp.read_bytes();meta=loadj(META)
 if digest(rawbytes)!=meta["raw_sha256"]:raise ValueError("Raw NOAA snapshot hash mismatch.")
 rows=json.loads(rawbytes.decode("utf-8"))
 if len(rows)!=meta["record_count"]:raise ValueError("NOAA record count mismatch.")
 paired=pair_rows(rows)
 savej(PAIR,{"dataset_id":"DS-GOES-XRS-PAIRED-2026-11-03","record_count":len(paired),"records":paired,"join_key":["time_tag","satellite"],"source_files":[RAW],"method":"Exact matching of timestamp and satellite for one record in each reported energy band; no imputation or interpolation."})
 fields=list(paired[0]) if paired else ["time_tag","satellite"]
 with (ROOT/CSVPAIR).open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(paired)
 add_rows("data/sources.jsonl",SOURCES);add_rows("data/claims.jsonl",CLAIMS);add_rows("data/research_notes.jsonl",[NOTE])
 src=loadl("data/sources.jsonl")
 with (ROOT/"data/sources.csv").open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=FIELDS,extrasaction="ignore",lineterminator="\n");w.writeheader()
  for x in src:w.writerow({**x,"topics":json.dumps(x.get("topics",[]),ensure_ascii=False,separators=(",",":"))})
 rp=ROOT/"data/relationships.jsonl";rels=[json.loads(x) for x in rp.read_text(encoding="utf-8").splitlines() if x.strip()];known={(x.get("from"),x.get("relation",x.get("relationship","")),x.get("to")) for x in rels}
 for c in CLAIMS:
  for sid in c["source_ids"]:
   key=(c["id"],"supported_or_attributed_to",sid)
   if key not in known:rels.append({"from":key[0],"relation":key[1],"to":key[2]});known.add(key)
 for sid in NOTE["source_ids"]:
  key=("NOTE-023","informed_by",sid)
  if key not in known:rels.append({"from":key[0],"relation":key[1],"to":key[2]});known.add(key)
 rp.write_text("".join(json.dumps(x,separators=(",",":"))+"\n" for x in rels),encoding="utf-8")
 reg=loadj("data/dataset_registry.json");reg["atlas_version"]="1.0"
 obs={"dataset_id":"DS-GOES-XRS-PRIMARY-6H-2026-11-03","title":"NOAA primary GOES soft X-ray flux, frozen six-hour observation snapshot","kind":"observed","date_start":meta["time_tag_start"][:10],"date_end":meta["time_tag_end"][:10],"record_count":len(rows),"units":"W m^-2 in the provider flux fields; original field names retained","source_ids":["SRC-152"],"files":[{"path":RAW,"format":"json","sha256":digest(rawbytes),"role":"raw upstream payload"},{"path":META,"format":"json","sha256":digest(metap.read_bytes()),"role":"capture integrity metadata"}],"provenance_record":"data/provenance/release_v10_sources.jsonl:PROV-V10-NOAA-XRS-RAW","data_character":str(len(rows))+" raw rows; two band labels; captured "+meta["captured_before_utc"]+"."}
 der={"dataset_id":"DS-GOES-XRS-PAIRED-2026-11-03","title":"NOAA primary GOES X-ray flux, exact timestamp and satellite channel pairs","kind":"derived","date_start":meta["time_tag_start"][:10],"date_end":meta["time_tag_end"][:10],"record_count":len(paired),"units":"W m^-2; raw and observed flux fields remain separate","source_ids":["SRC-152"],"files":[{"path":PAIR,"format":"json","sha256":digest((ROOT/PAIR).read_bytes()),"role":"exact channel pairing"},{"path":CSVPAIR,"format":"csv","sha256":digest((ROOT/CSVPAIR).read_bytes()),"role":"tabular exact channel pairing"}],"provenance_record":"data/provenance/release_v10_sources.jsonl:PROV-V10-NOAA-XRS-PAIR","data_character":"One row per exact timestamp and satellite match containing both bands; no cross-instrument or causal join."}
 ds={x["dataset_id"]:x for x in reg["datasets"]};ds[obs["dataset_id"]]=obs;ds[der["dataset_id"]]=der;reg["datasets"]=[ds[k] for k in sorted(ds)];savej("data/dataset_registry.json",reg)
 prov=[]
 for s in SOURCES:prov.append({"record_id":"PROV-V10-"+s["id"],"record_kind":"cataloged_public_source","source_id":s["id"],"source_url":s["url"],"publisher":s["publisher"],"record_type":s["source_type"],"scope_note":s["summary"],"checked_at":DATE,"capture_status":s["snapshot_status"],"reuse_note":s["rights"]})
 prov += [{"record_id":"PROV-V10-NOAA-XRS-RAW","record_kind":"captured_observation_snapshot","source_id":"SRC-152","source_url":meta["source_url"],"path":RAW,"sha256":meta["raw_sha256"],"byte_count":meta["byte_count"],"record_count":meta["record_count"],"time_tag_start":meta["time_tag_start"],"time_tag_end":meta["time_tag_end"],"captured_before_utc":meta["captured_before_utc"],"captured_after_utc":meta["captured_after_utc"],"http_last_modified":meta.get("http_last_modified"),"http_etag":meta.get("http_etag"),"preservation":"Raw response bytes preserved."},{"record_id":"PROV-V10-NOAA-XRS-PAIR","record_kind":"deterministic_derivation","source_ids":["SRC-152"],"input_paths":[RAW],"input_sha256":meta["raw_sha256"],"output_paths":[PAIR,CSVPAIR],"join_key":["time_tag","satellite"],"energy_labels":["0.05-0.4nm","0.1-0.8nm"],"output_record_count":len(paired),"code_path":"tools/build_v10.py","limitations":"No interpolation, imputation, resampling, external joins or causal claim."}]
 savel("data/provenance/release_v10_sources.jsonl",prov)
 savej("data/discovery_batches/2026-11-03-v1.0.json",{"batch_id":"SIGNAL-ATLAS-v1.0-2026-11-03","release_version":"1.0","purpose":"Add public-history routes and a frozen GOES X-ray snapshot; unify navigation and coverage.","source_ids":[x["id"] for x in SOURCES],"claim_ids":[x["id"] for x in CLAIMS],"dataset_ids":[obs["dataset_id"],der["dataset_id"]],"note_ids":["NOTE-023"],"checked_at":DATE,"limitations":["History descriptions remain publisher-attributed.","GOES is a short rolling capture.","No unmeasured causal relation or prediction is inferred."]})
 write_research_docs(meta,len(paired));write_svg();update_navigation(len(src),len(loadl("data/claims.jsonl")),len(loadl("data/research_notes.jsonl")))
 subprocess.check_call([sys.executable,"-B",str(ROOT/"tools/build_atlas_index.py")],cwd=ROOT)
 index,manifest=build_search();build_packet(index,manifest);counts={"sources":len(src),"claims":len(loadl("data/claims.jsonl")),"notes":len(loadl("data/research_notes.jsonl")),"publications":len(loadl("data/publications.jsonl")),"lessons":sum(1 for p in (ROOT/"courses").glob("[0-9]*.md") if re.match(r"^\d+[-_]",p.stem)),"datasets":len(reg["datasets"])}
 coverage=build_coverage(index,counts);write_search_html(index);write_coverage_html(coverage);write_release_docs(counts,meta,len(paired));build_lineage()
 print(json.dumps({**counts,"goes_raw_rows":len(rows),"goes_paired_rows":len(paired),"search_entries":index["entry_count"],"search_manifest_sha256":manifest["manifest_sha256"]},indent=2))

def write_research_docs(meta,pairs):
 (ROOT/"docs/research/PUBLIC_HISTORICAL_RECORDS_v10.md").write_text("""# Public historical SIGINT records added in v1.0

This batch adds public records and accounts from NSA and GCHQ, plus ASD's institutional history. It keeps record types distinct so readers can follow a useful research route.

| ID | Record kind | Use | Boundary |
| --- | --- | --- | --- |
| SRC-061 | NSA history-publication catalog | Find public studies across periods and topics. | Catalog is a route, not the complete record. |
| SRC-148 | NSA recollection collection | Locate audio and transcript testimony. | Preserve speaker, date, and context. |
| SRC-149 | GCHQ historian interpretation | Study the Pearl Harbor warning question. | Attribute the interpretation; not independent adjudication. |
| SRC-150 | ASD institutional history | Follow the agency's published chronology. | Self-description, not current capability. |
| SRC-151 | GCHQ postwar account | Find letters and accounts about Bletchley personnel. | Keep writer, date, and editorial context attached. |

## Workflow

1. Classify the evidence: catalog, released record, recollection, institutional history, or historian's interpretation.
2. Open the original material and note creator, date, holder, release context, and scope.
3. Keep testimony and inference separate; cite a specific item for an event claim.
4. Use [offline search](../../site/unified_search.html) and [coverage](../../site/coverage.html) to explore related records and collection gaps.

Claims C-077 through C-081 retain publisher attribution. Public access does not establish historical completeness.

## Original records

- [NSA Historical Publications](https://www.nsa.gov/serve-from-netstorage/History/Cryptologic-History/Historical-Publications/index.html) — SRC-061.
- [NSA Voices from the Past](https://www.nsa.gov/History/Cryptologic-History/Voices-from-the-Past/) — SRC-148.
- [GCHQ historian on Pearl Harbor](https://www.gchq.gov.uk/information/did-signals-intelligence-predict-attack-pearl-harbor) — SRC-149.
- [ASD history](https://www.asd.gov.au/about/history) — SRC-150.
- [GCHQ postwar correspondence article](https://www.gchq.gov.uk/news/gchq-shares-what-happened-next-for-the-codebreakers) — SRC-151.

![Signal Atlas public-history provenance route](../../assets/unified_atlas_navigation_v10.svg)
""",encoding="utf-8")
 text="# NOAA GOES soft X-ray observations\n\nSignal Atlas v1.0 preserves "+str(meta["record_count"])+" raw rows from NOAA SWPC's [primary GOES six-hour X-ray product](https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json), timestamped "+meta["time_tag_start"]+" through "+meta["time_tag_end"]+". Capture time: "+meta["captured_before_utc"]+". Raw-response SHA-256 and HTTP metadata are stored with the bytes.\n\nThe payload includes the 0.05-0.4nm and 0.1-0.8nm energy labels. The paired JSON and CSV contain "+str(pairs)+" exact (time_tag, satellite) matches. Provider flux, observed_flux, correction, and contamination fields remain separate, including the original field spelling.\n\n## Limits\n\n- A rolling six-hour capture is not a long-term archive.\n- Pairing is exact; no interpolation, smoothing, time shifting, or cross-instrument joining is done.\n- Timestamp coincidence with solar wind, magnetic field, F10.7, or Kp is not proof of shared cause or forecasting value.\n- Quality flags are preserved, not independently calibrated.\n\n## Rebuild\n\n~~~powershell\npython tools/build_v10.py\npython tools/atlas_search_v10.py \"GOES x-ray flux\" --kind dataset\npython tools/validate_v10.py\n~~~\n\nObtain a new rolling capture only with the explicit dated fetch tool; do not overwrite frozen evidence. See the [registry](../../data/dataset_registry.json), [paired CSV](../../data/datasets/noaa_goes_primary_xrays_6hour_paired_2026-11-03.csv), and source provenance.\n"
 (ROOT/"docs/science/09_goes_xray_flux_observations.md").write_text(text,encoding="utf-8")
 (ROOT/"docs/research/DATA_COLLECTION_GUIDE_v10.md").write_text("""# Collection and compilation guide v1.0

## Goal

Compile useful public observations and research records while keeping each item's origin, time basis, units, evidence role, and limitation attached.

## Collection steps

1. Record the publisher, exact URL, UTC capture interval, response metadata, raw bytes and SHA-256, row count, fields, time coverage, units, and quality flags.
2. Store new captures under dated names; never overwrite an earlier release.
3. Check parseability, required fields, dates, duplicate keys, and data kind: observed, derived, or synthetic.
4. Keep derived joins separate. State the exact key and unmatched-row rule.
5. Update the dataset registry and provenance ledger with source IDs and file hashes.
6. Rebuild SQLite and unified search from frozen local inputs.
7. Use the coverage view to find time gaps, domain imbalance, and missing routes.
8. Run focused checks and record commands, results, and limitations.

The [coverage view](../../site/coverage.html) separates 10 registrations: daily F10.7 and estimated Kp, minute-scale plasma and magnetic field, explicit joins and context views, a synthetic lab, and a six-hour GOES X-ray capture with paired channels.

These records are not one continuous or interchangeable time series. Future captures should extend the dated evidence rather than replace earlier windows. Ordinary builds and tests do not fetch live data.
""",encoding="utf-8")
 (ROOT/"docs/research/UNIFIED_SEARCH_AND_COVERAGE_v10.md").write_text("""# Unified search and collection coverage

## Search behavior

The v1.0 index combines source cards, scoped claims, research notes, publication records, dataset registrations, numbered lessons, selected research Markdown, and project navigation. The index is data/unified_search_index_v10.json; its input paths and SHA-256 values are in data/unified_search_manifest_v10.json.

Queries use case-insensitive lexical matching. All typed terms must occur. Title matches rank above topic matches, then summaries; ties are stable by title and ID. Filters include item kind, domain, country, data kind, and inclusive date-window overlap. The CLI reads only the bundled JSON index. The browser page embeds the same catalog and makes no search network requests.

## Coverage behavior

The coverage report summarizes records and registered files in this release, with date bounds and known gaps. It describes the package contents, not global sensor footprints or field-wide completeness.

## Reproducibility and limits

Run tools/build_v10.py to rebuild from frozen local ledgers, documents, registry, and raw snapshot. Input hashes are recalculated. Search does not fetch web pages, read PDF bodies, use embeddings, assess truth, or generate answers. It is a navigational index for finding and reusing material.

The example packet binds result records to the search index and input manifest with SHA-256. This supports integrity checking, not the correctness of external sources.
""",encoding="utf-8")
 (ROOT/"courses/29-public-sigint-history.md").write_text("""# Lesson 29: Navigate public SIGINT history

## Outcome

Use a source catalog, oral recollection, institutional history, and historian's interpretation without treating them as the same evidence.

## Activity

1. Open the [public history guide](../docs/research/PUBLIC_HISTORICAL_RECORDS_v10.md).
2. Search cryptologic history in [offline unified search](../site/unified_search.html).
3. Choose two different record roles. Record publisher or creator, type, date, underlying item, and what it directly supports.
4. Write one attributed statement and one question the items cannot resolve.
5. Explain why a catalog is not the same as the document it points to.

A strong answer follows the source to its original page or item, distinguishes testimony from interpretation, and names a concrete limit. Atlas summaries are navigation aids, not substitutes for original material.
""",encoding="utf-8")
 (ROOT/"courses/30-compile-observations-and-provenance.md").write_text("""# Lesson 30: Compile observations without flattening them

## Outcome

Build a useful collection that keeps observation, derivation, and simulation distinct and makes every item findable again.

## Activity

1. Trace an observed dataset from its source URL to raw hash, capture record, and registry row.
2. Trace a derived dataset and identify its exact join key and unmatched-row rule.
3. Inspect the synthetic frequency-stability exercise and explain why it is not an observation.
4. Compare minute-scale solar-wind and GOES records with daily F10.7 and Kp.
5. Use offline search to build a packet naming source IDs, time window, data kind, and one limitation.

A strong answer preserves units and dates, avoids undocumented joins, and distinguishes “stored in the library” from complete coverage. Search finds material; it does not prove a claim.
""",encoding="utf-8")

def write_svg():
 (ROOT/"assets/unified_atlas_navigation_v10.svg").write_text("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600" role="img" aria-labelledby="t d"><title id="t">Signal Atlas collection and navigation</title><desc id="d">Public records and data are preserved, classified, connected with explicit keys, then searched, taught, and reused with gaps visible.</desc><rect width="1200" height="600" rx="24" fill="#071523"/><text x="50" y="58" fill="#63ddd1" font-size="30" font-family="Arial">SIGNAL ATLAS / COLLECT → TRACE → REUSE</text><g fill="#10283b" stroke="#59d5cf" stroke-width="3"><rect x="50" y="130" width="230" height="135" rx="18"/><rect x="340" y="130" width="230" height="135" rx="18"/><rect x="630" y="130" width="230" height="135" rx="18"/><rect x="920" y="130" width="230" height="135" rx="18"/><rect x="210" y="370" width="300" height="140" rx="18"/><rect x="680" y="370" width="340" height="140" rx="18"/></g><g fill="#edf3f1" font-size="23" font-family="Arial" font-weight="bold"><text x="80" y="180">Collect</text><text x="370" y="180">Preserve</text><text x="660" y="180">Classify</text><text x="950" y="180">Connect</text><text x="240" y="420">Navigate and teach</text><text x="710" y="420">Reuse with context</text></g><g fill="#a8bec5" font-size="17" font-family="Arial"><text x="80" y="218">Public records + data</text><text x="370" y="218">Original bytes + UTC</text><text x="660" y="218">Observed / derived</text><text x="950" y="218">Explicit keys only</text><text x="240" y="458">Offline search + lessons</text><text x="710" y="458">Packets + open gaps</text><text x="150" y="560">Every item keeps origin, time window, type, method, and limitation.</text></g><g stroke="#e4b577" stroke-width="4" fill="none"><path d="M280 198h55"/><path d="M570 198h55"/><path d="M860 198h55"/><path d="M1030 265c0 60-180 50-180 100"/><path d="M680 440H520"/></g></svg>\n""",encoding="utf-8")

def build_search():
 src=loadl("data/sources.jsonl");cl=loadl("data/claims.jsonl");notes=loadl("data/research_notes.jsonl");pub=loadl("data/publications.jsonl");reg=loadj("data/dataset_registry.json")
 domains={s["id"]:s["domain"] for s in src};entries=[];inputs={"data/sources.jsonl","data/claims.jsonl","data/research_notes.jsonl","data/publications.jsonl","data/dataset_registry.json"}
 def add(x):
  x["topics"]=x.get("topics",[]) or [];x["source_ids"]=x.get("source_ids",[]) or [];x["dataset_ids"]=x.get("dataset_ids",[]) or []
  x["search_text"]=" ".join(str(z) for z in [x.get("title",""),x.get("summary",""),x.get("domain",""),x.get("country","")," ".join(x["topics"]),x.get("body","")]);x["search_text"]=" ".join(x["search_text"].split())[:30000];entries.append(x)
 for x in src:add({"id":x["id"],"kind":"source","title":x["title"],"summary":x.get("summary",""),"path":"data/sources.jsonl","url":x["url"],"domain":x["domain"],"country":x["country"],"date_start":None,"date_end":None,"data_kind":None,"topics":x.get("topics",[]),"source_ids":[x["id"]],"body":x.get("publisher","")})
 for x in cl:
  ds=sorted({domains.get(s,"") for s in x.get("source_ids",[]) if domains.get(s)})
  add({"id":x["id"],"kind":"claim","title":x["claim"],"summary":x.get("notes",""),"path":"data/claims.jsonl","url":None,"domain":ds[0] if len(ds)==1 else "cross-domain","country":"","date_start":None,"date_end":None,"data_kind":None,"topics":[],"source_ids":x.get("source_ids",[]),"body":x.get("evidence_status","")})
 for x in notes:add({"id":x["id"],"kind":"research_note","title":x["title"],"summary":x.get("abstract",""),"path":"data/research_notes.jsonl","url":None,"domain":x.get("category",""),"country":"","date_start":None,"date_end":None,"data_kind":None,"topics":[],"source_ids":x.get("source_ids",[]),"body":x.get("limitation","")})
 for x in pub:add({"id":x["id"],"kind":"publication","title":x["title"],"summary":x.get("summary",""),"path":"documents/publications/reference-cards/"+x["id"]+".md","url":x.get("source"),"domain":"science","country":"","date_start":None,"date_end":None,"data_kind":None,"topics":x.get("topics",[]),"source_ids":[x["source_id"]] if x.get("source_id") else [],"body":x.get("publisher","")})
 for x in reg["datasets"]:
  fs=x.get("files",[])
  add({"id":x["dataset_id"],"kind":"dataset","title":x["title"],"summary":x.get("data_character",x.get("units","")),"path":fs[0]["path"] if fs else "data/dataset_registry.json","url":None,"domain":"science","country":"International","date_start":x.get("date_start"),"date_end":x.get("date_end"),"data_kind":x.get("kind"),"topics":[],"source_ids":x.get("source_ids",[]),"dataset_ids":[x["dataset_id"]],"body":x.get("units","")})
 dirs=["docs/science","docs/spectrum","docs/technology","docs/military","docs/regions","docs/applications","docs/research","courses","experiments","documents/publications/reference-cards"];paths=set()
 for d in dirs:
  folder=ROOT/d
  if folder.exists():
   for p in folder.rglob("*.md"):
    if p.name.upper().startswith(("RELEASE_SUMMARY_","RELEASE_AUDIT_")) or p.name=="INSTRUCTOR_NOTES.md":continue
    paths.add(p)
 paths.update(ROOT/x for x in ["README.md","START-HERE.md","AGENTS.md","RESEARCH_METHOD.md"])
 for p in sorted(paths):
  rel=p.relative_to(ROOT).as_posix();body=p.read_text(encoding="utf-8");title=next((l.lstrip("# ").strip() for l in body.splitlines() if l.startswith("# ")),p.stem.replace("_"," "));summary=" ".join(body.split())[:650]
  domain="education" if rel.startswith("courses/") else ("military-history" if rel.startswith("docs/military/") else (Path(rel).parts[1] if rel.startswith("docs/") else "science" if rel.startswith(("experiments/","documents/")) else "project-navigation"))
  ids=sorted(set(re.findall(r"SRC-\d{3}",body)));dids=sorted(set(re.findall(r"DS-[A-Z0-9-]+",body)))
  add({"id":"DOC:"+rel,"kind":"document","title":title,"summary":summary,"path":rel,"url":None,"domain":domain,"country":"","date_start":None,"date_end":None,"data_kind":None,"topics":[],"source_ids":ids,"dataset_ids":dids,"body":body});inputs.add(rel)
 entries.sort(key=lambda x:(x["kind"],x["id"]))
 manifest={"schema_version":1,"release_version":"1.0","inputs":[{"path":r,"sha256":digest((ROOT/r).read_bytes()),"bytes":(ROOT/r).stat().st_size} for r in sorted(inputs)],"entry_count":len(entries),"entry_kind_counts":dict(sorted(Counter(x["kind"] for x in entries).items()))}
 manifest["manifest_sha256"]=canon(manifest);savej("data/unified_search_manifest_v10.json",manifest)
 index={"schema_version":1,"release_version":"1.0","method":"Deterministic local lexical search; all query terms must occur; no live network, embeddings, or LLM ranking.","manifest_path":"data/unified_search_manifest_v10.json","manifest_sha256":manifest["manifest_sha256"],"entry_count":len(entries),"entries":entries}
 savej("data/unified_search_index_v10.json",index);return index,manifest

def build_coverage(index,counts):
 reg=loadj("data/dataset_registry.json");src=loadl("data/sources.jsonl")
 report={"release_version":"1.0","report_date":DATE,"counts":{**counts,"search_documents":sum(1 for x in index["entries"] if x["kind"]=="document"),"svg_graphics":len(list((ROOT/"assets").glob("*.svg")))},"source_domain_counts":dict(sorted(Counter(x.get("domain","other") for x in src).items())),"dataset_kind_counts":dict(sorted(Counter(x.get("kind","unspecified") for x in reg["datasets"]).items())),"datasets":[{"dataset_id":x["dataset_id"],"title":x["title"],"kind":x.get("kind","unspecified"),"date_start":x.get("date_start"),"date_end":x.get("date_end"),"record_count":x.get("record_count"),"source_ids":x.get("source_ids",[]),"files":[{"path":f["path"],"sha256":f["sha256"]} for f in x.get("files",[])]} for x in reg["datasets"]],"gaps":[{"title":"No continuous archive","detail":"The GOES addition is one rolling six-hour capture. Prior one-minute wind and daily products cover different windows."},{"title":"Different quantities and time supports","detail":"Daily F10.7 and estimated Kp, minute-scale solar wind, and GOES X-rays are not interchangeable. Joins need an explicit key and purpose."},{"title":"Selective history and science coverage","detail":"26 publication records and a few public history routes do not measure field-wide or archival completeness."},{"title":"Lexical search limits","detail":"Search covers bundled metadata and selected Markdown; it does not index remote pages or PDF full text or judge truth."}]}
 savej("data/coverage_report_v10.json",report);return report

def build_packet(index,manifest):
 import sys
 sys.path.insert(0,str(ROOT/"tools"))
 from atlas_search_core_v10 import search_entries
 hits=search_entries(index,"GOES X-ray flux",kind="dataset",limit=8)
 packet={"schema_version":"1.0","packet_id":"ATLAS-QUERY-GOES-XRAY-2026-11-03","release_version":"1.0","query":"GOES X-ray flux","filters":{"kind":"dataset"},"method":index["method"],"inputs":{"index_path":"data/unified_search_index_v10.json","index_sha256":digest((ROOT/"data/unified_search_index_v10.json").read_bytes()),"manifest_path":"data/unified_search_manifest_v10.json","manifest_sha256":manifest["manifest_sha256"]},"results":[{k:h.get(k) for k in ["id","kind","title","summary","path","url","domain","country","date_start","date_end","data_kind","source_ids","dataset_ids","score"]} for h in hits],"limitations":["Lexical metadata retrieval, not full-text or semantic search.","A matching record does not independently verify its source.","Snapshot windows are short and cross-product matches do not establish causality."]}
 packet["packet_sha256"]=canon(packet)
 savej("data/packets/examples/atlas-cross-domain-research.v1.0.packet.json",packet)

def write_search_html(index):
 data=json.dumps(index["entries"],ensure_ascii=False,separators=(",",":")).replace("&","\\u0026").replace("<","\\u003c").replace(">","\\u003e")
 page="""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SIGNAL ATLAS — Unified Search</title><style>
:root{color-scheme:dark;--bg:#071523;--panel:#10283b;--line:#37566b;--teal:#63ddd1;--warm:#f0ad74;--ink:#edf3f1;--muted:#a8bec5}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:28px 22px 64px}a{color:var(--teal)}nav{margin:18px 0}.muted{color:var(--muted)}.controls{display:grid;grid-template-columns:2fr repeat(4,1fr);gap:10px;background:var(--panel);padding:16px;border:1px solid var(--line);border-radius:14px;margin:20px 0}input,select{min-width:0;background:#071a2a;color:var(--ink);border:1px solid var(--line);padding:11px;border-radius:8px}#status{color:var(--warm);font:700 12px ui-monospace,monospace;margin:15px 0}.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px;margin:11px 0}.tags{font:700 11px ui-monospace,monospace;color:var(--warm)}.card h2{font-size:20px;margin:9px 0}.meta{color:var(--muted);font-size:13px}.empty{padding:30px;background:var(--panel)}@media(max-width:800px){.controls{grid-template-columns:1fr 1fr}}@media(max-width:550px){.controls{grid-template-columns:1fr}}
</style></head><body><main><p class="muted">SIGNAL ATLAS / OFFLINE COLLECTION</p><h1>Unified Search</h1><p class="muted">Search source cards, claims, datasets, publications, lessons, notes, and selected research documents. Search data is bundled; original-source links require internet access.</p><nav><a href="../README.md">Start</a> · <a href="coverage.html">Dataset coverage</a> · <a href="index.html">Source explorer</a></nav><p class="muted">Search results are navigation aids, not independent verification.</p><div class="controls"><input id="q" type="search" placeholder="solar wind, GOES x-ray, Pearl Harbor" aria-label="Search"><select id="kind"><option value="">All record types</option></select><select id="domain"><option value="">All areas</option></select><select id="dataKind"><option value="">All data kinds</option><option>observed</option><option>derived</option><option>synthetic</option></select><select id="country"><option value="">All countries</option></select><input id="from" type="date" aria-label="Date from"><input id="to" type="date" aria-label="Date to"></div><div id="status" role="status" aria-live="polite"></div><section id="results"></section></main><script id="catalog" type="application/json">@@INDEX@@</script><script>
const D=JSON.parse(document.getElementById('catalog').textContent),$=id=>document.getElementById(id),e=s=>String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function opts(id,vals){[...new Set(vals.filter(Boolean))].sort().forEach(v=>{let o=document.createElement('option');o.value=v;o.textContent=v;$(id).appendChild(o)})}opts('kind',D.map(x=>x.kind));opts('domain',D.map(x=>x.domain));opts('country',D.map(x=>x.country));
function render(){let terms=$('q').value.toLowerCase().trim().split(/\\s+/).filter(Boolean),kind=$('kind').value,domain=$('domain').value,dk=$('dataKind').value,country=$('country').value,from=$('from').value,to=$('to').value;
let rows=D.filter(x=>(!kind||x.kind===kind)&&(!domain||x.domain===domain)&&(!dk||x.data_kind===dk)&&(!country||x.country===country)&&(!from||(x.date_end&&x.date_end>=from))&&(!to||(x.date_start&&x.date_start<=to)));
rows=rows.filter(x=>terms.every(t=>x.search_text.toLowerCase().includes(t))).map(x=>{let score=0;for(const t of terms){if(x.title.toLowerCase().includes(t))score+=5;if(x.topics.some(z=>z.toLowerCase().includes(t)))score+=3;if(x.summary.toLowerCase().includes(t))score+=2;score++}return{x,score}}).sort((a,b)=>b.score-a.score||a.x.title.localeCompare(b.x.title)||a.x.id.localeCompare(b.x.id));
$('status').textContent=rows.length+' results / '+D.length+' indexed items';let out=$('results');out.replaceChildren();if(!rows.length){out.innerHTML='<div class="empty">Nothing matches. Broaden the search or check the coverage view.</div>';return}
rows.slice(0,100).forEach(o=>{let x=o.x,url=x.url||('../'+(x.path.startsWith('/')?x.path.slice(1):x.path)),external=!!x.url,el=document.createElement('article');el.className='card';el.innerHTML='<div class="tags">'+e(x.kind)+' / '+e(x.domain)+(x.data_kind?' / '+e(x.data_kind):'')+' / '+e(x.id)+'</div><h2><a href="'+e(url)+'" '+(external?'target="_blank" rel="noopener noreferrer"':'')+'>'+e(x.title)+'</a></h2><p>'+e(x.summary)+'</p><p class="meta">'+(x.country?e(x.country)+' · ':'')+(x.date_start?e(x.date_start)+' to '+e(x.date_end):'')+(x.source_ids.length?' · Sources: '+e(x.source_ids.join(', ')):'')+' · score '+o.score+'</p>';out.appendChild(el)})}
['q','kind','domain','dataKind','country','from','to'].forEach(id=>$(id).addEventListener(id==='q'?'input':'change',render));render();
</script></body></html>"""
 (ROOT/"site/unified_search.html").write_text(page.replace("@@INDEX@@",data),encoding="utf-8")
def write_coverage_html(report):
 data=json.dumps(report,ensure_ascii=False,separators=(",",":")).replace("&","\\u0026").replace("<","\\u003c").replace(">","\\u003e")
 page="""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SIGNAL ATLAS — Data Coverage</title><style>:root{color-scheme:dark;--bg:#071523;--panel:#10283b;--line:#37566b;--teal:#63ddd1;--ink:#edf3f1;--muted:#a8bec5}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:28px 22px 60px}a{color:var(--teal)}.muted{color:var(--muted)}nav{margin:18px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}.card,.table{background:var(--panel);border:1px solid var(--line);border-radius:13px;padding:17px;margin:14px 0}.num{font-size:28px;color:var(--teal);font-weight:750}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:9px;border-bottom:1px solid var(--line);vertical-align:top}@media(max-width:700px){.table{overflow:auto}}</style></head><body><main><p class="muted">SIGNAL ATLAS / COLLECTION MAP</p><h1>What is in the library?</h1><p class="muted">Release-time summary of registered catalog items and files; not global sensor coverage or scientific completeness.</p><nav><a href="../README.md">Start</a> · <a href="unified_search.html">Unified search</a> · <a href="index.html">Source explorer</a></nav><div id="cards" class="grid"></div><h2>Registered datasets</h2><div class="table"><table><thead><tr><th>Dataset</th><th>Kind</th><th>Dates</th><th>Rows</th><th>Files</th></tr></thead><tbody id="datasets"></tbody></table></div><h2>Source areas</h2><div id="domains" class="grid"></div><h2>Collection gaps</h2><div id="gaps"></div><p class="muted">Read the <a href="../docs/research/DATA_COLLECTION_GUIDE_v10.md">collection guide</a> before adding a dated capture.</p></main><script id="report" type="application/json">@@REPORT@@</script><script>
const R=JSON.parse(document.getElementById('report').textContent),e=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let cards=[['Sources',R.counts.sources],['Claims',R.counts.claims],['Lessons',R.counts.lessons],['Publications',R.counts.publications],['Datasets',R.counts.datasets],['Searchable documents',R.counts.search_documents]];
document.getElementById('cards').innerHTML=cards.map(x=>'<article class="card"><div class="num">'+e(x[1])+'</div>'+e(x[0])+'</article>').join('');
document.getElementById('datasets').innerHTML=R.datasets.map(d=>'<tr><td><b>'+e(d.dataset_id)+'</b><br>'+e(d.title)+'</td><td>'+e(d.kind)+'</td><td>'+e(d.date_start||'unspecified')+' to '+e(d.date_end||'unspecified')+'</td><td>'+e(d.record_count??'not stated')+'</td><td>'+d.files.map(f=>'<a href="../'+e(f.path)+'">'+e(f.path.split('/').pop())+'</a>').join('<br>')+'</td></tr>').join('');
document.getElementById('domains').innerHTML=Object.entries(R.source_domain_counts).sort((a,b)=>a[0].localeCompare(b[0])).map(x=>'<article class="card"><div class="num">'+e(x[1])+'</div>'+e(x[0])+'</article>').join('');
document.getElementById('gaps').innerHTML=R.gaps.map(g=>'<article class="card"><b>'+e(g.title)+'</b><p>'+e(g.detail)+'</p></article>').join('');
</script></body></html>"""
 (ROOT/"site/coverage.html").write_text(page.replace("@@REPORT@@",data),encoding="utf-8")
def update_navigation(sourcecount,claimcount,notecount):
 p=ROOT/"README.md";t=p.read_text(encoding="utf-8")
 t=t.replace("## Current work: v0.8 toward v1.0","## Current edition: v1.0")
 t=t.replace("**Edition:** v0.8 · **Source cards:** 145 · **Scoped claims:** 76 · **World profiles:** 18 · **Lessons:** 26 · **Scientific reference records:** 26 · **Original SVG diagrams:** 28 · **Research pass:** 2026-11-02",f"**Edition:** v1.0 · **Source cards:** {sourcecount} · **Scoped claims:** {claimcount} · **Research notes:** {notecount} · **World profiles:** 18 · **Lessons:** 30 · **Scientific reference records:** 26 · **Dataset registrations:** 10 · **Research pass:** {DATE}")
 t=t.replace("The current release links NOAA solar radio flux and geomagnetic observations with one-minute solar-wind plasma and magnetic-field measurements.","This first complete edition unifies public sources, scoped claims, lessons, research documents, and registered datasets. It adds a frozen GOES X-ray snapshot, exact channel pairing, public military SIGINT history, offline search, and a collection coverage view.")
 t=t.replace("[solar-wind explorer](site/solar_wind.html)","[unified search](site/unified_search.html), the [collection coverage view](site/coverage.html), and [solar-wind explorer](site/solar_wind.html)")
 t=t.replace("**What v0.8 adds:** a frozen one-minute plasma and magnetic-field snapshot, source-aware active-record selection, an exact timestamp/source paired data set, partial-day summaries, a new Solar-wind Explorer, a teaching graphic, a science guide, Lesson 28, and an AI-readable packet.","**What v1.0 adds:** a dated GOES soft X-ray snapshot and exact channel pairs; five public history routes; offline search, data coverage, provenance, two lessons, a navigational graphic, and an AI-readable packet.")
 t=t.replace("[**Start here**](START-HERE.md) · [**Browse source records**](site/index.html)","[**Start here**](START-HERE.md) · [**Unified search**](site/unified_search.html) · [**Dataset coverage**](site/coverage.html) · [**Browse source records**](site/index.html)")
 t=t.replace("| [Offline source explorer](site/index.html) | Curated sources, claims, research notes, lessons, world profiles, and topic navigation |","| [Offline source explorer](site/index.html) | Curated sources, claims, research notes, lessons, world profiles, and topic navigation |\n| [Unified offline search](site/unified_search.html) | Filter source cards, claims, datasets, publications, lessons, and research documents |\n| [Dataset coverage](site/coverage.html) | Inspect registered kinds, date windows, files, and collection gaps |")
 t=t.replace("[26-lesson course](courses/README.md)","[30-lesson course](courses/README.md)").replace("The library contains 142 source records",f"The library contains {sourcecount} source records")
 t=t.replace("independent review of source and rights coverage; a blind held-out retrieval comparison; and, if useful, a controlled human/model answer-quality study","optional future studies such as blind retrieval comparison or controlled human/model answer-quality study")
 if "### Edition 1.0 collection routes" not in t:t += "\n\n### Edition 1.0 collection routes\n\n- [Unified search](site/unified_search.html) · [dataset coverage](site/coverage.html) · [public history](docs/research/PUBLIC_HISTORICAL_RECORDS_v10.md) · [GOES X-ray guide](docs/science/09_goes_xray_flux_observations.md) · [collection guide](docs/research/DATA_COLLECTION_GUIDE_v10.md).\n- [Lesson 29](courses/29-public-sigint-history.md) teaches evidence roles; [Lesson 30](courses/30-compile-observations-and-provenance.md) traces raw, derived, and synthetic data.\n- [AI research packet](data/packets/examples/atlas-cross-domain-research.v1.0.packet.json) and [release audit](docs/research/RELEASE_AUDIT_v10.md).\n"
 # Canonicalize README navigation and counts so repeated builds remain idempotent.
 lines=t.splitlines()
 idx=lines.index("## Current edition: v1.0")
 intro="This first complete edition unifies public sources, scoped claims, lessons, research documents, and registered datasets. It adds a frozen GOES X-ray snapshot, exact channel pairing, public military SIGINT history, offline search, and a collection coverage view. Start with the [unified search](site/unified_search.html), [dataset coverage](site/coverage.html), [solar-wind explorer](site/solar_wind.html), [dataset registry](data/dataset_registry.json), [collection guide](docs/research/DATA_COLLECTION_GUIDE_v10.md), or [roadmap to v1.0](docs/research/ROADMAP_TO_1.0.md). The evergreen logo above remains version independent."
 lines[idx+2]=intro
 svg_count=len(list((ROOT/"assets").glob("*.svg")))
 stats=f"**Edition:** v1.0 · **Source cards:** {sourcecount} · **Scoped claims:** {claimcount} · **Research notes:** {notecount} · **World profiles:** 18 · **Lessons:** 30 · **Scientific reference records:** 26 · **Dataset registrations:** 10 · **Original SVG diagrams:** {svg_count} · **Research pass:** {DATE}"
 for i,line in enumerate(lines):
  if line.startswith("**Edition:**"):lines[i]=stats
  if line.startswith("[**Start here**]"):
   lines[i]="[**Start here**](START-HERE.md) · [**Unified search**](site/unified_search.html) · [**Dataset coverage**](site/coverage.html) · [**Browse source records**](site/index.html) · [**Topic map**](site/topic-map.html) · [**Roadmap to release**](assets/signal_atlas_roadmap_to_release.png) · [**v1.0 release audit**](docs/research/RELEASE_AUDIT_v10.md) · [**Resume handoff**](THREAD-RESUME-HANDOFF.md)"
  if line.startswith("The library contains "):lines[i]=f"The library contains {sourcecount} source records, not a mirror of the Internet. Search and coverage describe the frozen package, not the world-wide completeness of sources or measurements."
  if line.startswith("- **Next evidence gate:**"):lines[i]="- **Optional evaluation:** retrieval or human/model answer-quality studies can be added if they help users. This release measures index integrity and search behavior, not scientific conclusions or model improvement."
  if line.startswith("- **v0.8:**") and not any(x.startswith("- **v1.0:**") for x in lines):lines.insert(i+1,"- **v1.0:** adds a GOES X-ray capture, expanded public history routes, unified offline search, dataset coverage, provenance, two lessons, a query packet, and validation while retaining the evergreen logo and earlier release contents.")
  if line.startswith("| [26-lesson course]"):lines[i]=line.replace("[26-lesson course]","[30-lesson course]")
  if line.startswith("| [Unified offline search]"):lines[i]=""
  if line.startswith("| [Dataset coverage]"):lines[i]=""
  if line.startswith("| [Unified offline search]") or line.startswith("| [Dataset coverage]"):lines[i]=""
  if line.startswith("| [GOES"):lines[i]=""
  if line.startswith("| [Public history"):lines[i]=""
  if line.startswith("| [30-lesson course]"):lines[i]=""
  if line.startswith("| [Scientific reference index]"):lines[i]=""
  if line.startswith("| [Science guide]"):lines[i]=""
  if line.startswith("| [Technology guide]"):lines[i]=""
  if line.startswith("| [Research desk]"):lines[i]=""
  if line.startswith("| [Research packet schema]"):lines[i]=""
  if line.startswith("| [Agent instructions]"):lines[i]=""
  if line.startswith("| [Offline source explorer]"):lines[i]=""
 # Rebuild the table as a single source of truth.
 start=lines.index("## Explore the library")
 end=next(i for i in range(start+1,len(lines)) if lines[i].startswith("## "))
 table=["## Explore the library","","| Destination | What it contains |","| --- | --- |","| [Offline source explorer](site/index.html) | Curated source cards, claims, lessons, profiles, and topic navigation |","| [Unified offline search](site/unified_search.html) | Search source cards, claims, datasets, publications, lessons, notes, and research documents |","| [Dataset coverage](site/coverage.html) | Inspect data kinds, capture windows, files, and known collection gaps |","| [30-lesson course](courses/README.md) | Signal foundations, public history, measurement, and research practice |","| [Science guide](docs/science/README.md) | Wave physics, sampling, remote sensing, and measurement science |","| [Public history guide](docs/research/PUBLIC_HISTORICAL_RECORDS_v10.md) | NSA, GCHQ, and ASD routes with source roles and limits |","| [Scientific reference index](documents/INDEX.md) | Publication and technical-reference records; four original Atlas PDFs |","| [Technology guide](docs/technology/README.md) | SDR, receivers, metadata standards, reproducibility, and lawful workflows |","| [Research desk](docs/research/README.md) | Evidence workflow, open questions, and collection notes |","| [Research packet schema](docs/research/PACKET_SCHEMA_v06.md) | Provenance, deterministic packet fields, and evidence limits |","| [Agent instructions](AGENTS.md) | Read-only workflow, attribution rules, evidence statuses, and safety boundaries |",""]
 lines=lines[:start]+table+lines[end:]
 t="\n".join(lines)+"\n"
 p.write_text(t,encoding="utf-8")
 p=ROOT/"site/index.html";h=p.read_text(encoding="utf-8")
 s=h.index("const SOURCES=")+len("const SOURCES=");e=h.index("];",s)+1
 h=h[:s]+json.dumps(loadl("data/sources.jsonl"),ensure_ascii=False,separators=(",",":"))+h[e:]
 h=re.sub(r"const CLAIM_COUNT=\d+;",f"const CLAIM_COUNT={claimcount};",h,count=1)
 lessons=[]
 for f in sorted((ROOT/"courses").glob("[0-9]*.md")):
  m=re.match(r"^(\d+)[-_]",f.stem)
  if not m:continue
  n=m.group(1)
  body=f.read_text(encoding="utf-8");title=next((x.lstrip("# ").strip() for x in body.splitlines() if x.startswith("# ")),f.stem)
  objective=next((x[3:].strip() for x in body.splitlines() if x.startswith("## Outcome")),"See lesson learning outcome.")
  lessons.append({"n":n.zfill(2),"title":title,"objective":objective,"file":f.name})
 s=h.index("const LESSONS=")+len("const LESSONS=");e=h.index("];",s)+1
 h=h[:s]+json.dumps(lessons,ensure_ascii=False,separators=(",",":"))+h[e:]
 s=h.index("const NOTES=")+len("const NOTES=");e=h.index("];",s)+1
 h=h[:s]+json.dumps(loadl("data/research_notes.jsonl"),ensure_ascii=False,separators=(",",":"))+h[e:]
 navlink='<a class="navlink" href="unified_search.html">09 / UNIFIED SEARCH</a><a class="navlink" href="coverage.html">10 / DATA COVERAGE</a>'
 h=re.sub(r'(?:'+re.escape(navlink)+r')+',navlink,h)
 if navlink not in h:h=h.replace("</aside>",navlink+"</aside>",1)
 navstyle=".navlink{display:block;width:100%;color:#b0c0cb;padding:10px 13px 10px 16px;text-decoration:none;font:700 11px ui-monospace,monospace;letter-spacing:.55px}.navlink:hover{color:var(--teal)}"
 while navstyle+navstyle in h:h=h.replace(navstyle+navstyle,navstyle)
 if navstyle not in h:h=h.replace(".navbtn{display:block",navstyle+".navbtn{display:block",1)
 p.write_text(h,encoding="utf-8")
 p=ROOT/"courses/README.md";t=p.read_text(encoding="utf-8").replace("26-lesson open course","30-lesson open course")
 t=t.replace("| 27 | [Join space-weather observations](27_space_weather_data_join.md) | Build and interpret a date-keyed F10.7 and estimated planetary Kp comparison. |","| 27 | [Join space-weather observations](27_space_weather_data_join.md) | Build and interpret a date-keyed F10.7 and estimated planetary Kp comparison. |\n| 29 | [Navigate public SIGINT history](29-public-sigint-history.md) | Distinguish catalogs, recollections, institutional histories, and interpretations. |\n| 30 | [Compile observations with provenance](30-compile-observations-and-provenance.md) | Trace raw, derived, and synthetic datasets through provenance and search. |")
 if "## v1.0" not in t:t += "\n\n## v1.0\n\n- [Lesson 29](29-public-sigint-history.md) → [public history guide](../docs/research/PUBLIC_HISTORICAL_RECORDS_v10.md).\n- [Lesson 30](30-compile-observations-and-provenance.md) → [coverage](../site/coverage.html) → [registry](../data/dataset_registry.json) → [offline search](../site/unified_search.html).\n"
 lines=t.splitlines()
 lines=[line for line in lines if not (line.startswith("| 28 |") or line.startswith("| 29 |") or line.startswith("| 30 |"))]
 row27=next((i for i,line in enumerate(lines) if line.startswith("| 27 |")),None)
 newrows=["| 28 | [Align solar-wind time series](28_solar_wind_time_alignment.md) | Pair minute-scale plasma and magnetic-field records by timestamp and source. |","| 29 | [Navigate public SIGINT history](29-public-sigint-history.md) | Distinguish catalogs, recollections, institutional histories, and interpretations. |","| 30 | [Compile observations with provenance](30-compile-observations-and-provenance.md) | Trace raw, derived, and synthetic datasets through provenance and search. |"]
 if row27 is not None:lines[row27+1:row27+1]=newrows
 t="\n".join(lines)+"\n"
 p.write_text(t,encoding="utf-8")
 appends={"docs/INDEX.md":"\n\n## Version 1.0\n\n- [Public history](research/PUBLIC_HISTORICAL_RECORDS_v10.md) · [GOES science](science/09_goes_xray_flux_observations.md) · [collection guide](research/DATA_COLLECTION_GUIDE_v10.md)\n- [Unified search](../site/unified_search.html) · [coverage](../site/coverage.html) · [release audit](research/RELEASE_AUDIT_v10.md)\n","docs/research/README.md":"\n\n## Version 1.0\n\n- [Unified search and coverage](UNIFIED_SEARCH_AND_COVERAGE_v10.md)\n- [Collection guide](DATA_COLLECTION_GUIDE_v10.md) · [public history](PUBLIC_HISTORICAL_RECORDS_v10.md)\n- [Summary](RELEASE_SUMMARY_v10.md) · [audit](RELEASE_AUDIT_v10.md) · [handoff](../../THREAD-RESUME-HANDOFF.md)\n","data/README.md":"\n\n## Version 1.0\n\n- Registry distinguishes observed, derived, and synthetic datasets.\n- Unified search index and input manifest are offline derivatives.\n- GOES raw snapshot, metadata, paired table, and provenance share source/dataset IDs.\n- Coverage report describes this package, not global sensor coverage.\n"}
 for rel,addition in appends.items():
  p=ROOT/rel;old=p.read_text(encoding="utf-8");marker="## Version 1.0" if rel=="docs/INDEX.md" else ("## Version 1.0" if rel=="docs/research/README.md" else "## Version 1.0");p.write_text(old if marker in old else old+addition,encoding="utf-8")
 p=ROOT/"docs/research/ROADMAP_TO_1.0.md";t=p.read_text(encoding="utf-8")
 if "## v1.0 delivered" not in t:
  lines=t.splitlines();first=next(i for i,line in enumerate(lines) if line.startswith("# "))
  lines[first+1:first+1]=["","## v1.0 delivered — 2026-11-03","","This first complete edition compiles public records, dated observations, provenance-bound derivations, offline search, a coverage view, public SIGINT history, and teaching routes. See the [release summary](RELEASE_SUMMARY_v10.md) and [audit](RELEASE_AUDIT_v10.md). Future releases should extend dated collections and source coverage based on actual use.",""]
  t="\n".join(lines)+"\n"
 p.write_text(t,encoding="utf-8")
 (ROOT/"CHANGELOG.md").write_text("# Changelog\n\n## v1.0 — 2026-11-03\n\n- Added a frozen NOAA GOES X-ray snapshot and exact timestamp/satellite channel pairing.\n- Added five attributed NSA, GCHQ, and ASD history routes and claims.\n- Added offline unified search, collection coverage, input hashes, provenance, and an AI-readable packet.\n- Added two teaching lessons, collection guidance, release lineage, and focused validation.\n- Preserved the evergreen logo and v0.5-v0.8 contents.\n",encoding="utf-8")
 p=ROOT/"START-HERE.md";old=p.read_text(encoding="utf-8");p.write_text(old if "## Version 1.0" in old else old+"\n\n## Version 1.0\n\n1. Use [Unified Search](site/unified_search.html) to find sources, claims, datasets, lessons, or research documents.\n2. Check [dataset coverage](site/coverage.html) for time windows and gaps.\n3. Follow [Lesson 30](courses/30-compile-observations-and-provenance.md) from raw input to derived series.\n4. Follow [Lesson 29](courses/29-public-sigint-history.md) for public military SIGINT research routes.\n",encoding="utf-8")
 p=ROOT/"AGENTS.md";old=p.read_text(encoding="utf-8");p.write_text(old if "## v1.0 local commands" in old else old+"\n\n## v1.0 local commands\n\n- Search frozen local records: python tools/atlas_search_v10.py \\\"solar wind\\\" --kind dataset.\n- Rebuild deterministic derivatives: python tools/build_v10.py. No live fetch is used.\n- Validate with tools/validate_v10.py and unittest discover -s tests -p test_v10_atlas.py.\n- New rolling data is obtained only through the explicit dated fetch tool, which will not overwrite this snapshot.\n",encoding="utf-8")
 (ROOT/"THREAD-RESUME-HANDOFF.md").write_text("""# Signal Atlas thread-resume handoff

## Current release: v1.0

- Goal: compile useful public science, signal, technology, and historical data into a coherent, navigable system for humans and AI, with origin, dates, joins, evidence roles, and limits attached.
- Release: first complete v1.0 edition. Preserve the evergreen version-neutral logo at assets/signal_atlas_logo_header.png.
- User direction: collect more data; make the system coherent and useful; the public GitHub repository is exactly SIGNAL-ATLAS, with no version number.
- GitHub: public repository creation is authorized but pending because connected GitHub tools do not expose repository creation. Do not create another name or publish elsewhere.
- Library: preserve v0.5, v0.6, v0.7, v0.8, and v1.0 archives with their summary, audit, and handoff in the persistent SIGNAL ATLAS Space.
- Start with README.md, site/unified_search.html, site/coverage.html, docs/research/RELEASE_SUMMARY_v10.md, and docs/research/RELEASE_AUDIT_v10.md.
- New batch: NSA, GCHQ and ASD public-history routes; one frozen NOAA primary GOES X-ray snapshot and exact paired channels.
- Future work: extend dated collections and source coverage; create and push to SIGNAL-ATLAS when repository-creation access is available.

## Reproduction

From the package root run tools/build_v10.py, tools/atlas_search_v10.py "GOES x-ray flux" --kind dataset, tools/validate.py, tools/validate_science.py, tools/validate_v10.py, and unittest discover -s tests -p test_v10_atlas.py.

Historical v0.5 through v0.8 handoffs remain in their release ZIPs.
""",encoding="utf-8")

def write_release_docs(counts,meta,pairs):
 (ROOT/"docs/research/RELEASE_SUMMARY_v10.md").write_text(f"""# SIGNAL ATLAS v1.0 — Release summary

Release date: 2026-11-03  
Status: first complete, locally validated edition

Signal Atlas compiles public science, signal, technology, and historical material into a reusable library for people and AI. The core goal is to collect useful data, make it coherent, and make the compiled library navigable again.

## Included

- Complete inherited v0.8 tree; evergreen, version-neutral README logo preserved.
- {counts["sources"]} source cards, {counts["claims"]} scoped claims, {counts["notes"]} research notes, {counts["publications"]} publication records, {counts["lessons"]} lessons, and {counts["datasets"]} registered datasets.
- Five public-history routes across NSA, GCHQ, and ASD, with attributed source cards and scoped claims.
- Frozen NOAA GOES primary X-ray response: {meta["record_count"]} raw rows, capture metadata and raw SHA-256; {pairs} exact timestamp/satellite pairs across two energy bands.
- Offline unified search across sources, claims, notes, publications, datasets, lessons, and selected research documents.
- Dataset coverage view, CLI, deterministic input manifest, provenance, teaching graphic, two lessons, and AI-readable query packet.

## Start

Open START-HERE.md, then site/unified_search.html and site/coverage.html.

~~~powershell
python tools/atlas_search_v10.py "solar wind" --kind dataset
python tools/atlas_search_v10.py "Pearl Harbor" --kind source --json
~~~

## Limits

The GOES file is one rolling six-hour capture, not a continuous archive. Physical quantities and time supports differ. No interpolation, event causality, nowcast, or forecast is claimed. Search is lexical over bundled metadata and selected Markdown; it does not crawl remote pages, index PDF full text, or answer with an LLM.

The requested public GitHub name is SIGNAL-ATLAS. Public creation is authorized but pending because current connected GitHub tools cannot create a repository. Artifacts should remain in the persistent SIGNAL ATLAS Library with earlier versions.
""",encoding="utf-8")
 lin=loadj("data/release_v10_lineage.json") if (ROOT/"data/release_v10_lineage.json").exists() else {}
 (ROOT/"docs/research/RELEASE_AUDIT_v10.md").write_text(f"""# SIGNAL ATLAS v1.0 — Release audit

## Integrity and lineage

- Parent release: v0.8; retained manifest SHA-256: {lin.get("parent_manifest_sha256","recorded after build")}.
- Parent paths: {lin.get("parent_entry_count","pending")}; required unchanged or explicitly modified.
- Modified parent paths and new files are enumerated in data/release_v10_lineage.json.
- Evergreen logo is verified against the parent manifest.
- Release packaging checks ZIP CRC, complete manifest membership, and SHA-256 for every file.

## Data checks

- Catalog: {counts["sources"]} sources, {counts["claims"]} claims, {counts["notes"]} research notes, and {counts["datasets"]} registered datasets.
- GOES capture: {meta["record_count"]} raw rows, {meta["time_tag_start"]} to {meta["time_tag_end"]}; captured {meta["captured_before_utc"]}; raw SHA-256 {meta["raw_sha256"]}.
- Derived channel table: {pairs} exact timestamp/satellite pairs; validator recomputes matches and duplicate/unmatched handling.
- Search input hashes and packet digest are recomputed by validation.

## Release checks

The release runs tools/validate.py, tools/validate_science.py, tools/validate_v10.py, unittest discover -s tests -p test_v10_atlas.py, then tools/release.py --version v1.0 --output <outputs/SIGNAL-ATLAS-v1.0.zip>. The packaging step verifies each ZIP member against the file manifest.

## Limits

This checks internal consistency, reproducible local derivation, v0.8 inheritance, and package integrity. It does not establish complete scientific or archive coverage, independent truth assessment of every source, or end-user utility through a user study. GOES records are a six-hour capture; no cross-instrument physical attribution or forecast validation is claimed. Search is not PDF full-text search or semantic truth scoring.
""",encoding="utf-8")

def build_lineage():
 p=ROOT/"data/release_v10_lineage.json"
 if p.exists():
  old=loadj("data/release_v10_lineage.json");base=old["parent_entries"];basehash=old["parent_manifest_sha256"]
 else:
  text=(ROOT/"MANIFEST.sha256").read_text(encoding="utf-8");base=[]
  for line in text.splitlines():
   if line.strip():h,r=line.split("  ",1);base.append({"path":r,"sha256":h})
  basehash=digest(text.encode())
 paths={x["path"] for x in base};changed=[];missing=[]
 for x in base:
  f=ROOT/x["path"]
  if not f.exists():missing.append(x["path"])
  elif digest(f.read_bytes())!=x["sha256"]:changed.append(x["path"])
 if missing:raise ValueError("Missing v0.8 parent files "+str(missing[:5]))
 current={f.relative_to(ROOT).as_posix() for f in ROOT.rglob("*") if f.is_file() and f.name not in {"MANIFEST.sha256","release_v10_lineage.json"} and "__pycache__" not in f.parts}
 added=sorted((current-paths)|{"data/release_v10_lineage.json"})
 release_entries=[{"path":r,"sha256":digest((ROOT/r).read_bytes())} for r in sorted(current)]
 savej(p,{"parent_release":"v0.8","parent_manifest_sha256":basehash,"parent_entry_count":len(base),"parent_entries":base,"allowed_changed_paths":sorted(changed),"added_paths":added,"release_entry_count":len(release_entries),"release_entries":release_entries,"policy":"Every v0.8 path remains. Changed parent paths are explicit; other parent content is byte-identical. All additions are inventoried and release hashes are recorded."})
 print("LINEAGE",len(base),"parent files;",len(changed),"changed;",len(added),"added")
if __name__=="__main__":build()

