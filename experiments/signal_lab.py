#!/usr/bin/env python3
"""Synthetic, offline experiments on Nyquist aliasing and amplitude modulation.

No receiver, live spectrum collection, or external datasets are used.
Requirements: numpy, matplotlib (for regenerating illustrations).
"""
from pathlib import Path
import json,hashlib,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
ASSETS=R/'assets';D=R/'data/experiments';D.mkdir(parents=True,exist_ok=True)

def peak(signal,fs):
    y=np.abs(np.fft.rfft(signal))*2/len(signal)
    f=np.fft.rfftfreq(len(signal),1/fs)
    return float(f[int(np.argmax(y[1:])+1)]), f, y

T=2.0; actual=17.0
results={}
fig,axes=plt.subplots(2,1,figsize=(9,6.1),layout='constrained')
for i,fs in enumerate([20,100]):
    n=np.arange(round(T*fs));t=n/fs; x=np.cos(2*np.pi*actual*t)
    p,f,y=peak(x,fs)
    expect=3 if fs==20 else 17
    assert abs(p-expect)<1e-10,(fs,p,expect)
    results[f'fs_{fs}_Hz']={'physical_tone_hz':actual,'sample_rate_hz':fs,'nyquist_hz':fs/2,'measured_peak_hz':p,'expected_peak_hz':expect,'n_samples':len(x),'passed':True}
    a=axes[i];a.stem(f,y,basefmt=' ');a.set_xlim(0,50);a.grid(alpha=.3);a.set_title(f'{actual:g} Hz tone sampled at {fs} Hz: FFT peak {p:g} Hz');a.set_xlabel('observed non-negative frequency (Hz)');a.set_ylabel('FFT amplitude')
fig.suptitle('Aliasing is a sampling ambiguity, not a new physical frequency',fontsize=13)
fig.savefig(ASSETS/'experiment_aliasing.svg',bbox_inches='tight')
fig.savefig(ASSETS/'experiment_aliasing.png',dpi=145,bbox_inches='tight')
plt.close(fig)

fs=256;T=2;n=np.arange(round(fs*T));t=n/fs;fc=20.;fm=3.;depth=.65
x=(1+depth*np.cos(2*np.pi*fm*t))*np.cos(2*np.pi*fc*t)
f=np.fft.rfftfreq(len(x),1/fs);a=np.abs(np.fft.rfft(x))*2/len(x)
peaks={str(int(k)):float(a[int(round(k*T))]) for k in [fc-fm,fc,fc+fm]}
assert all(abs(peaks[str(int(k))]-value)<1e-10 for k,value in [(fc-fm,depth/2),(fc,1),(fc+fm,depth/2)])
results['am_modulation']={'carrier_hz':fc,'message_hz':fm,'modulation_depth':depth,'sideband_hz':[fc-fm,fc+fm],'measured_amplitudes':peaks,'expected_amplitudes':{'17':depth/2,'20':1.0,'23':depth/2},'passed':True}
fig,ax=plt.subplots(figsize=(9,4.3),layout='constrained');ax.stem(f,a,basefmt=' ');ax.set_xlim(10,30);ax.set_ylim(0,1.1);ax.set_xlabel('frequency (Hz)');ax.set_ylabel('amplitude (normalized)');ax.set_title('Synthetic amplitude modulation: symmetric sidebands (17, 20, 23 Hz)');ax.grid(alpha=.3)
for xx,label in [(17,'lower sideband'),(20,'carrier'),(23,'upper sideband')]:ax.annotate(label,xy=(xx,a[int(xx*T)]),xytext=(xx+0.6, .53 if xx!=20 else 1.03),fontsize=9,arrowprops={'arrowstyle':'->'})
fig.savefig(ASSETS/'experiment_am_sidebands.svg',bbox_inches='tight')
fig.savefig(ASSETS/'experiment_am_sidebands.png',dpi=145,bbox_inches='tight')
plt.close(fig)
results['scope']='purely synthetic proof-of-implementation against established Fourier sampling theory; not a new physical discovery or real-world RF validation'
results['reproducibility']={'numpy_version':np.__version__,'matplotlib_version':matplotlib.__version__,'randomness':'none','command':'python experiments/signal_lab.py'}
(D/'signal_lab_v04.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
