import numpy as np
def analyze(x,sr):
    if x.ndim==1: return {'channels':1,'correlation':1.0,'width_db':0.0,'mid_rms':float(np.sqrt(np.mean(x*x))),'side_rms':0.0}
    l,r=x[:,0],x[:,1]; m=(l+r)/2; s=(l-r)/2; corr=float(np.corrcoef(l,r)[0,1]) if np.std(l)*np.std(r)>0 else 1.0
    return {'channels':x.shape[1],'left_rms':float(np.sqrt(np.mean(l*l))),'right_rms':float(np.sqrt(np.mean(r*r))),'correlation':corr,'width_db':float(20*np.log10((np.std(s)+1e-12)/(np.std(m)+1e-12))),'mid_rms':float(np.sqrt(np.mean(m*m))),'side_rms':float(np.sqrt(np.mean(s*s))),'mono_rms':float(np.sqrt(np.mean(m*m)))}
