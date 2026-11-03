#!/usr/bin/env python3
"""Offline observed-data pilot using NOAA's retained 30-day F10.7 JSON excerpt.

No external HTTP calls. No generalization to solar cycle length, ionospheric events, or RF intercepts.
"""
import json,math,statistics,hashlib,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DAT=ROOT/'data/datasets/noaa_f107_30day_2026-11-02.json'
rows=json.loads(DAT.read_text(encoding='utf-8'))
assert len(rows)==30
values=[float(r['flux']) for r in rows]
days=[datetime.date.fromisoformat(r['time_tag'][:10]) for r in rows]
assert all((b-a).days==1 for a,b in zip(days,days[1:])), 'Must be a one-day-interval excerpt'
assert all(math.isfinite(x) for x in values)
mean=statistics.mean(values);std=statistics.stdev(values)
lo=min(values);hi=max(values)
max_dates=[str(days[i]) for i,v in enumerate(values) if v==hi]
min_dates=[str(days[i]) for i,v in enumerate(values) if v==lo]
seven=[statistics.mean(values[max(0,i-6):i+1]) for i in range(len(values))]
result={
 'name':'NOAA 10.7 cm solar radio flux, 30-day observed-data pilot',
 'data_origin':'https://services.swpc.noaa.gov/products/10cm-flux-30-day.json',
 'data_status':'actual public reported observations transcribed from source on 2026-11-02',
 'content_sha256':hashlib.sha256(DAT.read_bytes()).hexdigest(),
 'sample_count':len(values),'first_date':str(days[0]),'last_date':str(days[-1]),
 'unit':'solar flux units (sfu)','measurement_frequency_mhz':2800,
 'vacuum_wavelength_m':299792458/(2800e6),
 'mean':round(mean,6),'sample_stddev':round(std,6),'min':lo,'max':hi,
 'max_dates':max_dates,'min_dates':min_dates,
 'last_observation':values[-1],'last_seven_day_trailing_mean':round(seven[-1],6),
 'limitations':['30 days cannot establish a solar cycle or causal effects on communications',
 'the underlying rolling endpoint is mutable; this dataset is a fixed dated excerpt',
 'source time tags have no explicit time-zone offset',
 'these are daily reported flux values, not raw IQ samples or personally intercepted transmissions'],
 'interpretation':'established observational variation only; no scientific novelty inferred'
}
out=ROOT/'data/experiments/noaa_f107_v05.json';out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
# Editable SVG teaching chart with title, description and source data markers.
W,H=1400,720;left,right,top,bottom=130,1315,190,570
def x(i):return left+i*(right-left)/(len(values)-1)
def y(v):return bottom-(v-75)/(145-75)*(bottom-top)
points=' '.join(f'{x(i):.2f},{y(v):.2f}' for i,v in enumerate(values))
rolling=' '.join(f'{x(i):.2f},{y(v):.2f}' for i,v in enumerate(seven))
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">',
'<title>NOAA F10.7 solar radio flux observed values during 2026-10-04 to 2026-11-02</title>',
'<desc>Thirty daily values in solar flux units vary from 89 to 137. A solid turquoise curve marks observations and dashed amber line shows trailing seven-day means. This is a real published sample, not a simulation.</desc>',
'<rect width="1400" height="720" fill="#071827"/>',
'<text x="72" y="86" font-size="48" fill="#f0f9f7" font-family="Arial" font-weight="bold">REAL OBSERVATIONS: SOLAR RADIO FLUX</text>',
'<text x="72" y="128" font-size="23" fill="#a5c7cf" font-family="Arial">NOAA SWPC • 10.7 cm (2800 MHz) • 30 reported daily observations • units: sfu</text>',
'<rect x="114" y="162" width="1224" height="445" rx="8" fill="#0f2b3b" stroke="#3b5768"/>']
for grid in range(80,141,10):
 yy=y(grid)
 svg.append(f'<line x1="{left}" x2="{right}" y1="{yy:.1f}" y2="{yy:.1f}" stroke="#426071" stroke-dasharray="4 6"/><text x="80" y="{yy+8:.1f}" font-size="18" fill="#bbd3d5" font-family="Arial">{grid}</text>')
for i in [0,7,14,21,29]:
 svg.append(f'<text x="{x(i):.1f}" y="619" text-anchor="middle" font-size="19" fill="#bbd3d5" font-family="Arial">{days[i].strftime("%b %d")}</text>')
svg.extend([f'<polyline points="{rolling}" fill="none" stroke="#ecab69" stroke-width="5" stroke-dasharray="12 8" stroke-linejoin="round"/>',
 f'<polyline points="{points}" fill="none" stroke="#62e3db" stroke-width="4" stroke-linejoin="round"/>'])
for i,val in enumerate(values):
 svg.append(f'<circle cx="{x(i):.1f}" cy="{y(val):.1f}" r="3.2" fill="#79f7ef"/>')
svg.extend(['<circle cx="920" cy="670" r="5" fill="#62e3db"/><text x="937" y="678" font-size="19" fill="#d7efec" font-family="Arial">daily observations</text>',
'<line x1="1140" x2="1175" y1="671" y2="671" stroke="#ecab69" stroke-width="4" stroke-dasharray="8 5"/><text x="1185" y="678" font-size="18" fill="#d7efec" font-family="Arial">7-day mean</text>',
'<text x="75" y="678" font-size="18" fill="#9bc8cc" font-family="Arial">Source: services.swpc.noaa.gov/products/10cm-flux-30-day.json (frozen sample)</text></svg>'])
(ROOT/'assets/experiment_noaa_f107.svg').write_text('\n'.join(svg),encoding='utf-8')
print('PASS NOAA observational pilot:',len(values),'mean',round(mean,3),'range',lo,'–',hi,'SHA',result['content_sha256'][:12])
