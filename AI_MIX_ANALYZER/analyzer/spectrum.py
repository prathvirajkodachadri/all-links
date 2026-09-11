import numpy as np
def analyze(x,sr,n_fft=8192):
    x=x if x.ndim==1 else x.mean(1); x=x[:n_fft]; x=np.pad(x,(0,max(0,n_fft-len(x)))); w=np.hanning(n_fft); mag=np.abs(np.fft.rfft(x*w)); f=np.fft.rfftfreq(n_fft,1/sr); p=mag/(mag.max()+1e-12)
    centroid=float((f*mag).sum()/(mag.sum()+1e-12)); spread=float(np.sqrt(((f-centroid)**2*mag).sum()/(mag.sum()+1e-12)))
    bands={'sub_bass':(20,60),'bass':(60,150),'low_mid':(150,400),'mid':(400,2000),'upper_mid':(2000,5000),'presence':(5000,8000),'high':(8000,20000)}
    energy={k:float(np.mean(mag[(f>=lo)&(f<hi)]**2)) for k,(lo,hi) in bands.items()}
    return {'frequencies_hz':f.tolist(),'magnitude':mag.tolist(),'centroid_hz':centroid,'bandwidth_hz':spread,'band_energy':energy}
