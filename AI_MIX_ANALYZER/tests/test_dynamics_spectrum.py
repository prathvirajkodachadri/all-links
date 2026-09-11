import numpy as np
from analyzer.dynamics import analyze as dyn
from analyzer.spectrum import analyze as spec

def test_known_sine_rms():
 sr=48000; x=.5*np.sin(2*np.pi*1000*np.arange(sr)/sr); r=dyn(x,sr); assert abs(r['rms']['overall_dbfs']-20*np.log10(.5/np.sqrt(2)))<.05

def test_dynamics_change():
 sr=1000; x=np.r_[np.ones(1000)*.01,np.ones(1000)*.5,np.ones(1000)*.01]; r=dyn(x,sr,window_seconds=.2,hop_seconds=.1); vals=[z['rms_dbfs'] for z in r['rms']['history']]; assert max(vals)-min(vals)>20

def test_sine_spectrum():
 sr=48000; x=np.sin(2*np.pi*1000*np.arange(8192)/sr); r=spec(x,sr); f=np.array(r['frequencies_hz']); m=np.array(r['magnitude']); assert abs(f[np.argmax(m)]-1000)<10

def test_stereo_spectrum():
 sr=48000; t=np.arange(8192)/sr; r=spec(np.c_[np.sin(2*np.pi*100*t),np.sin(2*np.pi*5000*t)],sr); assert r['overall']['centroid_hz'] is not None
