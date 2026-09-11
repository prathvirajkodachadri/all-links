import numpy as np
from analyzer.audio_loader import AudioData
from analyzer.sections import analyze_sections

def test_sections():
 a=AudioData(np.zeros(44100*21,dtype=np.float32),44100,'test.wav')
 r=analyze_sections(a)
 assert len(r['sections'])==2
 assert r['dynamic_contrast_db']==0
