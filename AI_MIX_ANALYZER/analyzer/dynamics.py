"""Deterministic RMS and crest-factor measurements; no interpretation."""
import numpy as np

def _stats(v):
 v=np.asarray(v,dtype=float); v=v[np.isfinite(v)]
 if not len(v): return {'minimum_dbfs':None,'maximum_dbfs':None,'mean_dbfs':None,'median_dbfs':None,'std_db':None,'p10_dbfs':None,'p90_dbfs':None}
 return {'minimum_dbfs':float(v.min()),'maximum_dbfs':float(v.max()),'mean_dbfs':float(v.mean()),'median_dbfs':float(np.median(v)),'std_db':float(v.std()),'p10_dbfs':float(np.percentile(v,10)),'p90_dbfs':float(np.percentile(v,90))}
def _db(v): return None if v<=1e-15 else float(20*np.log10(v))
def analyze(x,sr,window_seconds=.3,hop_seconds=.1):
 a=np.asarray(x,dtype=float); a=a[:,None] if a.ndim==1 else a; n=max(1,round(window_seconds*sr)); h=max(1,round(hop_seconds*sr)); hist=[]; channel=[]
 for c in range(a.shape[1]):
  rms=np.sqrt(np.mean(a[:,c]**2)) if len(a) else 0; peak=np.max(np.abs(a[:,c])) if len(a) else 0; channel.append({'channel':c+1,'rms_dbfs':_db(rms),'peak_dbfs':_db(peak),'crest_factor_db':None if rms<=1e-15 else _db(peak/rms)})
 for i in range(0,max(1,len(a)-n+1),h):
  b=a[i:i+n]; rms=np.sqrt(np.mean(b*b,axis=0)); peak=np.max(np.abs(b),axis=0); r=float(np.sqrt(np.mean(b*b))); p=float(np.max(np.abs(b)))
  hist.append({'time_s':round(i/sr,6),'rms_dbfs':_db(r),'peak_dbfs':_db(p),'crest_factor_db':None if r<=1e-15 else _db(p/r),'channels':[{'channel':j+1,'rms_dbfs':_db(rms[j]),'peak_dbfs':_db(peak[j]),'crest_factor_db':None if rms[j]<=1e-15 else _db(peak[j]/rms[j])} for j in range(a.shape[1])]})
 rmsvals=[z['rms_dbfs'] for z in hist if z['rms_dbfs'] is not None]; crest=[z['crest_factor_db'] for z in hist if z['crest_factor_db'] is not None]
 overall=np.sqrt(np.mean(a*a)); peak=float(np.max(np.abs(a))) if a.size else 0
 return {'rms':{'overall_dbfs':_db(overall),'window_seconds':window_seconds,'hop_seconds':hop_seconds,'history':hist,**_stats(rmsvals)},'crest_factor':{'overall_db':None if overall<=1e-15 else _db(peak/overall),**_stats(crest)},'dynamic_variation':{'rms_dynamic_spread_db':None if not rmsvals else float(np.percentile(rmsvals,95)-np.percentile(rmsvals,10)),'percentiles':{f'p{p}':float(np.percentile(rmsvals,p)) for p in (10,25,50,75,90)} if rmsvals else {}},'channels':channel,'methodology':{'rms_definition':'sqrt(mean(sample^2)) without normalization','window_seconds':window_seconds,'hop_seconds':hop_seconds,'crest_factor_definition':'peak level minus RMS level using the same scope','peak_definition':'absolute sample peak'}}
