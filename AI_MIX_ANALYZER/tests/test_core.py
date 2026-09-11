import numpy as np
from analyzer.loudness import rms
from analyzer.stereo import analyze
def test_silence(): assert rms(np.zeros(1000))==0
def test_phase_inversion():
 x=np.sin(np.linspace(0,20,1000)); r=analyze(np.c_[x,-x],1000); assert r['correlation'] < -0.99
def test_mono(): assert analyze(np.ones(1000),1000)['channels']==1
