import numpy as np

def _energy(d, lo, hi):
 s=d['spectrum']; f=np.asarray(s['frequencies_hz']); m=np.asarray(s['magnitude']); q=(f>=lo)&(f<hi)
 return float(np.mean(m[q]**2)) if q.any() else 0.0

def analyze_roles(results):
 items=[d for d in results.values() if d and 'error' not in d]; out=[]
 for d in items:
  role=d.get('role','Other')
  if role in ('Bass','Kick','Lead Vocal','Backing Vocal'):
   ranges={'Bass':(40,180),'Kick':(40,150),'Lead Vocal':(800,5000),'Backing Vocal':(800,5000)}; lo,hi=ranges[role]
   out.append({'filename':d['file']['filename'],'role':role,'focus_range_hz':[lo,hi],'focus_energy':round(_energy(d,lo,hi),4),'note':'Role-focused measurement; confirm musical relevance by listening.'})
 for a in items:
  for b in items:
   if a is b: continue
   ra,rb=a.get('role','Other'),b.get('role','Other')
   if {ra,rb}=={'Kick','Bass'}:
    ea=_energy(a,40,150); eb=_energy(b,40,150); out.append({'type':'kick_bass_relationship','kick':a['file']['filename'] if ra=='Kick' else b['file']['filename'],'bass':a['file']['filename'] if ra=='Bass' else b['file']['filename'],'low_end_energy_ratio':round(max(ea,eb)/(min(ea,eb)+1e-12),3),'what_to_check':'Kick/bass phase, fundamental ownership, sustain overlap and sidechain behavior.'})
 return out
