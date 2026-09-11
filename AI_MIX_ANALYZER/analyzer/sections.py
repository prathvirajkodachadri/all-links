import numpy as np

def analyze_sections(audio, window_s=10.0):
    x=audio.samples if audio.samples.ndim==1 else audio.samples.mean(axis=1); sr=audio.sample_rate; n=max(1,int(window_s*sr)); sections=[]
    for i in range(0,len(x),n):
        chunk=x[i:i+n]
        if len(chunk)<max(1,n//4): continue
        rms=float(np.sqrt(np.mean(chunk.astype(float)**2))+1e-12); peak=float(np.max(np.abs(chunk))+1e-12)
        sections.append({'start_s':round(i/sr,3),'end_s':round(min(len(x),i+n)/sr,3),'rms_dbfs':round(20*np.log10(rms),2),'crest_db':round(20*np.log10(peak/rms),2)})
    if sections:
        levels=np.array([s['rms_dbfs'] for s in sections]); med=float(np.median(levels))
        for s in sections: s['relative_to_median_db']=round(s['rms_dbfs']-med,2); s['classification']='higher-energy' if s['rms_dbfs']>med+1.5 else ('lower-energy' if s['rms_dbfs']<med-1.5 else 'typical')
    return {'window_s':window_s,'sections':sections,'dynamic_contrast_db':round(float(max([s['rms_dbfs'] for s in sections],default=0)-min([s['rms_dbfs'] for s in sections],default=0)),2)}
