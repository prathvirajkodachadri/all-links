import numpy as np
from analyzer.spectrum import analyze
from analyzer.role_analysis import analyze_roles

def test_role_analysis():
 x=np.sin(2*np.pi*80*np.arange(8192)/44100)
 r={}
 for name,role in [('kick','Kick'),('bass','Bass')]: r[name]={'role':role,'file':{'filename':name},'spectrum':analyze(x,44100)}
 out=analyze_roles(r)
 assert any(x.get('type')=='kick_bass_relationship' for x in out)
