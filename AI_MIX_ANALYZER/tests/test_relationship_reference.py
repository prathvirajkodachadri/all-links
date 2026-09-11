import numpy as np
from analyzer.spectrum import analyze
from analyzer.dynamics import analyze as dyn
from analyzer.relationships import compare
from analyzer.reference import compare as refcompare

def stem(x): return {'file':{'filename':'x'},'spectrum':analyze(x,48000),'dynamics':dyn(x,48000)}
def test_separated_relationship():
 a=stem(np.sin(2*np.pi*100*np.arange(8192)/48000)); b=stem(np.sin(2*np.pi*5000*np.arange(8192)/48000)); r=compare(a,b); assert r['spectral_similarity']['value']<.5
def test_identical_reference():
 x=np.sin(2*np.pi*1000*np.arange(8192)/48000); a=stem(x); r=refcompare(a,a); assert abs(r['loudness']['difference_lu'] or 0)<1e-9 and abs(r['spectrum']['centroid_difference_hz'] or 0)<1e-9
def test_level_difference():
 a=stem(np.ones(8192)*.1); b=stem(np.ones(8192)*.2); r=compare(a,b); assert r['relative_level']['difference_db']<0
