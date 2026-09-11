import numpy as np

def _band(d,lo,hi):
 s=d['spectrum']; f=np.asarray(s['frequencies_hz']); m=np.asarray(s['magnitude']); q=(f>=lo)&(f<hi)
 return float(np.mean(m[q]**2)) if q.any() else 0.0

def analyze_vocals(results):
 vocals=[d for d in results.values() if d and d.get('role') in ('Lead Vocal','Backing Vocal') and 'error' not in d]
 others=[d for d in results.values() if d and d.get('role') not in ('Lead Vocal','Backing Vocal') and 'error' not in d]
 out=[]
 for v in vocals:
  presence=_band(v,1000,5000); sibilance=_band(v,5000,10000); bed=sum(_band(x,1000,5000) for x in others)
  out.append({'filename':v['file']['filename'],'role':v.get('role'),'presence_energy':round(presence,4),'sibilance_energy':round(sibilance,4),'instrumental_presence_energy':round(bed,4),'note':'This is a spectral screening result, not a definitive intelligibility or de-essing diagnosis.'})
  if bed>0 and presence/bed<0.35: out[-1]['possible_issue']='Vocal presence may be masked by the instrumental bed.'
  if presence>0 and sibilance/presence>0.8: out[-1]['possible_issue']='High-frequency vocal energy may warrant a sibilance check.'
 return out
