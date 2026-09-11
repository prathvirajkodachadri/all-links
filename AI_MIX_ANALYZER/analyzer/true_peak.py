"""Finite-oversampling inter-sample peak measurement.

This is a documented true-peak estimate, not a claim of formal compliance. The
waveform is reconstructed with scipy's polyphase resampling filter in float64,
then searched at the requested 4x/8x/16x rate. Original samples are measured
separately. Peak time is referenced to the original sample clock.
"""
import numpy as np
from scipy.signal import resample_poly
DEFAULT_TRUE_PEAK_OVERSAMPLING=8
SUPPORTED_OVERSAMPLING=(4,8,16)

def _db(value):
    return None if value is None or abs(value)<=1e-15 else float(20*np.log10(abs(value)))

def _channel_peak(ch,sr,factor,index):
    ch=np.asarray(ch,dtype=np.float64); n=len(ch)
    if not n or not np.any(np.isfinite(ch)) or np.max(np.abs(np.nan_to_num(ch,nan=0.0,posinf=0.0,neginf=0.0)))<=1e-15:
        return {'channel':index,'status':'silence','sample_peak_dbfs':None,'true_peak_dbtp':None}
    ch=np.nan_to_num(ch,nan=0.0,posinf=0.0,neginf=0.0)
    si=int(np.argmax(np.abs(ch))); sv=float(ch[si])
    # scipy polyphase reconstruction; default zero-phase FIR edge handling.
    y=resample_poly(ch,factor,1).astype(np.float64,copy=False)
    ti=int(np.argmax(np.abs(y))); tv=float(y[ti]); positive=float(np.max(y)); negative=float(np.min(y))
    return {'channel':index,'status':'ok','sample_peak_dbfs':_db(sv),'sample_peak_value':sv,'sample_peak_index':si,'sample_peak_time_s':si/sr,'true_peak_dbtp':_db(tv),'true_peak_value':tv,'positive_true_peak_dbtp':_db(positive),'negative_true_peak_dbtp':_db(negative),'true_peak_oversampled_index':ti,'true_peak_time_s':ti/(sr*factor),'true_peak_excess_db':None if _db(tv) is None or _db(sv) is None else _db(tv)-_db(sv)}

def true_peak(x, factor=DEFAULT_TRUE_PEAK_OVERSAMPLING, sample_rate=None):
    if factor not in SUPPORTED_OVERSAMPLING: raise ValueError(f'factor must be one of {SUPPORTED_OVERSAMPLING}')
    a=np.asarray(x,dtype=np.float64); channels=a[:,None] if a.ndim==1 else a
    if channels.ndim!=2: raise ValueError('audio must be a 1D or 2D array')
    sr=float(sample_rate or 1.0); results=[_channel_peak(channels[:,i],sr,factor,i+1) for i in range(channels.shape[1])]
    valid=[p for p in results if p.get('true_peak_value') is not None]
    if not valid:
        return {'status':'silence','sample_peak_dbfs':None,'true_peak_dbtp':None,'oversampling_factor':factor,'channels':results,'per_channel':results,'method':'scipy.signal.resample_poly float64 finite-oversampling estimate','methodology':{'reconstruction_method':'polyphase FIR resampling','edge_handling':'scipy default zero-phase filter behavior; edge peaks are reported and should be interpreted with source boundaries','peak_time_reference':'original sample clock'},'dbtp':None,'sample_index':None,'value':None}
    best=max(valid,key=lambda p:abs(p['true_peak_value'])); sample_best=max(results,key=lambda p:abs(p.get('sample_peak_value',0.0)))
    return {'status':'ok','sample_peak_dbfs':sample_best['sample_peak_dbfs'],'sample_peak_value':sample_best['sample_peak_value'],'true_peak_dbtp':best['true_peak_dbtp'],'true_peak_value':best['true_peak_value'],'sample_peak_index':sample_best['sample_peak_index'],'true_peak_time_s':best['true_peak_time_s'],'oversampling_factor':factor,'channels':results,'per_channel':results,'method':'scipy.signal.resample_poly float64 finite-oversampling estimate','methodology':{'reconstruction_method':'polyphase FIR resampling','filter':'scipy resample_poly default FIR design','edge_handling':'scipy default zero-phase filter behavior','peak_time_reference':'original sample clock; oversampled index is retained per channel'},'dbtp':best['true_peak_dbtp'],'sample_index':best['true_peak_time_s'],'value':best['true_peak_value']}
