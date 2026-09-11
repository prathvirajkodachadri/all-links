import numpy as np
from analyzer.true_peak import true_peak

def test_silence():
 r=true_peak(np.zeros(8),sample_rate=48000); assert r['status']=='silence' and r['true_peak_dbtp'] is None

def test_stereo_channels():
 x=np.c_[np.ones(32)*.5,np.ones(32)*.25]; r=true_peak(x,sample_rate=48000)
 assert len(r['channels'])==2 and r['channels'][0]['sample_peak_dbfs'] > r['channels'][1]['sample_peak_dbfs']

def test_intersample_measurement_has_separate_fields():
 n=np.arange(4096); x=.95*np.sin(2*np.pi*997.3*n/48000)
 r=true_peak(x,8,sample_rate=48000); assert 'sample_peak_dbfs' in r and 'true_peak_dbtp' in r and r['oversampling_factor']==8

def test_factors():
 x=np.sin(2*np.pi*1000*np.arange(1000)/48000)
 for f in (4,8,16): assert true_peak(x,f,sample_rate=48000)['oversampling_factor']==f

def test_short():
 r=true_peak(np.array([.5,-.2,.1]),sample_rate=48000); assert r['status']=='ok'
