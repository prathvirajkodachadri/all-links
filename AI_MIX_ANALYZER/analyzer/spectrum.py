"""Windowed FFT evidence. Magnitudes are reported relative to full-scale FFT energy."""
import numpy as np
BANDS=[(20,40),(40,80),(80,120),(120,250),(250,500),(500,1000),(1000,2000),(2000,4000),(4000,8000),(8000,16000),(16000,20000)]
def _db(v): return None if v<=1e-15 else float(20*np.log10(v))
def _frame(x,sr,n,hop):
 x=x[:n] if len(x)<n else x; x=np.pad(x,(0,max(0,n-len(x)))); return np.fft.rfft(x*np.hanning(n))
def analyze(x,sr,n_fft=8192,hop_seconds=.1):
 a=np.asarray(x,dtype=float); a=a[:,None] if a.ndim==1 else a; n=min(n_fft,max(1,len(a))); n=n_fft; hop=max(1,round(hop_seconds*sr)); f=np.fft.rfftfreq(n,1/sr); frames=[]
 for i in range(0,max(1,len(a)-n+1),hop): frames.append(np.mean(np.abs(np.column_stack([_frame(a[i:i+n,j],sr,n,hop) for j in range(a.shape[1])]))**2,axis=1))
 if not frames: frames=[np.zeros(len(f))]
 avg=np.mean(frames,axis=0); total=avg.sum(); centroid=float((f*avg).sum()/total) if total else None; cumulative=np.cumsum(avg); roll=float(f[np.searchsorted(cumulative,.85*total)]) if total else None; flat=float(np.exp(np.mean(np.log(avg+1e-20)))/(np.mean(avg)+1e-20)) if total else None
 bands=[]
 for lo,hi in BANDS:
  q=(f>=lo)&(f<hi); bands.append({'low_hz':lo,'high_hz':hi,'level_db':_db(np.sqrt(np.mean(avg[q]))) if q.any() else None})
 history=[]
 for k,mag in enumerate(frames[::max(1,round(.5/hop_seconds))]):
  e=mag.sum(); history.append({'time_s':round(k*.5,6),'centroid_hz':float((f*mag).sum()/e) if e else None,'bands':{f'{lo}_{hi}':_db(np.sqrt(np.mean(mag[(f>=lo)&(f<hi)]))) if np.any((f>=lo)&(f<hi)) else None for lo,hi in BANDS}})
 return {'methodology':{'fft_size':n_fft,'window':'Hann','hop_seconds':hop_seconds,'frequency_resolution_hz':sr/n_fft,'reference':'relative FFT RMS magnitude; not calibrated acoustic dB'},'frequencies_hz':f.tolist(),'magnitude':[_db(np.sqrt(v)) for v in avg],'overall':{'centroid_hz':centroid,'rolloff_hz':roll,'rolloff_percentage':.85,'flatness':flat},'frequency_bands':bands,'history':history,'band_energy':{f'{lo}_{hi}':b['level_db'] for b,(lo,hi) in zip(bands,BANDS)}}
