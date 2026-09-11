import numpy as np
from scipy.signal import lfilter
try:
    import pyloudnorm as pyln
except ImportError:
    pyln = None

def _k_weight(x, sr):
    # BS.1770-style high-shelf + high-pass approximation using biquads.
    from scipy.signal import butter
    b1,a1=butter(2,60/(sr/2),'highpass'); b2,a2=butter(2,1500/(sr/2),'high')
    return lfilter(b2,a2,lfilter(b1,a1,x))
def rms(x): return float(np.sqrt(np.mean(np.square(x), dtype=np.float64)))
def db(x, floor=-120): return max(floor, 20*np.log10(max(float(x),10**(floor/20))))
def loudness(samples,sr,window=0.4,hop=0.1):
    x=samples if samples.ndim==2 else samples[:,None]; mono=x.mean(1); kw=_k_weight(mono,sr)
    if pyln is not None:
        meter=pyln.Meter(sr)
        integrated=float(meter.integrated_loudness(x))
        momentary=[]
        step=max(1,int(hop*sr)); size=max(1,int(0.4*sr))
        for i in range(0,max(1,len(x)-size+1),step):
            try: momentary.append(float(meter.integrated_loudness(x[i:i+size])))
            except Exception: pass
        vals=np.asarray(momentary if momentary else [integrated])
        short=np.asarray([float(np.mean(vals[i:i+30])) for i in range(0,max(1,len(vals)-29),10)])
        return {'integrated_lufs':integrated,'momentary_lufs':float(vals.max()),'short_term_lufs':float(short.max()) if len(short) else integrated,'history':vals.tolist(),'lra':float(np.percentile(vals,95)-np.percentile(vals,10)) if len(vals)>1 else 0.0,'method':'pyloudnorm BS.1770-compatible meter'}
    n=max(1,int(window*sr)); h=max(1,int(hop*sr)); vals=[]
    for i in range(0,max(1,len(kw)-n+1),h): vals.append(-0.691+10*np.log10(max(np.mean(kw[i:i+n]**2),1e-15)))
    vals=np.asarray(vals); gated=vals[vals>-70]; integrated=float(np.mean(gated)) if len(gated) else -70.0
    short=np.array([np.mean(vals[i:i+30]) for i in range(0,max(1,len(vals)-29),10)]) if len(vals) else np.array([])
    return {'integrated_lufs':integrated,'momentary_lufs':float(vals.max()) if len(vals) else -70,'short_term_lufs':float(short.max()) if len(short) else -70,'history':vals.tolist(),'lra':float(np.percentile(vals,95)-np.percentile(vals,10)) if len(vals)>1 else 0.0}
