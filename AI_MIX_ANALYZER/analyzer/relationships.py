"""Objective cross-stem relationships; frequency overlap is not psychoacoustic masking."""
import numpy as np
BANDS=[(20,40),(40,80),(80,120),(120,250),(250,500),(500,1000),(1000,2000),(2000,4000),(4000,8000),(8000,16000),(16000,20000)]
def _linear(d):
 m=np.asarray(d['spectrum']['magnitude'],float); m=10**(m/20); m[~np.isfinite(m)]=0; return np.asarray(d['spectrum']['frequencies_hz']),m
def compare(a,b):
 fa,ma=_linear(a); fb,mb=_linear(b); n=min(len(ma),len(mb)); ma,mb=ma[:n],mb[:n]; f=fa[:n]; q=(f>=20)&(f<=20000); av=ma[q]; bv=mb[q];
 if not len(av): return {'status':'no_common_frequency_bins'}
 sa=av/(np.linalg.norm(av)+1e-15); sb=bv/(np.linalg.norm(bv)+1e-15); bands=[]
 for lo,hi in BANDS:
  z=(f>=lo)&(f<hi); aa=ma[z]; bb=mb[z]; oa=float(np.minimum(aa/(aa.max()+1e-15),bb/(bb.max()+1e-15)).mean()) if z.any() else 0
  bands.append({'low_hz':lo,'high_hz':hi,'a_level_db':float(20*np.log10(max(np.sqrt(np.mean(aa*aa)),1e-15))) if len(aa) else None,'b_level_db':float(20*np.log10(max(np.sqrt(np.mean(bb*bb)),1e-15))) if len(bb) else None,'overlap':oa})
 ar=a.get('dynamics',{}).get('rms',{}).get('overall_dbfs'); br=b.get('dynamics',{}).get('rms',{}).get('overall_dbfs')
 return {'status':'ok','relative_level':{'a_rms_dbfs':ar,'b_rms_dbfs':br,'difference_db':None if ar is None or br is None else ar-br},'spectral_similarity':{'value':float(np.dot(sa,sb)),'method':'L2-normalized cosine similarity of linear FFT magnitudes'},'frequency_overlap':{'overall':float(np.minimum(sa,sb).mean()),'bands':bands},'time_history':[],'methodology':{'alignment':'comparison uses already decoded independent stem measurements; time alignment is not inferred','overlap_definition':'mean minimum of per-spectrum L2-normalized magnitudes','frequency_range_hz':[20,20000]}}
def project_relationships(results):
 items=[d for d in results.values() if d and 'error' not in d]; out=[]
 for i,a in enumerate(items):
  for b in items[i+1:]: out.append({'stem_a':a['file']['filename'],'stem_b':b['file']['filename'],'relationship':compare(a,b)})
 return {'methodology':{'pair_selection':'all available pairs','role_usage':'roles are metadata only'},'pairs':out}
