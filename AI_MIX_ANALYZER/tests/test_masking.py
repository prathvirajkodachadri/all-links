import numpy as np
from analyzer.spectrum import analyze
from analyzer.masking import compare_spectral_masking

def test_masking_report():
 x=np.sin(2*np.pi*100*np.arange(8192)/44100)
 a={'spectrum':analyze(x,44100)}; b={'spectrum':analyze(x,44100)}
 r=compare_spectral_masking(a,b,44100)
 assert r['overlap_score'] >= 0
 assert 'bands' in r
