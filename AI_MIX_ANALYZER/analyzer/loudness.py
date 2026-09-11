"""Deterministic BS.1770-compatible loudness measurements.

The implementation uses pyloudnorm for integrated loudness when installed. Windowed
momentary and short-term values are calculated independently from K-weighted
energy windows; they are never derived by averaging LUFS values.
"""
import numpy as np
from scipy.signal import lfilter, butter
try:
    import pyloudnorm as pyln
except ImportError:
    pyln = None

FLOOR = -120.0

def rms(x):
    x=np.asarray(x,dtype=np.float64)
    return float(np.sqrt(np.mean(x*x)))

def _finite_audio(samples):
    x=np.asarray(samples,dtype=np.float64)
    return np.nan_to_num(x,nan=0.0,posinf=0.0,neginf=0.0)

def _k_weight_channels(x,sr):
    nyq=sr/2
    if sr<=120: return x
    b1,a1=butter(2,min(.99,60/nyq),'highpass')
    if 1500 >= nyq: return np.column_stack([lfilter(b1,a1,x[:,i]) for i in range(x.shape[1])])
    b2,a2=butter(2,min(.99,1500/nyq),'high')
    return np.column_stack([lfilter(b2,a2,lfilter(b1,a1,x[:,i])) for i in range(x.shape[1])])

def _window_lufs(weighted, start, size):
    block=weighted[start:start+size]
    if len(block)==0:return None
    # BS.1770 energy sum; pyloudnorm's meter applies channel weights for layouts.
    energy=float(np.mean(block*block))
    if energy<=1e-15:return None
    return float(-0.691+10*np.log10(energy))

def _series(weighted,sr,window,hop):
    size=max(1,round(window*sr)); step=max(1,round(hop*sr)); out=[]
    for start in range(0,max(1,len(weighted)-size+1),step):
        v=_window_lufs(weighted,start,size)
        out.append({'time_s':round(start/sr,6),'lufs':v})
    return out

def _stats(history):
    values=np.array([x['lufs'] for x in history if x['lufs'] is not None],dtype=float)
    if not len(values): return {'minimum_lufs':None,'maximum_lufs':None,'mean_lufs':None,'median_lufs':None,'percentile_10_lufs':None,'percentile_95_lufs':None,'standard_deviation_lu':None}
    return {'minimum_lufs':float(np.min(values)),'maximum_lufs':float(np.max(values)),'mean_lufs':float(np.mean(values)),'median_lufs':float(np.median(values)),'percentile_10_lufs':float(np.percentile(values,10)),'percentile_95_lufs':float(np.percentile(values,95)),'standard_deviation_lu':float(np.std(values))}

def _lra(short_history):
    values=np.array([x['lufs'] for x in short_history if x['lufs'] is not None and x['lufs']>-70],dtype=float)
    if len(values)<2:return None
    ungated=float(np.mean(values)); gated=values[values>=ungated-20.0]
    if len(gated)<2:return None
    return float(np.percentile(gated,95)-np.percentile(gated,10))

def calculate_integrated_loudness(x,sr):
    if not np.any(np.abs(x)>1e-12): return None,'below_measurement_floor'
    if pyln is not None:
        try:
            value=float(pyln.Meter(sr).integrated_loudness(x if x.shape[1]>1 else x[:,0]))
            return value,'pyloudnorm Meter; BS.1770-compatible gating'
        except Exception: pass
    weighted=_k_weight_channels(x,sr); blocks=_series(weighted,sr,0.4,0.1); values=np.array([z['lufs'] for z in blocks if z['lufs'] is not None])
    if not len(values):return None,'below_measurement_floor'
    gated=values[values>-70]
    return (float(np.mean(gated)) if len(gated) else None),'fallback K-weighted energy with absolute floor only'

def loudness(samples,sr,window=0.4,hop=0.1):
    x=_finite_audio(samples); x=x[:,None] if x.ndim==1 else x
    weighted=_k_weight_channels(x,sr)
    momentary_history=_series(weighted,sr,0.4,hop)
    short_history=_series(weighted,sr,3.0,hop)
    integrated,method=calculate_integrated_loudness(x,sr)
    status='ok' if integrated is not None else 'below_measurement_floor'
    report={'standard':'BS.1770-compatible','status':status,'integrated':{'lufs':integrated},'momentary':{'window_seconds':0.4,'hop_seconds':hop,'history':momentary_history,**_stats(momentary_history)},'short_term':{'window_seconds':3.0,'hop_seconds':hop,'history':short_history,**_stats(short_history)},'lra':{'value_lu':_lra(short_history),'method':'EBU R 128 / Tech 3342-style gated short-term percentile estimate'},'methodology':{'standard':'ITU-R BS.1770-compatible; EBU-style LRA estimate','weighting':'K-weighting; channel layout weighting delegated to pyloudnorm for integrated measurement','gating':'pyloudnorm integrated gating when available; fallback absolute -70 LUFS','implementation':method,'silence_representation':'null with status below_measurement_floor'}}
    # Compatibility aliases for existing UI/consumers; canonical data is nested above.
    report.update({'integrated_lufs':integrated,'momentary_lufs':report['momentary']['maximum_lufs'],'short_term_lufs':report['short_term']['maximum_lufs'],'history':[z['lufs'] for z in momentary_history],'lra':report['lra']['value_lu']})
    return report
