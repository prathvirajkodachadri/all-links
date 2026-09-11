import numpy as np
from analyzer.spectrum import analyze
from analyzer.vocal_analysis import analyze_vocals

def test_vocal_analysis():
 x=np.sin(2*np.pi*1500*np.arange(8192)/44100)
 r={'v':{'role':'Lead Vocal','file':{'filename':'vocal'},'spectrum':analyze(x,44100)},'m':{'role':'Other','file':{'filename':'music'},'spectrum':analyze(x,44100)}}
 out=analyze_vocals(r)
 assert len(out)==1 and 'presence_energy' in out[0]
