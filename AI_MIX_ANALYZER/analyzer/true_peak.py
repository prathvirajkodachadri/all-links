import numpy as np
from scipy.signal import resample_poly

def _peak(channel, factor):
 y=resample_poly(channel,factor,1); i=int(np.argmax(np.abs(y))); value=float(y[i])
 return {'dbtp':float(20*np.log10(max(abs(value),1e-12))),'sample_index':i/factor,'value':value}

def true_peak(x, factor=8):
    channels=x[:,None] if x.ndim==1 else x
    peaks=[_peak(channels[:,i],factor) for i in range(channels.shape[1])]
    best=max(peaks,key=lambda p:abs(p['value']))
    return {'dbtp':best['dbtp'],'sample_index':best['sample_index'],'value':best['value'],'oversampling_factor':factor,'per_channel':peaks}
