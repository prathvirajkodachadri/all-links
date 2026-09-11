import numpy as np
def analyze(x,sr):
    a=x if x.ndim==1 else x.max(1); peak=float(np.max(np.abs(a))); clipped=np.where(np.abs(a)>=0.999)[0]
    dc=np.mean(x,axis=0).tolist() if x.ndim==2 else [float(np.mean(x))]; rr=float(np.sqrt(np.mean(a*a)))
    return {'sample_peak_db':float(20*np.log10(max(peak,1e-12))),'clipped_samples':int(len(clipped)),'clip_timestamps':[float(i/sr) for i in clipped[:100]],'dc_offset':dc,'rms_db':float(20*np.log10(max(rr,1e-12))),'crest_factor_db':float(20*np.log10(max(peak,1e-12)/max(rr,1e-12)))}
