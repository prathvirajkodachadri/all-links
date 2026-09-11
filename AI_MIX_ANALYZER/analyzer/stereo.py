"""Deterministic stereo, Mid/Side, correlation and mono measurements."""
import numpy as np
class CorrelationEvidence(dict):
 def _v(self): return self.get('overall')
 def __lt__(self,o): return self._v()<o
 def __le__(self,o): return self._v()<=o
 def __gt__(self,o): return self._v()>o
 def __ge__(self,o): return self._v()>=o
 def __sub__(self,o): return self._v()-o
 def __rsub__(self,o): return o-self._v()
BANDS=[(20,40),(40,80),(80,120),(120,250),(250,500),(500,1000),(1000,2000),(2000,4000),(4000,8000),(8000,16000),(16000,20000)]
def _db(v): return None if v<=1e-15 else float(20*np.log10(v))
def _corr(a,b):
 if len(a)<2 or np.std(a)==0 or np.std(b)==0:return None
 return float(np.corrcoef(a,b)[0,1])
def analyze(x,sr,window_seconds=.3,hop_seconds=.1):
 a=np.asarray(x,dtype=float); a=a[:,None] if a.ndim==1 else a
 if a.shape[1]<2:return {'status':'mono_input','channels':a.shape[1],'methodology':{'note':'Stereo-specific measurements are not fabricated for mono input.'}}
 l,r=a[:,0],a[:,1]; mid=(l+r)/2; side=(l-r)/2; n=max(1,round(window_seconds*sr)); h=max(1,round(hop_seconds*sr)); hist=[]
 for i in range(0,max(1,len(a)-n+1),h):
  ll,rr=l[i:i+n],r[i:i+n]; mm=(ll+rr)/2; ss=(ll-rr)/2; hist.append({'time_s':round((i+n/2)/sr,6),'correlation':_corr(ll,rr),'mid_rms_dbfs':_db(np.sqrt(np.mean(mm*mm))),'side_rms_dbfs':_db(np.sqrt(np.mean(ss*ss)))})
 cv=[z['correlation'] for z in hist if z['correlation'] is not None]; mono=(l+r)/2; stereo_r=np.sqrt(np.mean((l*l+r*r)/2)); mono_r=np.sqrt(np.mean(mono*mono)); bands=[]
 for lo,hi in BANDS:
  nfft=8192; f=np.fft.rfftfreq(nfft,1/sr); frame_len=min(len(l),nfft); window=np.hanning(frame_len); lm=np.abs(np.fft.rfft(l[:frame_len]*window,nfft)); rm=np.abs(np.fft.rfft(r[:frame_len]*window,nfft)); q=(f>=lo)&(f<hi); bands.append({'low_hz':lo,'high_hz':hi,'mid_energy':float(np.mean(((lm[q]+rm[q])/2)**2)) if q.any() else 0.0,'side_energy':float(np.mean(((lm[q]-rm[q])/2)**2)) if q.any() else 0.0,'correlation':_corr(l[q] if len(l)==len(q) else l[:0],r[q] if len(r)==len(q) else r[:0])})
 out={'status':'stereo','channels':a.shape[1],'balance':{'left_rms_dbfs':_db(np.sqrt(np.mean(l*l))),'right_rms_dbfs':_db(np.sqrt(np.mean(r*r))),'difference_db':None if _db(np.sqrt(np.mean(l*l))) is None or _db(np.sqrt(np.mean(r*r))) is None else _db(np.sqrt(np.mean(l*l)))-_db(np.sqrt(np.mean(r*r)))},'mid_side':{'mid_rms_dbfs':_db(np.sqrt(np.mean(mid*mid))),'side_rms_dbfs':_db(np.sqrt(np.mean(side*side))),'side_to_mid_db':None if _db(np.sqrt(np.mean(side*side))) is None or _db(np.sqrt(np.mean(mid*mid))) is None else _db(np.sqrt(np.mean(side*side)))-_db(np.sqrt(np.mean(mid*mid)))},'correlation':{'overall':_corr(l,r),'minimum':min(cv) if cv else None,'maximum':max(cv) if cv else None,'mean':float(np.mean(cv)) if cv else None,'window_seconds':window_seconds,'hop_seconds':hop_seconds,'history':hist},'mono_compatibility':{'stereo_rms_dbfs':_db(stereo_r),'mono_rms_dbfs':_db(mono_r),'level_difference_db':None if _db(mono_r) is None or _db(stereo_r) is None else _db(mono_r)-_db(stereo_r)},'frequency_bands':bands,'methodology':{'correlation_definition':'Pearson correlation of windowed L/R samples','mid_side_definition':'M=(L+R)/2, S=(L-R)/2','mono_sum_definition':'(L+R)/2','timestamp_reference':'window center'}}; out['correlation']=CorrelationEvidence(out['correlation']); out.update({'width_db':out['mid_side']['side_to_mid_db'],'mid_rms':10**(out['mid_side']['mid_rms_dbfs']/20) if out['mid_side']['mid_rms_dbfs'] is not None else 0.0,'side_rms':10**(out['mid_side']['side_rms_dbfs']/20) if out['mid_side']['side_rms_dbfs'] is not None else 0.0}); return out
