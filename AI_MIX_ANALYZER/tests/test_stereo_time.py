import numpy as np
from analyzer.stereo import analyze
from analyzer.time_analysis import analyze as time_analyze

def test_identical_lr():
 x=np.sin(2*np.pi*100*np.arange(1000)/1000); r=analyze(np.c_[x,x],1000); assert abs(r['correlation']['overall']-1)<1e-6

def test_inverted_lr():
 x=np.sin(2*np.pi*100*np.arange(1000)/1000); r=analyze(np.c_[x,-x],1000); assert r['correlation']['overall'] < -.99

def test_mono_status(): assert analyze(np.ones(10),1000)['status']=='mono_input'

def test_time_sections():
 r=time_analyze(np.r_[np.ones(1000)*.1,np.ones(1000)*.5],1000,1); assert len(r['sections'])==2 and r['sections'][1]['delta_from_previous']['rms_db']>10
